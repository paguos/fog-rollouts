# Fog Rollouts

A Kubernetes operator for experimental deployment of applications in fog computing environments, enabling seamless rollouts across cloud, fog, and edge layers.

## 🌟 Overview

Fog Rollouts is a Python-based Kubernetes operator that orchestrates application deployments across multiple computing layers in fog environments. It provides automated synchronization and management of applications between cloud, fog, and edge infrastructures using custom Kubernetes resources.

### Key Features

- **Multi-layer Deployment**: Deploy applications across cloud, fog, and edge layers
- **Automatic Synchronization**: Keeps deployments synchronized across different layers
- **Custom Resource Definitions**: Uses Kubernetes CRDs for declarative fog rollout management
- **RESTful API**: FastAPI-based service for rollout management
- **Version Management**: Tracks and manages application versions across layers
- **Kubernetes Native**: Built on Kubernetes using kopf (Kubernetes Operator Pythonic Framework)

## 🏗️ Architecture

The system operates on a hierarchical fog computing model:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Cloud    │───▶│     Fog     │───▶│    Edge     │
│  (Central)  │    │ (Regional)  │    │  (Local)    │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Components

- **FogRollout CRD**: Custom Kubernetes resource defining multi-layer deployments
- **Watcher**: Python service that synchronizes rollouts between layers
- **API Server**: FastAPI service providing REST endpoints for rollout management
- **Helm Chart**: Kubernetes deployment configuration

## 📋 Requirements

### Prerequisites

- [Docker](https://www.docker.com/get-started) - Container platform
- [Helm](http://helm.sh) - Kubernetes package manager  
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) - Kubernetes management tool
- [k3d](https://github.com/rancher/k3d) - Containerized k3s Kubernetes distribution
- [pipenv](https://pipenv.pypa.io/en/latest/) - Python dependency manager

### Python Dependencies

- **kopf**: Kubernetes operator framework
- **fastapi**: Modern web framework for APIs
- **uvicorn**: ASGI server
- **pykube-ng**: Kubernetes client library
- **loguru**: Advanced logging
- **requests**: HTTP library

## 🚀 Quick Start

### 1. Initialize Kubernetes Cluster

Create a local k3d cluster:

```bash
k3d create --image rancher/k3s:v1.18.2-k3s1
```

Configure kubectl:

```bash
export KUBECONFIG="$(k3d get-kubeconfig --name='k3s-default')"
```

### 2. Deploy Fog Rollouts

Use the Makefile to build and deploy:

```bash
make run
```

This command will:
- Build the Docker image
- Import it into k3d
- Deploy using Helm across cloud, fog, and edge namespaces

### 3. Deploy Example Application

Deploy the nginx example rollout:

```bash
kubectl apply -f examples/nginx-rollout.yml -n cloud
```

### 4. Verify Deployment

Check rollouts across all namespaces:

```bash
kubectl get fog-rollouts --all-namespaces
kubectl get pods --all-namespaces
```

## 📖 Usage

### Creating a FogRollout

Define a FogRollout resource:

```yaml
apiVersion: paguos.io/v1alpha1
kind: FogRollout
metadata:
  name: my-app-rollout
spec:
  version: v1.0.0
  deployments:
    cloud:
      replicas: 3
      containers:
        - name: my-app
          image: my-app:v1.0.0
          ports:
            - containerPort: 8080
    fog:
      replicas: 2
      containers:
        - name: my-app
          image: my-app:v1.0.0
          ports:
            - containerPort: 8080
    edge:
      replicas: 1
      containers:
        - name: my-app
          image: my-app:v1.0.0
          ports:
            - containerPort: 8080
```

### API Endpoints

The system provides REST API endpoints:

- **GET /rollouts**: List all rollouts in a namespace
- **GET /rollouts/{rollout_name}**: Get specific rollout details

Example API usage:

```bash
# List rollouts in default namespace
curl http://fog-rollouts-api.cloud/rollouts

# Get specific rollout
curl http://fog-rollouts-api.cloud/rollouts/nginx-rollout
```

## 🔧 Development

### Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd fog-rollouts
```

2. Install dependencies:
```bash
pipenv install --dev
pipenv shell
```

3. Run linting:
```bash
flake8 fog-rollouts/
```

4. Auto-format code:
```bash
autopep8 --in-place --recursive fog-rollouts/
```

### Project Structure

```
fog-rollouts/
├── fog-rollouts/          # Main application code
│   ├── api.py            # FastAPI REST endpoints
│   ├── clients.py        # Kubernetes and API clients
│   ├── handlers.py       # Kopf event handlers
│   ├── models.py         # Data models and CRD definitions
│   └── watcher.py        # Main synchronization logic
├── chart/                # Helm chart for deployment
│   ├── crds/            # Custom Resource Definitions
│   ├── templates/       # Kubernetes manifests
│   ├── Chart.yaml       # Chart metadata
│   └── values.yaml      # Default configuration
├── examples/            # Example rollout configurations
├── Dockerfile          # Container build configuration
├── Makefile           # Build and deployment automation
├── Pipfile            # Python dependencies
└── Pipfile.lock       # Locked dependency versions
```

### Building and Testing

Build the Docker image:
```bash
make build
```

Import to k3d:
```bash
make k3d/import
```

Deploy with Helm:
```bash
make helm
```

Clean up deployment:
```bash
make clean
```

## 🐳 Docker

The application is containerized using a Python 3.8 slim base image. The Dockerfile:

- Uses `python:3.8-slim-buster` as base
- Installs pipenv for dependency management
- Sets up the application in `/fog-rollouts` directory
- Configures the watcher as the default command

## ☸️ Kubernetes Integration

### Custom Resource Definition

The system extends Kubernetes with a custom `FogRollout` resource that defines:

- Application version tracking
- Multi-layer deployment specifications
- Container configurations per layer
- Readiness and health check configurations

### Operator Pattern

Built using the kopf framework, the operator:

- Watches for FogRollout resource changes
- Synchronizes state across layers
- Handles create, update, and delete operations
- Maintains desired state reconciliation

## 🔒 Security Considerations

- Uses Kubernetes RBAC for access control
- Service-to-service communication within cluster
- Environment-based configuration for sensitive data
- Namespace isolation between layers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 conventions
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Maintain test coverage

## 📝 License

This project is licensed under the terms specified in the repository.

## 🚨 Known Issues

- Designed for Linux and macOS environments
- Requires specific k3s version (v1.18.2-k3s1)
- Currently in experimental stage

## 📞 Support

For questions, issues, or contributions, please use the GitHub issue tracker.

---

**Note**: This project is experimental and designed for fog computing research and development. Use in production environments should be carefully evaluated.

