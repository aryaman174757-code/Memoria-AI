# MEMORIA AI - DevOps & CI/CD Architecture

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

This document describes the DevOps and CI/CD architecture for MEMORIA AI, including infrastructure as code, continuous integration, continuous deployment, monitoring, logging, and operational practices. The architecture enables rapid, reliable, and secure delivery of features.

---

## CI/CD Pipeline Overview

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CI/CD Pipeline                                      │
│                                                                              │
│  1. Code Commit                                                             │
│         │                                                                   │
│         ▼                                                                   │
│  2. Trigger Pipeline (GitHub Actions)                                       │
│         │                                                                   │
│         ▼                                                                   │
│  3. Lint & Format Check                                                     │
│         │                                                                   │
│         ▼                                                                   │
│  4. Unit Tests                                                              │
│         │                                                                   │
│         ▼                                                                   │
│  5. Integration Tests                                                       │
│         │                                                                   │
│         ▼                                                                   │
│  6. Security Scan (SAST, SCA, Dependency Check)                             │
│         │                                                                   │
│         ▼                                                                   │
│  7. Build Docker Images                                                     │
│         │                                                                   │
│         ▼                                                                   │
│  8. Push to Container Registry                                              │
│         │                                                                   │
│         ▼                                                                   │  ┌─────────────────────┐
│  9. Deploy to Staging ──────────────────────────────────────────────────────►│  E2E Tests          │
│         │                                                                   │  └─────────────────────┘
│         ▼                                                                   │
│  10. Manual Approval (for Production)                                       │
│         │                                                                   │
│         ▼                                                                   │
│  11. Deploy to Production                                                   │
│         │                                                                   │
│         ▼                                                                   │
│  12. Smoke Tests                                                            │
│         │                                                                   │
│         ▼                                                                   │
│  13. Monitor & Alert                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## GitHub Actions Workflows

### Main CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

jobs:
  lint:
    name: Lint & Format Check
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: apps/frontend/package-lock.json
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
          cache-dependency-path: apps/backend/requirements.txt
      
      - name: Install frontend dependencies
        run: |
          cd apps/frontend
          npm ci
      
      - name: Install backend dependencies
        run: |
          cd apps/backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run ESLint
        run: |
          cd apps/frontend
          npm run lint
      
      - name: Run Prettier check
        run: |
          cd apps/frontend
          npm run format:check
      
      - name: Run Black check
        run: |
          cd apps/backend
          black --check .
      
      - name: Run Flake8
        run: |
          cd apps/backend
          flake8 .
      
      - name: Run MyPy
        run: |
          cd apps/backend
          mypy src/

  test:
    name: Test Suite
    runs-on: ubuntu-latest
    needs: lint
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: memoria_ai_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
      
      rabbitmq:
        image: rabbitmq:3-management
        env:
          RABBITMQ_DEFAULT_USER: guest
          RABBITMQ_DEFAULT_PASS: guest
        options: >-
          --health-cmd "rabbitmq-diagnostics -q ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5672:5672
          - 15672:15672
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: apps/frontend/package-lock.json
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
          cache-dependency-path: apps/backend/requirements.txt
      
      - name: Install frontend dependencies
        run: |
          cd apps/frontend
          npm ci
      
      - name: Install backend dependencies
        run: |
          cd apps/backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run frontend unit tests
        run: |
          cd apps/frontend
          npm run test:unit -- --coverage
      
      - name: Run backend unit tests
        run: |
          cd apps/backend
          pytest tests/unit/ -v --cov=src --cov-report=xml
      
      - name: Run backend integration tests
        run: |
          cd apps/backend
          pytest tests/integration/ -v
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          files: ./apps/frontend/coverage/lcov.info,./apps/backend/coverage.xml
          flags: frontend,backend
          name: codecov-umbrella

  security:
    name: Security Scanning
    runs-on: ubuntu-latest
    needs: lint
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Run Snyk security scan
        uses: snyk/actions/python@master
        continue-on-error: true
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
      
      - name: Run dependency check
        run: |
          cd apps/backend
          pip install safety
          safety check --json > safety-report.json || true
      
      - name: Run CodeQL analysis
        uses: github/codeql-action/analyze@v2
        with:
          languages: python, javascript

  build:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: [test, security]
    
    outputs:
      frontend-image: ${{ steps.build-frontend.outputs.image }}
      backend-image: ${{ steps.build-backend.outputs.image }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push frontend image
        id: build-frontend
        uses: docker/build-push-action@v5
        with:
          context: ./apps/frontend
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}
            ghcr.io/${{ github.repository }}/frontend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Build and push backend image
        id: build-backend
        uses: docker/build-push-action@v5
        with:
          context: ./apps/backend
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
            ghcr.io/${{ github.repository }}/backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### CD Pipeline

```yaml
# .github/workflows/cd.yml
name: CD Pipeline

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
          - staging
          - production

env:
  KUBECONFIG: ${{ secrets.KUBE_CONFIG }}

jobs:
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
      
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f deployments/kubernetes/staging/
          kubectl rollout status deployment/memoria-ai-backend -n staging
          kubectl rollout status deployment/memoria-ai-frontend -n staging
      
      - name: Run smoke tests
        run: |
          cd tests/e2e
          npm ci
          npm run test:staging

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment: production
    needs: deploy-staging
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_PRODUCTION }}
      
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f deployments/kubernetes/production/
          kubectl rollout status deployment/memoria-ai-backend -n production
          kubectl rollout status deployment/memoria-ai-frontend -n production
      
      - name: Run smoke tests
        run: |
          cd tests/e2e
          npm ci
          npm run test:production
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment completed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Docker Configuration

### Frontend Dockerfile

```dockerfile
# apps/frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
```

### Backend Dockerfile

```dockerfile
# apps/backend/Dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app .

RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: memoria-postgres
    environment:
      POSTGRES_USER: memoria
      POSTGRES_PASSWORD: memoria
      POSTGRES_DB: memoria_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U memoria"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: memoria-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: memoria-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: memoria
      RABBITMQ_DEFAULT_PASS: memoria
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
    container_name: memoria-backend
    environment:
      DATABASE_URL: postgresql+asyncpg://memoria:memoria@postgres:5432/memoria_ai
      REDIS_URL: redis://redis:6379/0
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      RABBITMQ_USER: memoria
      RABBITMQ_PASSWORD: memoria
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    volumes:
      - ./apps/backend:/app
      - backend_uploads:/app/uploads

  frontend:
    build:
      context: ./apps/frontend
      dockerfile: Dockerfile
    container_name: memoria-frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    container_name: memoria-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployments/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deployments/nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
  backend_uploads:
```

---

## Kubernetes Configuration

### Namespace Configuration

```yaml
# deployments/kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: memoria-ai
  labels:
    name: memoria-ai
    environment: production
```

### ConfigMap

```yaml
# deployments/kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: memoria-config
  namespace: memoria-ai
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  MAX_WORKERS: "4"
  REDIS_MAX_CONNECTIONS: "50"
  DATABASE_POOL_SIZE: "20"
```

### Secret

```yaml
# deployments/kubernetes/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: memoria-secrets
  namespace: memoria-ai
type: Opaque
stringData:
  database-url: "postgresql+asyncpg://user:password@postgres:5432/memoria_ai"
  redis-url: "redis://redis:6379/0"
  secret-key: "your-secret-key"
  openai-api-key: "sk-..."
  jwt-secret: "your-jwt-secret"
```

### Backend Deployment

```yaml
# deployments/kubernetes/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memoria-backend
  namespace: memoria-ai
  labels:
    app: memoria-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: memoria-backend
  template:
    metadata:
      labels:
        app: memoria-backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/memoria-ai/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: memoria-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: memoria-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: memoria-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Backend Service

```yaml
# deployments/kubernetes/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: memoria-backend
  namespace: memoria-ai
spec:
  selector:
    app: memoria-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Horizontal Pod Autoscaler

```yaml
# deployments/kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: memoria-backend-hpa
  namespace: memoria-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: memoria-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Ingress

```yaml
# deployments/kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: memoria-ingress
  namespace: memoria-ai
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.memoria.ai
    secretName: memoria-tls
  rules:
  - host: api.memoria.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: memoria-backend
            port:
              number: 8000
```

---

## Infrastructure as Code

### Terraform Configuration

```hcl
# deployments/terraform/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
  }
  
  backend "s3" {
    bucket         = "memoria-ai-terraform-state"
    key            = "infrastructure/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "memoria-ai-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}
```

### EKS Module

```hcl
# deployments/terraform/modules/eks.tf
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.27"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  eks_managed_node_groups = {
    general = {
      instance_types = ["t3.large", "t3a.large"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 3
      max_size     = 10
      desired_size = 3

      labels = {
        Environment = "production"
        NodeGroup   = "general"
      }
    }

    memory_optimized = {
      instance_types = ["r6g.large", "r6a.large"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 2
      max_size     = 5
      desired_size = 2

      labels = {
        Environment = "production"
        NodeGroup   = "memory-optimized"
      }
    }
  }

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
```

### RDS Module

```hcl
# deployments/terraform/modules/rds.tf
module "database" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "memoria-ai-db"

  engine               = "postgres"
  engine_version       = "15.4"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = "db.r6g.xlarge"

  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true

  db_name  = "memoria_ai"
  username = var.db_username
  password = var.db_password

  port = 5432

  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.rds_sg_id]

  maintenance_window = "Mon:00:00-Mon:03:00"
  backup_window      = "03:00-06:00"

  backup_retention_period = 30
  skip_final_snapshot    = false

  performance_insight_enabled = true
  monitoring_interval       = 60

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}
```

---

## Monitoring & Logging

### Prometheus Configuration

```yaml
# deployments/monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "MEMORIA AI - Application Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx Errors"
          }
        ]
      },
      {
        "title": "Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)",
            "legendFormat": "95th Percentile"
          }
        ]
      },
      {
        "title": "Database Connections",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "{{datname}}"
          }
        ]
      }
    ]
  }
}
```

### Loki Configuration

```yaml
# deployments/monitoring/loki-config.yml
server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h
      chunks:
        prefix: chunks_
        period: 168h

storage_config:
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 168h
```

---

## Logging Strategy

### Structured Logging

```python
# core/logging/logger.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # Add exception if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging(config: Config):
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler (in production)
    if config.ENVIRONMENT == "production":
        file_handler = logging.FileHandler('/var/log/memoria-ai/app.log')
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
```

### Logging Middleware

```python
# core/logging/middleware.py
from fastapi import Request
import uuid
import time

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            "Incoming request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )
        
        # Measure time
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log response
            duration = time.time() - start_time
            logger.info(
                "Request completed",
                request_id=request_id,
                status_code=response.status_code,
                duration=duration
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                request_id=request_id,
                error=str(e),
                duration=duration
            )
            raise
```

---

## Monitoring Metrics

### Application Metrics

```python
# core/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client.fastapi import metrics

# HTTP metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress',
    ['method', 'endpoint']
)

# Database metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

db_connections_idle = Gauge(
    'db_connections_idle',
    'Idle database connections'
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# AI metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI requests',
    ['provider', 'model']
)

ai_request_duration_seconds = Histogram(
    'ai_request_duration_seconds',
    'AI request duration',
    ['provider', 'model']
)

ai_tokens_total = Counter(
    'ai_tokens_total',
    'Total AI tokens used',
    ['provider', 'model', 'token_type']
)

# Application info
app_info = Info(
    'app_info',
    'Application information'
)
```

---

## Alerting

### Alert Rules

```yaml
# deployments/monitoring/alerts.yml
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} for the last 5 minutes"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "95th percentile latency is {{ $value }}s"
      
      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"
      
      - alert: DatabaseConnectionPoolExhausted
        expr: db_connections_active / db_connections_idle > 0.9
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Active connections: {{ $value }}"
      
      - alert: AIRequestFailure
        expr: rate(ai_requests_total{status="failed"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High AI request failure rate"
          description: "AI request failure rate is {{ $value }}"
```

---

## Backup Strategy

### Database Backup

```bash
# scripts/backup-database.sh
#!/bin/bash

# Configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-memoria_ai}"
DB_USER="${DB_USER:-memoria}"
S3_BUCKET="${S3_BUCKET:-memoria-ai-backups}"
BACKUP_RETENTION_DAYS=30

# Create backup filename
BACKUP_FILE="memoria_ai_$(date +%Y%m%d_%H%M%S).sql.gz"
BACKUP_PATH="/tmp/${BACKUP_FILE}"

# Perform backup
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME | gzip > $BACKUP_PATH

# Upload to S3
aws s3 cp $BACKUP_PATH s3://${S3_BUCKET}/database/${BACKUP_FILE}

# Clean up old backups
aws s3 ls s3://${S3_BUCKET}/database/ | while read -r line; do
    backup_date=$(echo $line | awk '{print $1}' | awk -F'/' '{print $NF}' | grep -oP '\d{8}')
    if [ -n "$backup_date" ]; then
        backup_sec=$(date -d "${backup_date}" +%s)
        current_sec=$(date +%s)
        diff_sec=$((current_sec - backup_sec))
        diff_days=$((diff_sec / 86400))
        
        if [ $diff_days -gt $BACKUP_RETENTION_DAYS ]; then
            backup_file=$(echo $line | awk '{print $NF}')
            aws s3 rm "s3://${S3_BUCKET}/database/${backup_file}"
        fi
    fi
done

# Clean up local file
rm $BACKUP_PATH

echo "Backup completed: ${BACKUP_FILE}"
```

---

## Disaster Recovery

### Disaster Recovery Plan

```yaml
# deployments/disaster-recovery/plan.yml
disaster_recovery:
  rto: 4 hours  # Recovery Time Objective
  rpo: 1 hour   # Recovery Point Objective
  
  backup_strategy:
    database:
      - type: automated
        frequency: hourly
        retention: 30 days
        location: s3
      
      - type: snapshot
        frequency: daily
        retention: 90 days
        location: aws_rds_snapshot
    
    files:
      - type: automated
        frequency: daily
        retention: 90 days
        location: s3
  
  recovery_procedures:
    database:
      - step: "Stop application"
        command: "kubectl scale deployment memoria-backend --replicas=0"
      
      - step: "Restore from latest backup"
        command: "aws s3 cp s3://memoria-ai-backups/database/latest.sql.gz - | gunzip | psql"
      
      - step: "Verify data integrity"
        command: "python scripts/verify_data.py"
      
      - step: "Start application"
        command: "kubectl scale deployment memoria-backend --replicas=3"
      
      - step: "Run smoke tests"
        command: "npm run test:smoke"
    
    application:
      - step: "Rollback to previous version"
        command: "helm rollback memoria-ai"
      
      - step: "Verify health"
        command: "kubectl rollout status deployment/memoria-backend"
```

---

## Best Practices

### 1. CI/CD
- Use feature branches for development
- Require code reviews before merging
- Run tests on every commit
- Use semantic versioning
- Automate deployments

### 2. Infrastructure
- Use infrastructure as code
- Version control all configurations
- Use immutable infrastructure
- Implement blue-green deployments
- Use canary releases for critical changes

### 3. Monitoring
- Monitor all layers of the stack
- Set up appropriate alerts
- Use structured logging
- Centralize logs
- Review metrics regularly

### 4. Security
- Scan for vulnerabilities regularly
- Use secrets management
- Implement network policies
- Regular security audits
- Keep dependencies updated

### 5. Performance
- Use horizontal scaling
- Implement caching
- Optimize database queries
- Use CDN for static assets
- Monitor resource usage

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** DevOps Team
