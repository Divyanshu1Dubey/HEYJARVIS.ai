# Deployment — Production Deployment Guide

## DP.1 Deployment Architecture

```
PRODUCTION ENVIRONMENT
├── us-east-1 (Primary Region)
│   ├── VPC
│   │   ├── Public Subnets (ALB, NAT Gateway)
│   │   ├── Private Subnets (API, Workers)
│   │   └── Data Subnets (Database, Redis)
│   │
│   ├── EKS Cluster (Kubernetes)
│   │   ├── API Servers (3 replicas)
│   │   ├── Worker Services (5 replicas)
│   │   ├── Scheduled Jobs (1 replica)
│   │   └── Monitoring
│   │
│   ├── RDS PostgreSQL
│   │   ├── Primary (db.r6g.2xlarge)
│   │   └── Read Replicas (2x db.r6g.xlarge)
│   │
│   ├── ElastiCache Redis
│   │   └── Primary + Replica (cache.r6g.large)
│   │
│   ├── S3 (Object Storage)
│   │   ├── Application data
│   │   └── Backups
│   │
│   ├── SQS (Message Queue)
│   │   ├── Standard Queue
│   │   └── Dead Letter Queue
│   │
│   └── ALB (Application Load Balancer)
│
├── us-west-2 (DR Region)
│   └── [Same structure, standby]
│
└── CloudFront (CDN for frontend)
```

## DP.2 Deployment Environments

| Environment | Purpose | Data | Deploy Trigger |
|-------------|---------|------|---------------|
| **Development** | Local development | Synthetic | Manual |
| **Staging** | Pre-production testing | Synthetic | Every PR merge |
| **Production** | Live system | Real PHI | Manual approval |

## DP.3 CI/CD Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Code   │───▶│   Lint   │───▶│   Test   │───▶│ Security │
│ Commit   │    │  & Type  │    │  & Eval  │    │   Scan   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                    ┌─────────────────────────────────┘
                    ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │  Build   │───▶│   Push   │───▶│ Staging  │
              │  Docker  │    │  Image   │    │ Deploy   │
              └──────────┘    └──────────┘    └──────────┘
                                           │
                    ┌──────────────────────┘
                    ▼
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │  Smoke   │───▶│  E2E    │───▶│ Manual   │
              │  Tests   │    │  Tests   │    │Approval  │
              └──────────┘    └──────────┘    └──────────┘
                                           │
                    ┌──────────────────────┘
                    ▼
              ┌──────────┐    ┌──────────┐
              │Canary    │───▶│  Full    │
              │Deploy    │    │ Rollout  │
              └──────────┘    └──────────┘
```

## DP.4 Deployment Scripts

### Deploy to Staging

```bash
#!/bin/bash
# scripts/deploy-staging.sh
set -e

echo "Building..."
pnpm build

echo "Building Docker images..."
docker build -f infra/docker/Dockerfile.api -t heyjarvis/api:$SHA apps/api/
docker build -f infra/docker/Dockerfile.worker -t heyjarvis/worker:$SHA apps/worker/

echo "Pushing to registry..."
docker push heyjarvis/api:$SHA
docker push heyjarvis/worker:$SHA

echo "Deploying to staging..."
kubectl apply -f infra/kubernetes/staging/

echo "Running smoke tests..."
pytest tests/e2e/test_smoke.py --env=staging

echo "Deployment complete!"
```

### Deploy to Production

```bash
#!/bin/bash
# scripts/deploy-production.sh
set -e

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./deploy-production.sh <version>"
    exit 1
fi

echo "Deploying version $VERSION to production..."

# 1. Deploy API (canary)
echo "Deploying API (canary 5%)..."
kubectl set image deployment/api \
    api=heyjarvis/api:$VERSION \
    -n heyjarvis-production

kubectl rollout pause deployment/api -n heyjarvis-production

# 2. Wait for rollout
kubectl rollout status deployment/api -n heyjarvis-production --timeout=10m

# 3. Run smoke tests
pytest tests/e2e/test_smoke.py --env=production

# 4. Canary for 1 hour
echo "Running canary (1 hour)..."
sleep 3600

# 5. Check metrics
ERROR_RATE=$(datadog query 'avg:api.errors.rate{env:production}' -s 3600)
if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
    echo "ERROR: Error rate too high: $ERROR_RATE"
    kubectl rollout undo deployment/api -n heyjarvis-production
    exit 1
fi

# 6. Full rollout
echo "Rolling out to 100%..."
kubectl rollout resume deployment/api -n heyjarvis-production
kubectl rollout status deployment/api -n heyjarvis-production

# 7. Deploy workers
echo "Deploying workers..."
kubectl set image deployment/worker \
    worker=heyjarvis/worker:$VERSION \
    -n heyjarvis-production
kubectl rollout status deployment/worker -n heyjarvis-production

echo "Deployment complete!"
```

## DP.5 Rollback Procedure

```bash
#!/bin/bash
# scripts/rollback.sh

# 1. Identify last known good version
PREVIOUS_VERSION=$(kubectl rollout history deployment/api -n heyjarvis-production | tail -2 | head -1 | awk '{print $1}')

echo "Rolling back to $PREVIOUS_VERSION..."

# 2. Rollback deployment
kubectl rollout undo deployment/api -n heyjarvis-production
kubectl rollout undo deployment/worker -n heyjarvis-production

# 3. Wait for rollout
kubectl rollout status deployment/api -n heyjarvis-production
kubectl rollout status deployment/worker -n heyjarvis-production

# 4. Verify
pytest tests/e2e/test_smoke.py --env=production

# 5. Notify team
curl -X POST $SLACK_WEBHOOK \
    -d '{"text": "Production rolled back to '"$PREVIOUS_VERSION"'"}'

echo "Rollback complete!"
```

## DP.6 Secrets Management

```bash
# Secrets stored in HashiCorp Vault

# Deploy secrets to Kubernetes
vault-k8s inject \
    --method=kubernetes \
    --path=kubernetes \
    --role=heyjarvis-production \
    deployment/api
```

## DP.7 Database Migrations

```bash
# Migration strategy: Online schema changes

# 1. Create migration
alembic revision -m "add column to patients"

# 2. Test migration
alembic upgrade head --sql > migration.sql
# Review migration.sql
# Test on staging

# 3. Deploy migration (before app deploy)
kubectl exec -it job/migrate -n heyjarvis-production -- \
    alembic upgrade head

# 4. Deploy application
kubectl apply -f infra/kubernetes/production/
```

## DP.8 Zero-Downtime Deployment

```yaml
# Kubernetes rolling update config
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1      # Max 1 pod down at a time
      maxSurge: 1            # Max 1 extra pod during update

  template:
    spec:
      containers:
      - name: api
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 3

        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3

        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 10"]  # Graceful drain
```

## DP.9 Monitoring Deployment

```bash
# Verify deployment health
kubectl get pods -n heyjarvis-production
kubectl get services -n heyjarvis-production
kubectl get hpa -n heyjarvis-production

# Check logs
kubectl logs -f deployment/api -n heyjarvis-production
kubectl logs -f deployment/worker -n heyjarvis-production

# Check metrics
kubectl top pods -n heyjarvis-production
```

## DP.10 Post-Deployment Checklist

```
□ All pods running and healthy
□ API latency < 200ms p95
□ Error rate < 0.5%
□ Queue depth normal
□ Database connections normal
□ All integrations healthy
□ Smoke tests passing
□ Canary metrics normal
□ No unexpected alerts
□ Team notified
□ Status page updated (if needed)
□ Rollback plan ready
```
