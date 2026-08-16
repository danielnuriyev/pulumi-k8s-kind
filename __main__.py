import os

import pulumi
import pulumi_command as command

config_path = os.path.abspath("kind-config.yaml")
kubeconfig_path = os.path.abspath(".kubeconfig")
cluster_name = "local"

kind_cluster = command.local.Command(
    "kind-cluster",
    create=f"""set -euo pipefail
if ! kind get clusters 2>/dev/null | grep -qx "{cluster_name}"; then
  kind create cluster --name {cluster_name} --config {config_path} --wait 120s
fi
kind export kubeconfig --name {cluster_name} --kubeconfig {kubeconfig_path}
""",
    delete=f"kind delete cluster --name {cluster_name}",
    triggers=[
        pulumi.Output.from_input(config_path).apply(
            lambda p: os.path.getmtime(p) if os.path.exists(p) else 0
        )
    ],
)

pulumi.export("cluster_name", cluster_name)
pulumi.export("kubeconfig", kubeconfig_path)
pulumi.export("context", f"kind-{cluster_name}")
