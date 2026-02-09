"""A Pulumi program to create a local Kubernetes cluster using kind."""
import pulumi
import pulumi_command as command

# Configuration
config = pulumi.Config()
cluster_name = config.get("clusterName") or "kind-cluster"
node_image = config.get("nodeImage") or "kindest/node:v1.27.3"

# Create kind cluster
create_cluster = command.local.Command(
    "create-kind-cluster",
    create=f"kind create cluster --name {cluster_name} --image {node_image}",
    delete=f"kind delete cluster --name {cluster_name}",
    opts=pulumi.ResourceOptions(
        custom_timeouts=pulumi.CustomTimeouts(create="10m", delete="5m")
    ),
)

# Get kubeconfig
get_kubeconfig = command.local.Command(
    "get-kubeconfig",
    create=f"kind get kubeconfig --name {cluster_name}",
    opts=pulumi.ResourceOptions(depends_on=[create_cluster]),
)

# Export the cluster name and kubeconfig
pulumi.export("clusterName", cluster_name)
pulumi.export("kubeconfig", get_kubeconfig.stdout)
pulumi.export("message", "Run 'kubectl config use-context kind-{cluster_name}' to use this cluster")
