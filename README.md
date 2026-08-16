# pulumi-kind

Local [Kind](https://kind.sigs.k8s.io/) cluster for [pulumi-api](../pulumi-api/) and [opentofu-prometheus](../opentofu-prometheus/).

## What it provides

- Cluster `local` (context `kind-local`)
- 1 control-plane + 3 workers
- `ingress-ready=true` label on control-plane
- Host port mappings for ingress HTTP/HTTPS (80, 443)
- Kubeconfig at `./.kubeconfig`

## Prerequisites

- Docker, [kind](https://kind.sigs.k8s.io/), [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [uv](https://docs.astral.sh/uv/) and [Pulumi CLI](https://www.pulumi.com/docs/install/)

## Deploy

```bash
export PULUMI_CONFIG_PASSPHRASE=""
uv sync
pulumi stack select local    # or: pulumi stack init local
pulumi up
```

## Verify

```bash
export KUBECONFIG=./.kubeconfig
kubectl get nodes
```

## Downstream stacks

Deploy in order:

1. `pulumi-kind` (this project)
2. `opentofu-prometheus`
3. `pulumi-api`

## Cleanup

```bash
pulumi destroy
```
