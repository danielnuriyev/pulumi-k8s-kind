# Quick Start Guide

This guide will help you quickly get started with creating a local Kubernetes cluster using kind, managed by Pulumi with Python and uv.

## Prerequisites Installation

### 1. Install uv (Python package manager)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv
```

### 2. Install Pulumi
```bash
# macOS
brew install pulumi

# Linux
curl -fsSL https://get.pulumi.com | sh

# Windows
choco install pulumi
```

### 3. Install kind
```bash
# macOS
brew install kind

# Linux
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Windows
choco install kind
```

### 4. Install Docker
Visit [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/) for installation instructions.

## Usage

### Basic Setup (5 minutes)

1. **Clone and setup:**
   ```bash
   git clone https://github.com/danielnuriyev/pulumi-k8s-kind.git
   cd pulumi-k8s-kind
   uv sync
   ```

2. **Configure Pulumi backend:**
   ```bash
   pulumi login --local  # Use local file-based backend
   # or
   pulumi login          # Use Pulumi Cloud
   ```

3. **Create and deploy cluster:**
   ```bash
   export PULUMI_CONFIG_PASSPHRASE=""  # For local backend
   pulumi stack init dev
   pulumi up --yes
   ```

4. **Use the cluster:**
   ```bash
   kubectl config use-context kind-kind-cluster
   kubectl get nodes
   ```

### Custom Configuration

Configure your cluster before deployment:

```bash
# Set custom cluster name
pulumi config set clusterName my-custom-cluster

# Set custom Kubernetes version
pulumi config set nodeImage kindest/node:v1.29.0

# Deploy with custom configuration
pulumi up
```

### Cleanup

```bash
# Destroy the cluster
pulumi destroy --yes

# Remove the stack
pulumi stack rm dev
```

## Common Commands

```bash
# View current stack outputs
pulumi stack output

# View cluster kubeconfig
pulumi stack output kubeconfig

# View all resources
pulumi stack --show-urns

# Preview changes before applying
pulumi preview
```

## Troubleshooting

### Issue: "kind: command not found"
**Solution:** Install kind following the prerequisites section.

### Issue: "Cannot connect to Docker daemon"
**Solution:** Ensure Docker is running: `docker ps`

### Issue: "Port already in use"
**Solution:** Delete existing kind cluster: `kind delete cluster --name <cluster-name>`

### Issue: Missing Pulumi plugins
**Solution:** Install required plugins:
```bash
pulumi plugin install resource command v1.1.3
pulumi plugin install resource kubernetes v4.25.0
```

## Next Steps

- Add applications to your cluster using `kubectl`
- Extend `__main__.py` to deploy Kubernetes resources
- Use `pulumi-kubernetes` provider to manage k8s resources as code
- Explore Pulumi examples: [https://github.com/pulumi/examples](https://github.com/pulumi/examples)

## Resources

- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [kind Documentation](https://kind.sigs.k8s.io/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
