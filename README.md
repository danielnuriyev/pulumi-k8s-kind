# pulumi-k8s-kind

Creates a local Kubernetes cluster using [kind](https://kind.sigs.k8s.io/) managed by [Pulumi](https://www.pulumi.com/) with Python and [uv](https://github.com/astral-sh/uv) to be used for my other local deployments: Trino, Snowflake Emulator, Spark, Dagster.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Docker**: Required by kind to run cluster nodes as containers.
    - [Install Docker Desktop](https://docs.docker.com/get-docker/) or Docker Engine.
2.  **kind**: The Kubernetes-in-Docker tool.
    - `brew install kind` (macOS) or follow [kind installation guide](https://kind.sigs.k8s.io/docs/user/quick-start/#installation).
3.  **uv**: A fast Python package manager and workflow tool.
    - `curl -LsSf https://astral-sh/uv/install.sh | sh` or `brew install uv`.
4.  **Pulumi CLI**: To manage the infrastructure.
    - `brew install pulumi` or follow [Pulumi installation guide](https://www.pulumi.com/docs/get-started/install/).
5.  **kubectl**: To interact with the cluster.
    - `brew install kubectl`.

## Project Structure

- `kind-config.yaml`: Configuration for the kind cluster, including multi-node setup and port mappings for various services (Minio, Trino, etc.).
- `__main__.py`: Pulumi program that uses the `pulumi-command` provider to create/delete the kind cluster.
- `Pulumi.yaml`: Project metadata, configured to use `uv` as the Python toolchain.
- `pyproject.toml`: Python project dependencies managed by `uv`.

## Deployment Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pulumi-k8s-kind
```

### 2. Install Dependencies

Use `uv` to install the required Python packages:

```bash
uv sync
```

### 3. Initialize Pulumi Stack

If you haven't already, create a new Pulumi stack (e.g., `dev`):

```bash
pulumi stack init dev
```

### 4. Deploy the Cluster

Run the following command to create the kind cluster:

```bash
pulumi up
```

This will:
- Read `kind-config.yaml`.
- Execute `kind create cluster --name local --config kind-config.yaml`.
- Set up the kubeconfig to point to the new cluster.

### 5. Verify the Cluster

Once the deployment is complete, verify that the nodes are running:

```bash
kubectl get nodes
```

You should see one control-plane node and several worker nodes as defined in `kind-config.yaml`.

## Port Mappings

The cluster is configured to expose the following services to your localhost:

| Service | Host Port | Container Port |
| :--- | :--- | :--- |
| Minio Console | 9001 | 9001 |
| Minio API | 9000 | 9000 |
| Nessie | 19120 | 19120 |
| Trino | 8080 | 8080 |
| Snowflake Emulator | 8081 | 8081 |
| Dagster | 3000, 4000, 4266 | 3000, 4000, 4266 |
| Windmill | 8082, 8443, 8001 | 80, 443, 8000 |
| Ingress (HTTP/S) | 80, 443 | 80, 443 |

## Cleanup

To delete the cluster and clean up resources:

```bash
pulumi destroy
```
