---
name: deployment-workflow
description: Production deployment workflow with safety checks and rollback procedures. Use when deploying applications to staging or production environments. Covers pre-deployment verification, staged rollout, monitoring, and rollback procedures.
version: 1.0.0
author: Platform Team
category: custom
token_estimate: ~3500
---

# Production Deployment Workflow Skill

## Purpose

This skill provides step-by-step guidance for safely deploying applications to production environments. It ensures all safety checks are performed, proper monitoring is in place, and rollback procedures are ready before deploying code that affects users.

## When to Use This Skill

Use this skill when:

- Deploying a service update to production
- Rolling out a new version of an application
- Applying configuration changes to production systems
- Performing blue-green or canary deployments
- Updating production infrastructure

Do NOT use this skill when:

- Deploying to local development environment
- Running tests in CI/CD (use testing skills instead)
- Making changes to non-production environments without risk

## Prerequisites

Before using this skill, ensure:

- Code has been reviewed and approved
- All tests pass in CI/CD pipeline
- Staging deployment completed successfully
- Rollback plan is documented
- On-call engineer is available
- Change has been communicated to team

## Instructions

### Step 1: Pre-Deployment Verification

Verify all prerequisites are met before starting deployment:

**Code Readiness:**
```bash
# Verify CI/CD pipeline passed
gh run list --branch main --limit 1 --json status,conclusion

# Expected: status=completed, conclusion=success
```

**Staging Validation:**
```bash
# Check staging deployment status
kubectl get deployment -n staging
kubectl get pods -n staging | grep -v Running

# Should see all pods Running, no errors
```

**Infrastructure Health:**
```bash
# Verify production cluster health
kubectl cluster-info
kubectl get nodes
kubectl top nodes

# All nodes should be Ready with reasonable resource usage
```

**Checklist:**
- [ ] All CI/CD tests passed
- [ ] Staging deployment successful and validated
- [ ] No active incidents in production
- [ ] Rollback plan documented
- [ ] Database migrations (if any) tested in staging
- [ ] Feature flags configured (if applicable)
- [ ] Monitoring alerts configured

### Step 2: Prepare for Deployment

Set up monitoring and prepare rollback resources:

**1. Create Deployment Tracking:**
```bash
# Create deployment tracking issue or ticket
# Document: version being deployed, key changes, rollback steps
```

**2. Set Up Monitoring Dashboard:**
```bash
# Open monitoring dashboards:
# - Application metrics (latency, error rate, throughput)
# - Infrastructure metrics (CPU, memory, disk)
# - Business metrics (user activity, transaction success rate)
```

**3. Notify Team:**
```bash
# Post in team channel:
# "🚀 Starting production deployment of [service-name] v[version]
#  Changes: [brief description]
#  ETA: [estimated time]
#  Monitoring: [dashboard link]"
```

**4. Verify Rollback Resources:**
```bash
# Confirm previous version artifacts are available
docker pull your-registry/service-name:previous-version

# Verify database backups are recent
# Check that rollback procedures are accessible
```

### Step 3: Execute Deployment

Deploy using your deployment method (examples provided for common scenarios):

**Kubernetes Rolling Update:**
```bash
# Update image tag in deployment
kubectl set image deployment/service-name \
  service-name=your-registry/service-name:new-version \
  -n production

# Monitor rollout
kubectl rollout status deployment/service-name -n production

# Watch pods coming up
kubectl get pods -n production -l app=service-name -w
```

**Blue-Green Deployment:**
```bash
# Deploy green version
kubectl apply -f deployment-green.yaml -n production

# Wait for green to be ready
kubectl wait --for=condition=ready pod \
  -l app=service-name,version=green \
  -n production \
  --timeout=300s

# Switch traffic to green
kubectl patch service service-name -n production \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Monitor for 5-10 minutes before cleaning up blue
```

**Canary Deployment:**
```bash
# Deploy canary with 10% traffic
kubectl apply -f deployment-canary.yaml -n production

# Monitor canary metrics for 10-15 minutes
# Compare error rates, latency between canary and stable

# If healthy, gradually increase canary traffic
kubectl scale deployment service-name-canary \
  --replicas=3 -n production  # 30% traffic

# Continue monitoring and scaling until full rollout
```

**Important Considerations:**
- Monitor metrics continuously during deployment
- Watch for error spikes or latency increases
- Check logs for unexpected errors
- Verify database connections are healthy

### Step 4: Post-Deployment Validation

Verify the deployment succeeded and system is healthy:

**1. Health Checks:**
```bash
# Verify all pods are running
kubectl get pods -n production -l app=service-name

# Check application health endpoint
curl https://api.example.com/health

# Expected response: {"status": "healthy", "version": "new-version"}
```

**2. Smoke Tests:**
```bash
# Run critical path tests
curl -X POST https://api.example.com/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "email": "test@example.com"}'

# Verify key functionality works
# Test authentication, critical endpoints, integrations
```

**3. Metrics Validation:**

Monitor for at least 15 minutes:

- **Error Rate**: Should be stable or improved (< 1% for most services)
- **Latency**: p50, p95, p99 should be stable or improved
- **Throughput**: Request rate should match expected traffic
- **Resource Usage**: CPU/Memory should be within normal ranges

**4. Log Analysis:**
```bash
# Check for errors in application logs
kubectl logs -n production -l app=service-name \
  --since=15m | grep -i error

# Review any warning or error patterns
```

**Validation Checklist:**
- [ ] All pods running and ready
- [ ] Health endpoints returning success
- [ ] Smoke tests passed
- [ ] Error rate normal
- [ ] Latency within acceptable range
- [ ] No unexpected errors in logs
- [ ] Database connections healthy
- [ ] Dependent services responding normally

### Step 5: Complete Deployment

Finalize deployment and communicate results:

**1. Update Documentation:**
```bash
# Update deployment tracking with results
# Document any issues encountered
# Note any configuration changes made
```

**2. Notify Team:**
```bash
# Post completion message:
# "✅ Production deployment of [service-name] v[version] complete
#  Status: Success
#  Metrics: [brief summary]
#  Issues: None / [describe any issues]"
```

**3. Clean Up (if applicable):**
```bash
# Remove old blue environment (blue-green deployment)
kubectl delete deployment service-name-blue -n production

# Scale down canary (canary deployment)
kubectl delete deployment service-name-canary -n production
```

**4. Schedule Follow-up:**
- Monitor metrics for next 24 hours
- Review performance in next team standup
- Document lessons learned if issues occurred

## Best Practices

### 1. Deploy During Low-Traffic Periods

**Rationale:** Reduces impact if issues occur and makes anomaly detection easier.

**Implementation:**
- Schedule non-urgent deployments during off-peak hours
- For 24/7 services, deploy during lowest traffic period
- Emergency fixes can be deployed anytime with extra caution

### 2. Use Feature Flags for Risky Changes

**Rationale:** Allows instant rollback of feature behavior without code deployment.

**Example:**
```python
# In application code
if feature_flags.is_enabled('new_algorithm'):
    result = new_algorithm(data)
else:
    result = legacy_algorithm(data)
```

Disable flag instantly if issues arise, no deployment needed.

### 3. Gradual Rollout Strategy

**Rationale:** Limits blast radius if issues occur.

**Implementation:**
- Start with 10% traffic (canary)
- Monitor for 15-30 minutes
- Increase to 50% if healthy
- Monitor for another 15-30 minutes
- Complete rollout to 100%

### 4. Degree of Freedom

**Medium Freedom**: Core safety steps must be followed (pre-deployment checks, monitoring, validation), but deployment method can be adapted based on:
- Service architecture (stateless vs. stateful)
- Risk level (hot-fix vs. major feature)
- Time constraints (emergency vs. planned)
- Team preferences (rolling vs. blue-green)

### 5. Token Efficiency

This skill uses approximately **3,500 tokens** when fully loaded.

**Optimization Strategy:**
- Core workflow: Always loaded (~2,500 tokens)
- Examples: Load for reference (~800 tokens)
- Detailed troubleshooting: Load if deployment issues occur (~200 tokens on-demand)

## Common Pitfalls

### Pitfall 1: Skipping Pre-Deployment Checks

**What Happens:** Deployment proceeds with failing tests or unhealthy staging environment, leading to production incidents.

**Why It Happens:** Pressure to deploy quickly, confidence in changes, or assumption that issues are minor.

**How to Avoid:**
1. Always verify CI/CD passed before deploying
2. Require staging validation for all deployments
3. Use automated gates in deployment pipeline
4. Don't skip checks even for "simple" changes

**Recovery:** If deployed without checks and issues arise, immediately roll back and perform full verification before re-deploying.

### Pitfall 2: Insufficient Monitoring During Deployment

**What Happens:** Issues go undetected until users report problems, making diagnosis harder and recovery slower.

**Why It Happens:** Assuming deployment will succeed, distractions, or lack of monitoring setup.

**How to Avoid:**
1. Open monitoring dashboards before starting deployment
2. Watch metrics continuously during rollout
3. Set up alerts for anomaly detection
4. Have dedicated person monitoring during deployment

**Warning Signs:**
- Gradual increase in error rate
- Latency creeping up over time
- Increased database query times
- Growing request queue length

### Pitfall 3: No Rollback Plan

**What Happens:** When issues occur, team scrambles to figure out how to recover, prolonging the incident.

**Why It Happens:** Optimism bias, time pressure, or lack of experience with rollbacks.

**How to Avoid:**
1. Document rollback steps before deployment
2. Verify previous version artifacts are available
3. Test rollback procedure in staging
4. Keep rollback instructions easily accessible

**Recovery:** If issues occur without rollback plan:
1. Check version control history for last good commit
2. Redeploy previous version using same deployment method
3. Verify in staging first if time permits
4. Communicate timeline to stakeholders

## Examples

### Example 1: Standard Kubernetes Rolling Update

**Context:** Deploying a new version of a stateless API service to production with low-risk changes (bug fixes, minor improvements).

**Situation:**
- Service: user-api
- Current version: v2.3.1
- New version: v2.4.0
- Changes: Bug fixes, performance optimizations
- Traffic: Moderate (~1000 req/min)

**Steps:**

1. **Pre-deployment verification:**
```bash
# Verify CI passed
gh run view --repo company/user-api

# Check staging
kubectl get deployment user-api -n staging
# Output: user-api   3/3     3            3           2h

# Verify staging health
curl https://staging.api.example.com/health
# Output: {"status": "healthy", "version": "v2.4.0"}
```

2. **Set up monitoring:**
```bash
# Open Datadog/Grafana dashboard
open https://monitoring.example.com/dashboards/user-api

# Post to Slack
slack post #deployments "🚀 Deploying user-api v2.4.0 to production. ETA: 10min"
```

3. **Execute deployment:**
```bash
# Update deployment
kubectl set image deployment/user-api \
  user-api=registry.example.com/user-api:v2.4.0 \
  -n production

# Monitor rollout
kubectl rollout status deployment/user-api -n production
# Output: deployment "user-api" successfully rolled out
```

4. **Validate:**
```bash
# Check pods
kubectl get pods -n production -l app=user-api
# All pods should show Running status

# Health check
curl https://api.example.com/health
# Output: {"status": "healthy", "version": "v2.4.0"}

# Check metrics (wait 15 minutes)
# - Error rate: 0.3% (was 0.4%, improved ✓)
# - Latency p95: 180ms (was 220ms, improved ✓)
# - Throughput: ~1000 req/min (stable ✓)
```

5. **Complete:**
```bash
slack post #deployments "✅ user-api v2.4.0 deployed successfully. Metrics looking good."
```

**Expected Output:**
```
Deployment successful
- Version: v2.4.0
- Pods: 5/5 running
- Health: All checks passed
- Metrics: Stable/Improved
- Duration: 8 minutes
```

**Outcome:** Deployment completed smoothly, performance improved as expected, no issues reported.

---

### Example 2: Blue-Green Deployment with Database Migration

**Context:** Deploying a major feature that requires database schema changes, using blue-green strategy to minimize downtime and enable fast rollback.

**Situation:**
- Service: payment-service
- Current version: v3.1.0 (blue)
- New version: v3.2.0 (green)
- Changes: New payment methods, database schema update
- Traffic: High (~5000 req/min)
- Migration: Adding tables for new payment types

**Challenges:**
- Database migration must be backward compatible
- High traffic requires zero-downtime deployment
- Financial service requires extra caution

**Steps:**

1. **Pre-deployment (extra careful):**
```bash
# Verify tests passed
gh run view --repo company/payment-service
# All checks passed: unit (850 tests), integration (120 tests), e2e (45 tests)

# Validate staging thoroughly
curl -X POST https://staging.api.example.com/api/v1/payments \
  -H "Authorization: Bearer $STAGING_TOKEN" \
  -d '{"method": "new_payment_type", "amount": 100}'
# Success: payment processed with new method

# Check database migration in staging
kubectl exec -n staging payment-service-db -it -- \
  psql -U app -c "\d payment_methods"
# New tables exist and are populated
```

2. **Deploy green with migration:**
```bash
# Apply migration (backward compatible, blue can still run)
kubectl apply -f migration-job.yaml -n production
kubectl wait --for=condition=complete job/payment-migration -n production

# Verify migration
kubectl logs job/payment-migration -n production
# Output: Migration completed successfully. 3 tables added, 0 rows migrated.

# Deploy green environment
kubectl apply -f deployment-green-v3.2.0.yaml -n production

# Wait for green to be ready
kubectl wait --for=condition=ready pod \
  -l app=payment-service,version=green \
  -n production --timeout=600s
```

3. **Validate green before switching traffic:**
```bash
# Test green directly (before traffic switch)
kubectl port-forward -n production \
  svc/payment-service-green 8080:80 &

curl http://localhost:8080/health
# Output: {"status": "healthy", "version": "v3.2.0"}

curl -X POST http://localhost:8080/api/v1/payments \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -d '{"method": "new_payment_type", "amount": 100}'
# Success: payment processed

# Kill port-forward
kill %1
```

4. **Switch traffic to green:**
```bash
# Post warning
slack post #deployments "⚠️ Switching payment-service traffic to v3.2.0. Monitoring closely."

# Switch service selector to green
kubectl patch service payment-service -n production \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Traffic now going to green
# Monitor intensively for 15 minutes
```

5. **Monitor and validate:**
```bash
# Check metrics every 2-3 minutes for 15 minutes
# - Error rate: 0.1% (was 0.1%, stable ✓)
# - Latency p95: 150ms (was 145ms, acceptable ✓)
# - Latency p99: 300ms (was 280ms, acceptable ✓)
# - Payment success rate: 99.4% (was 99.5%, within tolerance ✓)
# - New payment method usage: 12 transactions (working ✓)

# Check logs for any errors
kubectl logs -n production -l app=payment-service,version=green \
  --since=15m | grep -i error
# No critical errors found
```

6. **Complete deployment:**
```bash
# After 30 minutes of stable operation, remove blue
kubectl delete deployment payment-service-blue -n production

slack post #deployments "✅ payment-service v3.2.0 fully deployed. New payment methods active. Blue environment cleaned up."
```

**Expected Output:**
```
Blue-Green Deployment Success
- Green version: v3.2.0
- Migration: Completed successfully
- Traffic switch: Seamless (no downtime)
- Validation period: 30 minutes
- Metrics: Stable
- Blue cleanup: Completed
- Total duration: 45 minutes
```

**Outcome:** Complex deployment with database changes completed successfully. New payment methods working. Zero downtime. Blue kept around for 30 minutes as safety net, then cleaned up.

---

### Example 3: Emergency Rollback During Canary

**Context:** Canary deployment detects issues; immediate rollback required.

**Situation:**
- Service: recommendation-engine
- Attempted version: v4.1.0 (canary)
- Stable version: v4.0.3
- Issue: Canary showing 5% error rate vs. 0.5% in stable
- Traffic: Canary at 20% (stable at 80%)

**Steps:**

1. **Detect issue:**
```bash
# Monitoring shows elevated errors in canary
# Error rate: Canary 5.2%, Stable 0.4%
# Decision: Rollback immediately
```

2. **Execute rollback:**
```bash
# Scale down canary to 0
kubectl scale deployment recommendation-engine-canary \
  --replicas=0 -n production

# Verify stable handling 100% traffic
kubectl get deployment -n production
# recommendation-engine: 10/10 ready (stable)
# recommendation-engine-canary: 0/0 ready (scaled down)

# Check error rate
# After 2 minutes: Error rate back to 0.4%
```

3. **Investigate and document:**
```bash
# Collect logs from canary
kubectl logs -n production -l app=recommendation-engine,version=canary \
  --since=30m > canary-failure-logs.txt

# Post incident
slack post #incidents "⚠️ Rollback: recommendation-engine v4.1.0 canary showed 5% error rate. Rolled back to v4.0.3. Investigating."

# Create incident ticket
# Document error patterns, affected requests, timeline
```

4. **Root cause analysis:**
```bash
# Analyze logs
grep "ERROR" canary-failure-logs.txt | head -20
# Pattern: "NullPointerException in UserPreference.getHistory()"

# Finding: New code didn't handle missing user history gracefully
# Fix needed: Add null check before accessing user history
```

**Expected Output:**
```
Rollback Successful
- Detection time: 8 minutes into canary
- Rollback execution: 30 seconds
- Service recovery: 2 minutes
- Affected traffic: ~20% for 8 minutes
- Root cause: Found within 1 hour
- Fix: Deployed v4.1.1 next day after testing
```

**Outcome:** Quick detection and rollback prevented widespread issues. Root cause identified. Proper fix deployed after thorough testing. Canary deployment pattern prevented full-scale incident.

## Troubleshooting

### Issue 1: Deployment Stuck (Pods Not Coming Up)

**Symptoms:**
- `kubectl rollout status` shows "Waiting for deployment rollout to finish"
- Pods show `ImagePullBackOff` or `CrashLoopBackOff`
- Deployment exceeds expected time

**Diagnostic Steps:**
```bash
# Check pod status
kubectl get pods -n production -l app=service-name

# Describe problematic pod
kubectl describe pod <pod-name> -n production

# Check logs
kubectl logs <pod-name> -n production
```

**Common Causes and Solutions:**

**1. Image Pull Error:**
```bash
# Symptom: ImagePullBackOff
# Cause: Wrong image tag or registry auth issue

# Solution: Verify image exists
docker pull your-registry/service-name:version

# Fix: Correct image tag or update registry credentials
kubectl set image deployment/service-name \
  service-name=your-registry/service-name:correct-version \
  -n production
```

**2. Application Crash:**
```bash
# Symptom: CrashLoopBackOff
# Cause: Application error on startup

# Solution: Check application logs
kubectl logs <pod-name> -n production --previous

# Common issues:
# - Missing environment variables
# - Database connection failure
# - Configuration error

# Fix: Update configuration and redeploy
kubectl set env deployment/service-name NEW_VAR=value -n production
```

**3. Resource Constraints:**
```bash
# Symptom: Pods pending, not scheduled
# Cause: Insufficient cluster resources

# Check node resources
kubectl describe nodes | grep -A 5 "Allocated resources"

# Solution: Scale down other services or add nodes
kubectl scale deployment low-priority-service --replicas=2
```

**Prevention:**
- Test deployments in staging with production-like resources
- Monitor cluster capacity
- Set appropriate resource requests/limits

### Issue 2: Elevated Error Rate After Deployment

**Symptoms:**
- Error rate increases from baseline (e.g., 0.5% → 3%)
- Specific endpoints showing errors
- Client-side errors reported

**Diagnostic Steps:**
1. Check which endpoints are affected
2. Review error logs for patterns
3. Compare error types (4xx vs 5xx)
4. Check dependencies (database, APIs, cache)

**Solution:**

**Immediate:**
```bash
# If error rate is critical (>5%), rollback immediately
kubectl rollout undo deployment/service-name -n production

# Monitor for recovery
# If errors persist after rollback, issue may be elsewhere
```

**Investigation:**
```bash
# Analyze error patterns
kubectl logs -n production -l app=service-name \
  --since=30m | grep ERROR | sort | uniq -c | sort -rn

# Common patterns:
# - Dependency timeout: Check downstream services
# - Database errors: Check DB health and connections
# - Validation errors: Check request format changes
```

**Alternative Approaches:**
- If only specific endpoint affected, consider feature flag to disable
- If dependency issue, temporarily use fallback/cache
- If minor increase acceptable, monitor and investigate without rollback

### Issue 3: Database Migration Failure

**Symptoms:**
- Migration job fails or times out
- Application can't connect to database
- Data inconsistency reported

**Quick Fix:**
```bash
# Check migration status
kubectl logs job/migration-name -n production

# Common issues:
# - Lock timeout: Another migration running
# - Syntax error: SQL error in migration
# - Permission denied: Database user lacks permissions
```

**Root Cause Resolution:**

**1. Lock Timeout:**
```bash
# Check for long-running queries
# Connect to database and check pg_stat_activity (Postgres)
kubectl exec -it db-pod -n production -- \
  psql -U app -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Kill blocking query if safe
# Then retry migration
```

**2. Migration Syntax Error:**
```bash
# Review migration SQL
# Test in staging or local environment
# Fix syntax and redeploy migration

# Rollback if migration partially applied
# Run rollback migration script
```

**3. Permission Issues:**
```bash
# Grant necessary permissions
kubectl exec -it db-pod -n production -- \
  psql -U admin -c "GRANT ALL ON SCHEMA public TO app_user;"

# Retry migration
```

**Prevention:**
- Always test migrations in staging first
- Use migration tools with rollback support (Alembic, Flyway)
- Keep migrations backward compatible
- Run migrations before deploying code when possible

## Related Skills

This skill works well with:

- **database-migration**: Detailed database migration procedures and rollback strategies
- **incident-response**: If deployment causes an incident, switch to incident response workflow
- **monitoring-setup**: Setting up comprehensive monitoring for new services

This skill may conflict with:

- **rapid-prototyping**: Prototyping emphasizes speed over safety; don't use both simultaneously

## Integration Notes

### Working with Other Tools

**CI/CD Integration:**
This skill assumes CI/CD has already run tests. For CI/CD setup, reference your platform documentation.

**Monitoring Tools:**
Examples use generic commands. Adapt for your monitoring stack:
- Datadog: Use Datadog API or UI
- Grafana: Open relevant dashboards
- Prometheus: Query metrics directly

**Deployment Tools:**
Examples use kubectl. Adapt for your deployment method:
- Helm: `helm upgrade --install`
- ArgoCD: Update manifests, let ArgoCD sync
- Custom: Follow your deployment scripts

### Skill Composition

**Typical workflow combining multiple skills:**

1. **code-review-checklist**: Review code before merging
2. **integration-testing**: Run tests in staging
3. **deployment-workflow** (this skill): Deploy to production
4. **monitoring-setup**: Configure alerts for new features
5. **incident-response**: If issues arise during deployment

## Notes

### Limitations

- Examples focus on Kubernetes; adapt for other platforms (VMs, serverless, etc.)
- Assumes you have monitoring infrastructure set up
- Database migration details are brief; use database-migration skill for complex scenarios
- Rollback procedures assume stateless services; stateful services require additional considerations

### Assumptions

- You have access to production environment
- Monitoring dashboards are configured
- Staging environment mirrors production
- Team has agreed-upon deployment windows
- Rollback artifacts are retained for reasonable time

## Version History

### Version 1.0.0 (2025-01-20)
- Initial creation
- Core deployment workflow established
- Examples for rolling update, blue-green, and canary deployments
- Comprehensive troubleshooting guide

## Additional Resources

- [Kubernetes Deployments Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Blue-Green Deployment Pattern](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [Canary Deployment Pattern](https://martinfowler.com/bliki/CanaryRelease.html)
- Internal: Company deployment runbooks at [internal wiki]
