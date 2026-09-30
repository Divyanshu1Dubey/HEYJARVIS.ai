# Disaster Recovery — RPO, RTO, and Recovery Procedures

## DR.1 Recovery Objectives

| System Component | RPO (Recovery Point Objective) | RTO (Recovery Time Objective) | Priority |
|-----------------|-------------------------------|------------------------------|----------|
| Primary database | 1 hour | 2 hours | P0 |
| API servers | N/A (stateless) | 15 minutes | P0 |
| Worker services | N/A (stateless) | 15 minutes | P0 |
| Queue system | 5 minutes | 30 minutes | P0 |
| Cache (Redis) | 15 minutes | 15 minutes | P1 |
| Object storage | 1 hour | 1 hour | P2 |
| Frontend | N/A (static) | 15 minutes | P2 |
| Monitoring | 15 minutes | 1 hour | P2 |

## DR.2 Backup Strategy

### Database Backups

```
FULL BACKUP: Daily at 2 AM UTC
├── Method: pg_dump with compression
├── Retention: 30 days
├── Storage: S3 (primary) + Glacier (archive)
└── Verification: Weekly restore test

INCREMENTAL BACKUP: Every 1 hour
├── Method: WAL archiving
├── Retention: 7 days
├── Storage: S3
└── Enables point-in-time recovery

BACKUP SCHEDULE:
02:00 UTC - Full backup
03:00 UTC - Incremental
04:00 UTC - Incremental
...
Next 02:00 UTC - Full backup (previous day's backup replaced)
```

```python
class BackupService:
    async def create_full_backup(self):
        """Create full database backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_full_{timestamp}.sql.gz"

        # Create backup
        proc = await asyncio.create_subprocess_exec(
            "pg_dump",
            "-h", self.db_host,
            "-U", self.db_user,
            "-d", self.db_name,
            "-F", "c",  # Custom format
            "-f", f"/tmp/{filename}",
            env={"PGPASSWORD": self.db_password}
        )
        await proc.wait()

        # Upload to S3
        await self.s3.upload(f"/tmp/{filename}", f"backups/{filename}")

        # Verify backup
        if not await self.verify_backup(filename):
            await self.alert_ops("Backup verification failed")

        # Clean up local file
        os.remove(f"/tmp/{filename}")

    async def verify_backup(self, filename: str) -> bool:
        """Verify backup can be restored."""
        # Download backup
        await self.s3.download(f"backups/{filename}", f"/tmp/{filename}")

        # Try to restore to test database
        try:
            await asyncio.create_subprocess_exec(
                "pg_restore",
                "-h", self.test_db_host,
                "-U", self.test_db_user,
                "-d", self.test_db_name,
                "-c",  # Clean before restore
                f"/tmp/{filename}",
                env={"PGPASSWORD": self.test_db_password}
            )
            return True
        except Exception:
            return False
```

### Point-in-Time Recovery

```python
async def restore_to_point_in_time(self, target_time: datetime):
    """Restore database to a specific point in time."""

    # 1. Stop all writes to database
    await self.stop_application()

    # 2. Create new database from latest backup
    latest_backup = await self.get_latest_backup()
    await self.restore_backup(latest_backup)

    # 3. Apply WAL files up to target time
    wal_files = await self.get_wal_files_between(
        latest_backup.timestamp,
        target_time
    )
    await self.apply_wal_files(wal_files, target_time)

    # 4. Verify data
    await self.verify_restore(target_time)

    # 5. Switch traffic to restored database
    await self.switch_database()

    # 6. Resume application
    await self.start_application()
```

## DR.3 Failover Procedures

### Database Failover

```python
class DatabaseFailover:
    async def failover(self):
        """Failover from primary to replica database."""

        # 1. Verify replica is healthy
        replica_health = await self.check_replica_health()
        if not replica_health.healthy:
            raise FailoverError("Replica is not healthy")

        # 2. Verify replica is up to date
        replication_lag = replica_health.lag_seconds
        if replication_lag > 300:  # 5 minutes
            raise FailoverError(f"Replica lag too high: {replication_lag}s")

        # 3. Promote replica
        await self.promote_replica()

        # 4. Update connection strings
        await self.update_connection_strings()

        # 5. Verify application works with new primary
        await self.verify_application_health()

        # 6. Notify team
        await self.notify_failover_complete()
```

### Application Failover

```yaml
# Kubernetes deployment with multiple replicas
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3  # At least 3 for high availability
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      containers:
      - name: api
        image: heyjarvis/api:v1.2.3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## DR.4 Disaster Recovery Runbook

### Complete System Failure

```
SCENARIO: Primary region is completely unavailable

STEP 1: Assess
- Confirm primary region is down
- Check if secondary region can be activated
- Estimate data loss (last backup time)

STEP 2: Activate Secondary Region
- Promote secondary database to primary
- Update DNS to point to secondary region
- Verify all services in secondary region

STEP 3: Verify
- Run smoke tests
- Verify data integrity
- Verify all integrations working
- Verify monitoring working

STEP 4: Communicate
- Notify all stakeholders
- Update status page
- Notify affected clinics

STEP 5: Monitor
- Watch for errors
- Monitor performance
- Be ready to roll back

STEP 6: Recovery (when primary is back)
- Stop writes to secondary
- Sync data from secondary back to primary
- Switch DNS back to primary
- Verify everything working
```

## DR.5 Data Integrity

```python
class DataIntegrityCheck:
    """Regular data integrity verification."""

    async def verify_database_integrity(self):
        """Verify database integrity."""

        checks = [
            # Foreign key integrity
            "SELECT COUNT(*) FROM appointments a WHERE NOT EXISTS (SELECT 1 FROM patients p WHERE p.id = a.patient_id)",

            # Orphaned records
            "SELECT COUNT(*) FROM messages m WHERE NOT EXISTS (SELECT 1 FROM conversations c WHERE c.id = m.conversation_id)",

            # Duplicate opportunities
            "SELECT patient_id, category, COUNT(*) FROM recapture_opportunities GROUP BY patient_id, category HAVING COUNT(*) > 1",

            # Missing required fields
            "SELECT COUNT(*) FROM patients WHERE phone IS NULL OR first_name IS NULL"
        ]

        results = {}
        for check in checks:
            count = await self.db.scalar(check)
            results[check] = count

        return results
```

## DR.6 Regular Recovery Testing

| Test | Frequency | Duration | Success Criteria |
|------|-----------|----------|-----------------|
| Backup restore test | Weekly | 30 min | Backup restores successfully |
| Database failover | Monthly | 15 min | Failover completes within RTO |
| Full disaster recovery | Quarterly | 4 hours | System fully operational |

```python
async def test_backup_restore(self):
    """Weekly backup restore test."""

    # Get latest backup
    backup = await self.get_latest_backup()

    # Restore to test environment
    start = time.time()
    await self.restore_backup(backup, target="test_db")
    duration = time.time() - start

    # Verify data
    row_count = await self.db.scalar("SELECT COUNT(*) FROM patients")
    assert row_count > 0

    # Verify within RTO
    assert duration < self.RTO["database"]

    return {
        "backup": backup.filename,
        "duration_seconds": duration,
        "rows_restored": row_count,
        "passed": True
    }
```
