import pulumi
import pulumi_command as command
import os

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
    # if it was created outside of Pulumi or in a previous run that didn't track it correctly.
    # However, Pulumi state usually handles this. For robustness:
    triggers=[pulumi.Output.from_input(config_path).apply(lambda p: os.path.getmtime(p) if os.path.exists(p) else 0)]
)

# Export the cluster name
pulumi.export("cluster_name", cluster_name)
pulumi.export("kubeconfig", f"~/.kube/config")
