# MEMORIA AI - Deployment Architecture

## Version: 1.0
## Date: June 13, 2026
## Status: Final

---

## Executive Summary

This document describes the deployment architecture for MEMORIA AI, including deployment strategies, environment configurations, scaling approaches, and deployment targets. The architecture supports multiple deployment options including cloud providers (AWS, GCP, Azure), PaaS platforms (Vercel, Render), and self-hosted options.

---

## Deployment Targets

### Supported Deployment Options

| Platform | Type | Use Case | Status |
|----------|------|----------|--------|
| AWS EKS | Cloud | Production, Enterprise | Primary |
| GCP GKE | Cloud | Production, Enterprise | Supported |
| Azure AKS | Cloud | Production, Enterprise | Supported |
| Vercel | PaaS | Frontend, Staging | Supported |
| Render | PaaS | Full Stack, MVP | Supported |
| Self-Hosted | On-Premise | Enterprise, Compliance | Supported |
| Docker Compose | Local | Development | Primary |

---

## Environment Strategy

### Environment Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Environment Hierarchy                                │
│                                                                              │
│  Development ────────────────────────────────────────────────────────────────│
│       │                                                                       │
│       ├── Local Development (Docker Compose)                                  │
│       │   - Hot reload enabled                                               │
│       │   - Debug mode                                                      │
│       │   - Local services                                                   │
│       │                                                                       │
│       └── Development Cloud (AWS/GCP)                                         │
│           - Shared environment                                                │
│           - Integration testing                                               │
│           - Feature flags enabled                                            │
│                                                                              │
│  Staging ─────────────────────────────────────────────────────────────────────│
│       │                                                                       │
│       ├── Production-like configuration                                       │
│       ├── Real data (anonymized)                                              │
│       ├── Full monitoring                                                    │
│       └── Pre-production testing                                             │
│                                                                              │
│  Production ──────────────────────────────────────────────────────────────────│
│       │                                                                       │
│       ├── High availability                                                   │
│       ├── Auto-scaling                                                       │
│       ├── CDN enabled                                                        │
│       ├── Full monitoring & alerting                                          │
│       └── Disaster recovery enabled                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## AWS Deployment

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS Production Architecture                           │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                           Route 53                                   │   │
│  │  - DNS Management                                                     │   │
│  │  - SSL Certificates (ACM)                                             │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                           CloudFront CDN                               │   │
│  │  - Static assets                                                      │   │
│  │  - API caching                                                         │   │
│  │  - DDoS protection                                                     │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                                    ▼                                          │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                           Application Load Balancer                    │   │
│  │  - SSL termination                                                     │   │
│  │  - Health checks                                                        │   │
│  │  - Cross-zone load balancing                                           │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                    │                                          │
│                    ┌───────────────┼───────────────┐                          │
│                    ▼               ▼               ▼                          │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐   │
│  │   EKS Cluster       │  │   EKS Cluster       │  │   EKS Cluster       │   │
│  │   (us-east-1a)      │  │   (us-east-1b)      │  │   (us-east-1c)      │   │
│  │                     │  │                     │  │                     │   │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │   │
│  │  │ Frontend Pods │  │  │  │ Frontend Pods │  │  │  │ Frontend Pods │  │   │
│  │  └───────────────┘  │  │  └───────────────┘  │  │  └───────────────┘  │   │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │   │
│  │  │ Backend Pods  │  │  │  │ Backend Pods  │  │  │  │ Backend Pods  │  │   │
│  │  └───────────────┘  │  │  └───────────────┘  │  │  └───────────────┘  │   │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │   │
│  │  │ Worker Pods   │  │  │  │ Worker Pods   │  │  │  │ Worker Pods   │  │   │
│  │  └───────────────┘  │  │  └───────────────┘  │  │  └───────────────┘  │   │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                           Data Layer                                    │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │   │
│  │  │ Amazon RDS      │  │ Amazon ElastiCache│  │ Amazon S3       │       │   │
│  │  │ (PostgreSQL)    │  │ (Redis)          │  │ (Files, Backups)│       │   │
│  │  │ Multi-AZ        │  │ Cluster Mode     │  │ Versioning      │       │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │   │
│  │  ┌─────────────────┐  ┌─────────────────┐                              │   │
│  │  │ Amazon MSK      │  │ Amazon SQS       │                              │   │
│  │  │ (Kafka)         │  │ (Queue)          │                              │   │
│  │  └─────────────────┘  └─────────────────┘                              │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                           Monitoring & Logging                          │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │   │
│  │  │ CloudWatch      │  │ Prometheus      │  │ Grafana         │       │   │
│  │  │ Metrics & Logs  │  │ (Custom Metrics)│  │ (Dashboards)    │       │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │   │
│  │  ┌─────────────────┐  ┌─────────────────┐                              │   │
│  │  │ AWS X-Ray       │  │ Loki            │                              │   │
│  │  │ Tracing         │  │ (Log Aggregation)│                              │   │
│  │  └─────────────────┘  └─────────────────┘                              │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### AWS Components

#### EKS Cluster Configuration

```yaml
# deployments/aws/eks-cluster.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: memoria-ai
  region: us-east-1
  version: "1.27"

managedNodeGroups:
  - name: general-purpose
    instanceType: t3.large
    desiredCapacity: 3
    minSize: 3
    maxSize: 10
    labels:
      node-type: general
    taints: []
    tags:
      Environment: production
      NodeGroup: general
  
  - name: memory-optimized
    instanceType: r6g.large
    desiredCapacity: 2
    minSize: 2
    maxSize: 5
    labels:
      node-type: memory
    taints: []
    tags:
      Environment: production
      NodeGroup: memory
  
  - name: gpu-enabled
    instanceType: g4dn.xlarge
    desiredCapacity: 1
    minSize: 0
    maxSize: 3
    labels:
      node-type: gpu
    taints:
      - key: nvidia.com/gpu
        effect: NoSchedule
    tags:
      Environment: production
      NodeGroup: gpu

cloudWatch:
  clusterLogging:
    enableTypes: ["*"]

iam:
  withOIDC: true
  serviceAccounts:
    - metadata:
        name: ebs-csi-controller-sa
      attachPolicyARNs:
        - arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy

vpc:
  cidr: "10.0.0.0/16"
  clusterEndpoints:
    publicAccess: true
    privateAccess: true
```

#### RDS Configuration

```hcl
# deployments/aws/rds.tf
resource "aws_db_instance" "memoria_ai" {
  identifier = "memoria-ai-prod"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.xlarge"
  
  allocated_storage     = 100
  max_allocated_storage = 1000
  storage_encrypted     = true
  storage_type          = "gp3"
  iops                  = 3000
  
  db_name  = "memoria_ai"
  username = var.db_username
  password = var.db_password
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  
  multi_az               = true
  publicly_accessible    = false
  
  backup_retention_period = 30
  backup_window          = "03:00-06:00"
  maintenance_window     = "Mon:00:00-Mon:03:00"
  
  performance_insight_enabled = true
  monitoring_interval       = 60
  
  deletion_protection = true
  
  tags = {
    Name        = "memoria-ai-prod"
    Environment = "production"
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "memoria-ai-subnet-group"
  subnet_ids = var.private_subnet_ids
  
  tags = {
    Name = "Memoria AI DB Subnet Group"
  }
}
```

#### ElastiCache Configuration

```hcl
# deployments/aws/elasticache.tf
resource "aws_elasticache_replication_group" "memoria_ai" {
  replication_group_id = "memoria-ai-prod"
  description          = "Memoria AI Redis Cluster"
  
  node_type            = "cache.r6g.large"
  num_cache_clusters   = 3
  port                 = 6379
  
  engine               = "redis"
  engine_version       = "7.0"
  parameter_group_name = "default.redis7"
  
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  subnet_group_name  = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]
  
  snapshot_retention_limit = 7
  snapshot_window         = "02:00-03:00"
  
  tags = {
    Name        = "memoria-ai-prod"
    Environment = "production"
  }
}
```

---

## Vercel Deployment

### Configuration

```json
// vercel.json
{
  "name": "memoria-ai",
  "version": 2,
  "builds": [
    {
      "src": "apps/frontend/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.memoria.ai/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.memoria.ai",
    "NEXT_PUBLIC_APP_URL": "https://memoria.ai"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### Deployment Script

```bash
# scripts/deploy-vercel.sh
#!/bin/bash

# Set environment
export VERCEL_ORGANIZATION="memoria-ai"
export VERCEL_PROJECT_ID="prj_xxxxx"

# Build and deploy
cd apps/frontend
npm run build
vercel --prod --token=$VERCEL_TOKEN

# Deploy to production
vercel --prod --token=$VERCEL_TOKEN --yes
```

---

## Render Deployment

### Configuration

```yaml
# render.yaml
services:
  - type: web
    name: memoria-ai-backend
    env: docker
    plan: starter
    dockerContext: ./apps/backend
    dockerfilePath: ./apps/backend/Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: memoria-ai-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          type: redis
          name: memoria-ai-redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: OPENAI_API_KEY
        sync: false
    healthCheckPath: /health

databases:
  - name: memoria-ai-db
    databaseName: memoria_ai
    user: memoria
    plan: starter

  - name: memoria-ai-redis
    plan: starter
    maxmemoryPolicy: allkeys-lru
```

---

## Self-Hosted Deployment

### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: memoria-postgres
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: memoria_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: memoria-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: memoria-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    restart: unless-stopped
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
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/memoria_ai
      REDIS_URL: redis://redis:6379/0
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      RABBITMQ_USER: ${RABBITMQ_USER}
      RABBITMQ_PASSWORD: ${RABBITMQ_PASSWORD}
      SECRET_KEY: ${SECRET_KEY}
      ENVIRONMENT: production
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
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./apps/frontend
      dockerfile: Dockerfile
    container_name: memoria-frontend
    environment:
      NEXT_PUBLIC_API_URL: https://api.memoria.ai
      NEXT_PUBLIC_APP_URL: https://memoria.ai
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: memoria-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployments/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./deployments/nginx/ssl:/etc/nginx/ssl:ro
      - ./deployments/nginx/logs:/var/log/nginx
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: memoria-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./deployments/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: memoria-grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
  backend_uploads:
  prometheus_data:
  grafana_data:
```

---

## Scaling Strategy

### Horizontal Pod Autoscaler

```yaml
# deployments/kubernetes/hpa-backend.yaml
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
  maxReplicas: 20
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
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 4
        periodSeconds: 30
      selectPolicy: Max
```

### Cluster Autoscaler

```yaml
# deployments/kubernetes/cluster-autoscaler.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler
  namespace: kube-system
data:
  cluster-autoscaler: |
    balance-similar-node-groups: true
    skip-nodes-with-system-pods: false
    max-node-provision-time: 15m
    pods-per-node: 30
    scale-down-enabled: true
    scale-down-delay-after-add: 10m
    scale-down-delay-after-delete: 10s
    scale-down-delay-after-failure: 3m
    scale-down-unneeded-time: 10m
    scale-down-utilization-threshold: 0.5
```

---

## Deployment Strategies

### Blue-Green Deployment

```yaml
# deployments/kubernetes/blue-green-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: memoria-backend
  namespace: memoria-ai
spec:
  replicas: 5
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
  strategy:
    blueGreen:
      activeService: memoria-backend-active
      previewService: memoria-backend-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: memoria-backend-preview
      promotionAnalysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: memoria-backend-active
```

### Canary Deployment

```yaml
# deployments/kubernetes/canary-deployment.yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: memoria-backend
  namespace: memoria-ai
spec:
  replicas: 10
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
  strategy:
    canary:
      canaryService: memoria-backend-canary
      stableService: memoria-backend-stable
      trafficRouting:
        nginx:
          stableIngress: memoria-ingress
      steps:
      - setWeight: 10
      - pause: {duration: 10m}
      - setWeight: 25
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 75
      - pause: {duration: 10m}
      - setWeight: 100
      analysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: memoria-backend-canary
```

---

## Migration Strategy

### Database Migration

```bash
# scripts/migrate-database.sh
#!/bin/bash

# Configuration
ENVIRONMENT=${1:-staging}
BACKUP_DIR="/backups/migrations"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup before migration
echo "Creating backup..."
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/pre_migration_$TIMESTAMP.sql

# Run migrations
echo "Running migrations..."
cd apps/backend
alembic upgrade head

# Verify migration
echo "Verifying migration..."
alembic current

# If verification fails, rollback
if [ $? -ne 0 ]; then
    echo "Migration failed, rolling back..."
    alembic downgrade -1
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME < $BACKUP_DIR/pre_migration_$TIMESTAMP.sql
    exit 1
fi

echo "Migration completed successfully"
```

---

## Rollback Strategy

### Automated Rollback

```yaml
# .github/workflows/rollback.yml
name: Rollback Deployment

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to rollback'
        required: true
        default: 'production'
        type: choice
        options:
          - staging
          - production
      version:
        description: 'Version to rollback to'
        required: true

jobs:
  rollback:
    name: Rollback to Previous Version
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.version }}
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG_${{ github.event.inputs.environment }} }}
      
      - name: Rollback deployment
        run: |
          kubectl rollout undo deployment/memoria-backend -n ${{ github.event.inputs.environment }}
          kubectl rollout undo deployment/memoria-frontend -n ${{ github.event.inputs.environment }}
      
      - name: Verify rollback
        run: |
          kubectl rollout status deployment/memoria-backend -n ${{ github.event.inputs.environment }}
          kubectl rollout status deployment/memoria-frontend -n ${{ github.event.inputs.environment }}
      
      - name: Run smoke tests
        run: |
          cd tests/e2e
          npm ci
          npm run test:${{ github.event.inputs.environment }}
      
      - name: Notify rollback
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: "Rollback to version ${{ github.event.inputs.version }} completed"
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Disaster Recovery

### Multi-Region Deployment

```yaml
# deployments/kubernetes/multi-region.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: disaster-recovery-config
  namespace: memoria-ai
data:
  primary-region: "us-east-1"
  secondary-region: "us-west-2"
  failover-threshold: "5"
  data-replication-enabled: "true"
  backup-frequency: "hourly"
  recovery-time-objective: "4h"
  recovery-point-objective: "1h"
```

### Failover Procedure

```bash
# scripts/failover.sh
#!/bin/bash

PRIMARY_REGION="us-east-1"
SECONDARY_REGION="us-west-2"
NAMESPACE="memoria-ai"

# Check primary region health
HEALTH_CHECK=$(curl -s https://api.memoria.ai/health)

if [ "$HEALTH_CHECK" != "healthy" ]; then
    echo "Primary region unhealthy, initiating failover..."
    
    # Switch DNS to secondary region
    aws route53 change-resource-record-sets \
        --hosted-zone-id $HOSTED_ZONE_ID \
        --change-batch file://failover-change.json
    
    # Scale up secondary region
    kubectl config use-context $SECONDARY_REGION
    kubectl scale deployment memoria-backend -n $NAMESPACE --replicas=10
    kubectl scale deployment memoria-frontend -n $NAMESPACE --replicas=5
    
    # Verify failover
    sleep 60
    NEW_HEALTH_CHECK=$(curl -s https://api.memoria.ai/health)
    
    if [ "$NEW_HEALTH_CHECK" == "healthy" ]; then
        echo "Failover successful"
        # Notify team
        send_alert "Failover to $SECONDARY_REGION completed successfully"
    else
        echo "Failover failed, manual intervention required"
        send_alert "Failover to $SECONDARY_REGION failed"
        exit 1
    fi
fi
```

---

## Cost Optimization

### Resource Limits

```yaml
# deployments/kubernetes/resource-limits.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: resource-limits
  namespace: memoria-ai
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "250m"
      memory: "256Mi"
    max:
      cpu: "2000m"
      memory: "2Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

### Spot Instances

```yaml
# deployments/aws/spot-instances.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

managedNodeGroups:
  - name: spot-instances
    instanceType: t3.large
    desiredCapacity: 5
    minSize: 0
    maxSize: 20
    spot: true
    labels:
      node-type: spot
    taints:
      - key: spot
        effect: NoSchedule
    tags:
      Environment: production
      NodeGroup: spot
```

---

## Monitoring Deployment

### Health Checks

```python
# core/health/health_check.py
from fastapi import APIRouter, HTTPException
from typing import Dict
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict:
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "rabbitmq": await check_rabbitmq(),
        "vector_db": await check_vector_db()
    }
    
    all_healthy = all(check["status"] == "healthy" for check in checks.values())
    
    if all_healthy:
        return {"status": "healthy", "checks": checks}
    else:
        raise HTTPException(status_code=503, detail={"status": "unhealthy", "checks": checks})

async def check_database() -> Dict:
    try:
        # Check database connection
        await db.execute("SELECT 1")
        return {"status": "healthy", "message": "Database is responsive"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

async def check_redis() -> Dict:
    try:
        await redis.ping()
        return {"status": "healthy", "message": "Redis is responsive"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

async def check_rabbitmq() -> Dict:
    try:
        # Check RabbitMQ connection
        return {"status": "healthy", "message": "RabbitMQ is responsive"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

async def check_vector_db() -> Dict:
    try:
        # Check vector database connection
        await vector_db.health_check()
        return {"status": "healthy", "message": "Vector DB is responsive"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}
```

---

## Best Practices

### 1. Deployment
- Use immutable infrastructure
- Implement blue-green deployments
- Use canary releases for critical changes
- Automate rollback procedures
- Test in staging before production

### 2. Scaling
- Use horizontal scaling for stateless services
- Use vertical scaling for databases
- Implement auto-scaling policies
- Monitor resource utilization
- Set appropriate resource limits

### 3. High Availability
- Deploy across multiple availability zones
- Use load balancers
- Implement health checks
- Use multi-region deployment for critical services
- Implement disaster recovery procedures

### 4. Security
- Use secrets management
- Implement network policies
- Use TLS for all communications
- Regular security audits
- Keep dependencies updated

### 5. Cost Management
- Use spot instances for non-critical workloads
- Implement auto-scaling
- Monitor resource usage
- Use reserved instances for baseline load
- Optimize storage costs

---

**Document Status:** Approved
**Next Review:** Q4 2026
**Owner:** DevOps Team
