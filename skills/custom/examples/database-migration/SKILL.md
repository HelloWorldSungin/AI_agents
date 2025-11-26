---
name: database-migration
description: Safe database migration procedures with backward compatibility, backups, and rollback strategies. Use when creating, modifying, or dropping database schemas. Covers migration creation, testing, execution, and rollback.
version: 1.0.0
author: Database Team
category: custom
token_estimate: ~3000
---

<objective>
This skill provides procedures for safely executing database schema changes with minimal downtime and reliable rollback capability. It ensures migrations are tested, backward compatible, and can be safely applied to production databases.
</objective>

<when_to_use>
Use this skill when:

- Adding/modifying/removing database tables or columns
- Creating or dropping indexes
- Changing constraints or relationships
- Migrating data between schemas
- Altering database configurations

Do NOT use this skill when:

- Making simple data updates (use database query skills)
- One-time data fixes (use admin scripts)
- Schema-less database changes (document/key-value stores)
</when_to_use>

<prerequisites>
- Migration tool installed (Alembic, Flyway, Django migrations, etc.)
- Database backup capability available
- Staging environment that mirrors production
- Database admin access for production
- Rollback window defined
</prerequisites>

<workflow>
<step name="Create Migration">
Generate migration file with descriptive name:

**Using Alembic (Python):**
```bash
# Generate migration
alembic revision --autogenerate -m "add_user_preferences_table"

# Review generated migration
cat alembic/versions/abc123_add_user_preferences_table.py
```

**Migration Structure:**
```python
"""add user preferences table

Revision ID: abc123
Revises: xyz789
Create Date: 2025-01-20 10:30:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'xyz789'

def upgrade():
    """Apply migration."""
    # Create table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('theme', sa.String(20), default='light'),
        sa.Column('notifications_enabled', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now())
    )

    # Create indexes for common queries
    op.create_index('idx_user_preferences_user_id', 'user_preferences', ['user_id'])

def downgrade():
    """Rollback migration."""
    op.drop_index('idx_user_preferences_user_id')
    op.drop_table('user_preferences')
```

**Key Requirements:**
- Both `upgrade()` and `downgrade()` must be defined
- Descriptive migration message
- Include indexes for performance
- Foreign keys properly defined
</step>

<step name="Ensure Backward Compatibility">
Make migrations safe for zero-downtime deployments:

**Backward Compatible Patterns:**

**Adding Column (nullable or with default):**
```python
# Good: Nullable column (old code won't break)
op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))

# Good: Column with default (old code gets default value)
op.add_column('users', sa.Column('status', sa.String(20), server_default='active'))

# Bad: Required column without default (breaks old code)
op.add_column('users', sa.Column('required_field', sa.String(50), nullable=False))
```

**Removing Column (two-step process):**
```python
# Step 1 (Deploy first): Make column nullable, update code to not use it
op.alter_column('users', 'old_column', nullable=True)

# Step 2 (Deploy later): Remove column after old code is gone
op.drop_column('users', 'old_column')
```

**Renaming Column (multi-step process):**
```python
# Step 1: Add new column
op.add_column('users', sa.Column('new_name', sa.String(100)))

# Step 2: Backfill data
op.execute('UPDATE users SET new_name = old_name WHERE new_name IS NULL')

# Step 3 (separate migration): Drop old column after code updated
op.drop_column('users', 'old_name')
```

**Changing Column Type (multi-step):**
```python
# Step 1: Add new column with new type
op.add_column('users', sa.Column('age_int', sa.Integer()))

# Step 2: Migrate data
op.execute('UPDATE users SET age_int = CAST(age_string AS INTEGER)')

# Step 3 (separate migration): Remove old column
op.drop_column('users', 'age_string')
```
</step>

<step name="Test Migration in Staging">
Validate migration before production:

**Create Staging Database Snapshot:**
```bash
# Restore production snapshot to staging (sanitize PII first)
pg_dump production_db | pg_restore -d staging_db
```

**Apply Migration:**
```bash
# Run migration in staging
alembic upgrade head

# Check migration applied
alembic current

# Verify database state
psql staging_db -c "\d+ user_preferences"
```

**Test Application Compatibility:**
```bash
# Deploy code to staging
kubectl set image deployment/app app=myapp:new-version -n staging

# Run smoke tests
pytest tests/integration/ --env=staging

# Verify key workflows work
curl https://staging.api.com/health
```

**Test Rollback:**
```bash
# Rollback migration
alembic downgrade -1

# Verify rollback succeeded
alembic current
psql staging_db -c "\d+ user_preferences"  # Should not exist

# Re-apply for production
alembic upgrade head
```

**Staging Checklist:**
- [ ] Migration applies successfully
- [ ] Application works with new schema
- [ ] Application works with old schema (before migration)
- [ ] Rollback works correctly
- [ ] Performance is acceptable (check query times)
- [ ] Indexes are effective (check query plans)
</step>

<step name="Backup Production Database">
Always backup before migration:

**PostgreSQL Backup:**
```bash
# Full backup
pg_dump -h production-host -U dbuser -d production_db \
  -F c -f backup_before_migration_$(date +%Y%m%d_%H%M%S).dump

# Verify backup
pg_restore --list backup_before_migration_20250120_103000.dump | head

# Store securely
aws s3 cp backup_before_migration_20250120_103000.dump \
  s3://backups/migrations/
```

**MySQL Backup:**
```bash
# Full backup
mysqldump -h production-host -u dbuser -p production_db \
  > backup_before_migration_$(date +%Y%m%d_%H%M%S).sql

# Verify
head -n 50 backup_before_migration_20250120_103000.sql
```

**Document Backup:**
```bash
# Record backup details
echo "Migration: add_user_preferences_table" > migration_backup_info.txt
echo "Backup file: backup_before_migration_20250120_103000.dump" >> migration_backup_info.txt
echo "Database: production_db" >> migration_backup_info.txt
echo "Time: $(date)" >> migration_backup_info.txt
echo "Size: $(du -h backup_before_migration_20250120_103000.dump)" >> migration_backup_info.txt
```
</step>

<step name="Execute Migration in Production">
Apply migration with monitoring:

**Pre-Migration Checks:**
```bash
# Verify backup exists
ls -lh backup_before_migration_*.dump

# Check database connection
psql -h production-host -U dbuser -d production_db -c "SELECT version();"

# Review migration to apply
alembic upgrade head --sql > migration_preview.sql
cat migration_preview.sql  # Review SQL before applying

# Check current database version
alembic current
```

**Apply Migration:**
```bash
# Connect to production
export DATABASE_URL="postgresql://user:pass@prod-host/prod_db"

# Apply migration
alembic upgrade head

# Verify applied
alembic current

# Check new table exists
psql $DATABASE_URL -c "\d+ user_preferences"
```

**Monitor Application:**
```bash
# Watch application logs for errors
kubectl logs -n production -l app=myapp --follow | grep -i error

# Check error rate in monitoring
# - Should remain stable
# - No spike in database errors

# Verify key endpoints
curl https://api.example.com/health
curl https://api.example.com/api/v1/users/me
```

**Validation:**
```bash
# Run smoke tests against production
pytest tests/smoke/ --env=production

# Check database metrics
# - Query performance
# - Connection count
# - Lock waits

# Verify indexes being used
psql $DATABASE_URL -c "EXPLAIN ANALYZE SELECT * FROM user_preferences WHERE user_id = 123;"
```
</step>

<step name="Rollback if Needed">
Rollback procedure if issues arise:

**When to Rollback:**
- Application errors increase significantly
- Migration takes longer than maintenance window
- Data corruption detected
- Performance severely degraded

**Rollback Steps:**
```bash
# 1. Stop application traffic (if severe)
kubectl scale deployment/app --replicas=0 -n production

# 2. Rollback migration
alembic downgrade -1

# 3. Verify rollback
alembic current
psql $DATABASE_URL -c "\d+ user_preferences"  # Should not exist

# 4. Restore application
kubectl scale deployment/app --replicas=5 -n production

# 5. Monitor for recovery
# Check error rates return to normal
# Verify application functionality
```

**If Rollback Fails:**
```bash
# Restore from backup (last resort)
pg_restore -h production-host -U dbuser -d production_db \
  --clean --if-exists \
  backup_before_migration_20250120_103000.dump

# Verify restore
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
# Compare with expected count

# Restart application
kubectl rollout restart deployment/app -n production
```
</step>
</workflow>

<best_practices>
<practice name="Always Test in Staging First">
Never apply untested migrations to production.
</practice>

<practice name="Backward Compatible Migrations">
Structure changes to work with both old and new code.
</practice>

<practice name="Small, Focused Migrations">
One logical change per migration for easier rollback.
</practice>

<practice name="Degree of Freedom">
**Low Freedom**: Database migrations require following exact procedures for safety. Core steps (backup, test, apply, verify) must not be skipped.
</practice>

<practice name="Token Efficiency">
This skill uses approximately **3,000 tokens** when fully loaded.
</practice>
</best_practices>

<common_pitfalls>
<pitfall name="No Backward Compatibility">
**What Happens:** Deployment fails because old code can't work with new schema.

**How to Avoid:**
- Add columns as nullable or with defaults
- Use multi-step migrations for breaking changes
- Test with old and new code versions
</pitfall>

<pitfall name="Skipping Staging Validation">
**What Happens:** Migration fails in production due to data issues not present in testing.

**How to Avoid:**
- Use production snapshot for staging
- Test with realistic data volumes
- Verify migration and rollback both work
</pitfall>

<pitfall name="No Backup">
**What Happens:** Migration causes data loss with no recovery option.

**How to Avoid:**
- Always backup before migration
- Verify backup is restorable
- Store backup securely
- Test restore process periodically
</pitfall>
</common_pitfalls>

<examples>
<example name="Adding Index for Performance">
**Context:** Users table queries are slow; need index on email column.

**Migration:**
```python
def upgrade():
    # Create index concurrently (doesn't lock table)
    op.create_index(
        'idx_users_email',
        'users',
        ['email'],
        unique=True,
        postgresql_concurrently=True
    )

def downgrade():
    op.drop_index('idx_users_email', 'users', postgresql_concurrently=True)
```

**Testing in Staging:**
```bash
# Apply migration
alembic upgrade head

# Test query performance
psql staging_db -c "EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';"
# Should show index scan, not seq scan

# Check index is used
psql staging_db -c "SELECT * FROM pg_stat_user_indexes WHERE indexrelname = 'idx_users_email';"
```

**Production Application:**
```bash
# Backup
pg_dump production_db -F c -f backup_before_index.dump

# Apply
alembic upgrade head
# Takes ~2 minutes for 1M rows with CONCURRENT

# Verify
psql production_db -c "\d+ users"
# Should show new index

# Monitor query performance improvement
# Check monitoring dashboards for query time reduction
```

**Outcome:** Index created without downtime. Query performance improved from 2s to 50ms.
</example>

<example name="Multi-Step Schema Change">
**Context:** Need to rename `username` column to `display_name` in users table.

**Step 1 Migration: Add New Column**
```python
def upgrade():
    # Add new column with same data
    op.add_column('users', sa.Column('display_name', sa.String(100)))

    # Copy data
    op.execute('UPDATE users SET display_name = username WHERE display_name IS NULL')

    # Make non-nullable after data copied
    op.alter_column('users', 'display_name', nullable=False)

def downgrade():
    op.drop_column('users', 'display_name')
```

**Step 1 Code Update:**
```python
# Update code to write to both columns
class User(db.Model):
    username = db.Column(db.String(100))  # Old, will remove later
    display_name = db.Column(db.String(100))  # New

    def set_name(self, name):
        self.username = name  # Still write to old
        self.display_name = name  # Also write to new
```

**Deploy Step 1:**
```bash
# Apply migration
alembic upgrade head

# Deploy code that writes to both columns
kubectl set image deployment/app app=myapp:step1 -n production

# Monitor: No errors, both columns being written
```

**Step 2 Migration: Drop Old Column (weeks later)**
```python
def upgrade():
    # Drop old column (after code fully migrated)
    op.drop_column('users', 'username')

def downgrade():
    # Can't really undo this without data loss
    # Would need to add column and copy from display_name
    op.add_column('users', sa.Column('username', sa.String(100)))
    op.execute('UPDATE users SET username = display_name')
```

**Step 2 Code Update:**
```python
# Remove old column from code
class User(db.Model):
    display_name = db.Column(db.String(100))  # Only new column
```

**Deploy Step 2:**
```bash
# Deploy code that only uses display_name
kubectl set image deployment/app app=myapp:step2 -n production

# Wait a few days, verify stability

# Apply migration to drop old column
alembic upgrade head
```

**Outcome:** Zero-downtime rename completed over two deployments. Old and new code worked throughout.
</example>
</examples>

<related_skills>
- **deployment-workflow**: Coordinate migrations with application deployments
- **database-design**: Schema design best practices
- **monitoring-setup**: Monitor database performance during migrations
</related_skills>

<version_history>
**Version 1.0.0 (2025-01-20)**
- Initial creation
- Safe migration procedures
- Backward compatibility patterns
- Multi-step migration examples
</version_history>

<additional_resources>
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Zero-Downtime Database Migrations](https://spring.io/blog/2016/05/31/zero-downtime-deployment-with-a-database)
- Internal: Database Migration Runbook at [internal wiki]
</additional_resources>
