import os

import pulumi
import pulumi_command as command
import pulumi_aws as aws
from pulumi_aws import ec2, eks, iam

config = pulumi.Config()
cluster_type = config.get("cluster_type") or "kind"  # "kind" or "eks"

aws_region = config.get("aws_region") or "us-east-1"
eks_cluster_name = config.get("eks_cluster_name") or "pulumi-k8s-kind-eks"
node_group_desired_capacity = int(config.get("node_group_desired_capacity") or "2")
node_group_instance_type = config.get("node_group_instance_type") or "t3.medium"

if cluster_type == "kind":
    # Get the absolute path to the kind-config.yaml
    config_path = os.path.abspath("kind-config.yaml")
    cluster_name = "local"

    # Create the kind cluster using the command provider
    # We use 'kind create cluster' and 'kind delete cluster'
    kind_cluster = command.local.Command(
        "kind-cluster",
        create=f"kind create cluster --name {cluster_name} --config {config_path}",
        delete=f"kind delete cluster --name {cluster_name}",
        # Check if the cluster already exists to avoid errors on 'pulumi up'
        triggers=[
            pulumi.Output.from_input(config_path).apply(
                lambda p: os.path.getmtime(p) if os.path.exists(p) else 0
            )
        ],
    )

    pulumi.export("cluster_type", "kind")
    pulumi.export("cluster_name", cluster_name)
    pulumi.export("kubeconfig", "~/.kube/config")
else:
    # Create IAM role for EKS cluster
    cluster_role = iam.Role(
        "eks-cluster-role",
        assume_role_policy="""{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "eks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }""",
    )

    cluster_policy_attachment = iam.RolePolicyAttachment(
        "eks-cluster-policy",
        role=cluster_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
    )

    cluster_service_policy_attachment = iam.RolePolicyAttachment(
        "eks-cluster-service-policy",
        role=cluster_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEKSServicePolicy",
    )

    # Create IAM role for EKS node group
    node_role = iam.Role(
        "eks-node-role",
        assume_role_policy="""{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }""",
    )

    node_policy_attachment = iam.RolePolicyAttachment(
        "eks-node-policy",
        role=node_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    )

    node_cni_policy_attachment = iam.RolePolicyAttachment(
        "eks-node-cni-policy",
        role=node_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    )

    node_registry_policy_attachment = iam.RolePolicyAttachment(
        "eks-node-registry-policy",
        role=node_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    )

    # Create VPC and subnets for EKS
    vpc = ec2.Vpc(
        "eks-vpc",
        cidr_block="10.0.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
    )

    subnet1 = ec2.Subnet(
        "eks-subnet-1",
        vpc_id=vpc.id,
        cidr_block="10.0.1.0/24",
        availability_zone=pulumi.Output.concat(aws_region, "a"),
        tags={"Name": "eks-subnet-1"},
    )

    subnet2 = ec2.Subnet(
        "eks-subnet-2",
        vpc_id=vpc.id,
        cidr_block="10.0.2.0/24",
        availability_zone=pulumi.Output.concat(aws_region, "b"),
        tags={"Name": "eks-subnet-2"},
    )

    igw = ec2.InternetGateway(
        "eks-igw",
        vpc_id=vpc.id,
    )

    route_table = ec2.RouteTable(
        "eks-route-table",
        vpc_id=vpc.id,
        routes=[
            ec2.RouteTableRouteArgs(
                cidr_block="0.0.0.0/0",
                gateway_id=igw.id,
            )
        ],
    )

    route_table_assoc1 = ec2.RouteTableAssociation(
        "eks-route-table-assoc-1",
        subnet_id=subnet1.id,
        route_table_id=route_table.id,
    )

    route_table_assoc2 = ec2.RouteTableAssociation(
        "eks-route-table-assoc-2",
        subnet_id=subnet2.id,
        route_table_id=route_table.id,
    )

    cluster_security_group = ec2.SecurityGroup(
        "eks-cluster-sg",
        vpc_id=vpc.id,
        description="Security group for EKS cluster",
        ingress=[
            ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=443,
                to_port=443,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
        egress=[
            ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
    )

    eks_cluster = eks.Cluster(
        eks_cluster_name,
        version="1.28",
        role_arn=cluster_role.arn,
        vpc_config=eks.ClusterVpcConfigArgs(
            subnet_ids=[subnet1.id, subnet2.id],
            security_group_ids=[cluster_security_group.id],
        ),
        opts=pulumi.ResourceOptions(
            depends_on=[
                cluster_policy_attachment,
                cluster_service_policy_attachment,
            ]
        ),
    )

    node_group = eks.NodeGroup(
        "eks-node-group",
        cluster_name=eks_cluster.name,
        node_role_arn=node_role.arn,
        subnet_ids=[subnet1.id, subnet2.id],
        scaling_config=eks.NodeGroupScalingConfigArgs(
            desired_size=node_group_desired_capacity,
            max_size=node_group_desired_capacity + 2,
            min_size=1,
        ),
        instance_types=[node_group_instance_type],
        opts=pulumi.ResourceOptions(
            depends_on=[
                node_policy_attachment,
                node_cni_policy_attachment,
                node_registry_policy_attachment,
            ]
        ),
    )

    kubeconfig = pulumi.Output.all(
        eks_cluster.certificate_authority.data,
        eks_cluster.endpoint,
        eks_cluster.name,
    ).apply(
        lambda args: {
            "apiVersion": "v1",
            "clusters": [
                {
                    "cluster": {
                        "certificate-authority-data": args[0],
                        "server": args[1],
                    },
                    "name": "kubernetes",
                }
            ],
            "contexts": [
                {
                    "context": {"cluster": "kubernetes", "user": "aws"},
                    "name": "aws",
                }
            ],
            "current-context": "aws",
            "kind": "Config",
            "preferences": {},
            "users": [
                {
                    "name": "aws",
                    "user": {
                        "exec": {
                            "apiVersion": "client.authentication.k8s.io/v1beta1",
                            "command": "aws",
                            "args": [
                                "eks",
                                "get-token",
                                "--cluster-name",
                                args[2],
                                "--region",
                                aws_region,
                            ],
                        }
                    },
                }
            ],
        }
    )

    pulumi.export("cluster_type", "eks")
    pulumi.export("cluster_name", eks_cluster.name)
    pulumi.export("cluster_endpoint", eks_cluster.endpoint)
    pulumi.export("kubeconfig", kubeconfig)
