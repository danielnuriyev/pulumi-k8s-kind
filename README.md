# pulumi-k8s-kind

Creates a local Kubernetes cluster using kind, managed with Pulumi and Python with uv.

## Prerequisites

- [Pulumi](https://www.pulumi.com/docs/get-started/install/)
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker](https://docs.docker.com/get-docker/) (required by kind)
- Python 3.8 or later

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/danielnuriyev/pulumi-k8s-kind.git
   cd pulumi-k8s-kind
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

3. **Initialize Pulumi stack:**
   ```bash
   pulumi login --local  # Use local backend
   pulumi stack init dev
   ```

4. **Configure the cluster (optional):**
   ```bash
   pulumi config set clusterName my-kind-cluster
   pulumi config set nodeImage kindest/node:v1.27.3
   ```

5. **Deploy the cluster:**
   ```bash
   pulumi up
   ```

6. **Use the cluster:**
   ```bash
   kubectl config use-context kind-<cluster-name>
   kubectl get nodes
   ```

7. **Destroy the cluster:**
   ```bash
   pulumi destroy
   ```

## Configuration

| Config Key | Default Value | Description |
|------------|---------------|-------------|
| `clusterName` | `kind-cluster` | Name of the kind cluster |
| `nodeImage` | `kindest/node:v1.27.3` | Docker image for kind nodes |

## Features

- Creates a local Kubernetes cluster using kind
- Manages cluster lifecycle with Pulumi
- Uses uv for fast and reliable Python dependency management
- Exports kubeconfig for easy cluster access

## Project Structure

```
.
├── Pulumi.yaml          # Pulumi project configuration
├── pyproject.toml       # Python project and dependencies (uv)
├── __main__.py          # Pulumi program
└── README.md            # This file
```
