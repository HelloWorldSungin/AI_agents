---
name: incident-response
description: Structured incident response workflow for production issues. Use when handling outages, performance degradation, or user-impacting problems. Covers triage, communication, mitigation, resolution, and post-incident review.
version: 1.0.0
author: SRE Team
category: custom
token_estimate: ~3500
---

<objective>
This skill provides a structured approach to handling production incidents efficiently and effectively. It ensures consistent response, clear communication, proper escalation, and thorough documentation for learning and prevention.
</objective>

<when_to_use>
Use this skill when:

- Production outage or severe degradation detected
- Users reporting inability to access system
- Error rates spike significantly
- Critical functionality is broken
- Security incident detected
- Data integrity issues discovered

Do NOT use this skill when:

- Minor bugs in non-critical features (use bug fix workflow)
- Planned maintenance (use deployment workflow)
- Development environment issues
- User support questions (use support workflow)
</when_to_use>

<prerequisites>
- Access to monitoring dashboards
- Communication channels set up (Slack, PagerDuty, etc.)
- Incident tracking system (Jira, GitHub Issues, etc.)
- On-call rotation defined
- Rollback procedures documented
- Status page access (if applicable)
</prerequisites>

<workflow>
<step name="Detect and Acknowledge">
Recognize incident and take ownership:

**Detection Sources:**
- Monitoring alerts (PagerDuty, Datadog, etc.)
- User reports (support tickets, social media)
- Team member observation
- Automated health checks

**Acknowledge Incident:**
```bash
# Acknowledge alert in PagerDuty/monitoring system
# This stops alert escalation

# Post in incident channel
slack post #incidents "🚨 INCIDENT: [Brief description]
Status: Acknowledged
Severity: [P0/P1/P2/P3]
Owner: @your-name
Time: $(date)"
```

**Initial Assessment (< 2 minutes):**
- What is broken? (Symptom)
- How many users affected? (Scope)
- Is it getting worse? (Trend)
- Quick severity classification

**Severity Levels:**

**P0 - Critical:**
- Complete outage
- All users unable to access system
- Data loss occurring
- Security breach active
- **Response Time:** Immediate
- **Communication:** Every 15 minutes
- **Escalation:** Immediate to leadership

**P1 - High:**
- Major functionality broken
- Significant user impact (>20%)
- Severe performance degradation
- **Response Time:** < 15 minutes
- **Communication:** Every 30 minutes
- **Escalation:** Within 1 hour if not resolving

**P2 - Medium:**
- Partial functionality impaired
- Limited user impact (<20%)
- Non-critical feature broken
- **Response Time:** < 1 hour
- **Communication:** Hourly updates
- **Escalation:** If no progress in 4 hours

**P3 - Low:**
- Minor issue
- Minimal user impact
- Workaround available
- **Response Time:** Best effort
- **Communication:** At resolution
- **Escalation:** Not needed
</step>

<step name="Initial Communication">
Inform stakeholders and establish communication rhythm:

**Internal Communication (Slack):**
```markdown
# Post in #incidents channel
🚨 **INCIDENT [INC-2025-0120-001]**

**Status:** Investigating
**Severity:** P1 - High
**Impact:** User authentication failing, ~30% of login attempts failing
**Started:** 2025-01-20 10:30 UTC
**Owner:** @jane.doe
**War Room:** #incident-2025-0120

**Current Actions:**
- Checking auth service logs
- Reviewing recent deployments
- Monitoring error rates

**Next Update:** 11:00 UTC (30 minutes)

**How to Help:**
- Join #incident-2025-0120 if you have context on auth service
- Please avoid deploying non-critical changes until resolved
```

**External Communication (Status Page):**
```markdown
# If customer-facing
Title: Login Issues - Investigating

We are investigating reports of login failures affecting some users.
Our team is actively working to resolve this issue.

Last Updated: 2025-01-20 10:35 UTC
Status: Investigating
```

**Communication Checklist:**
- [ ] Incident channel created (#incident-YYYYMMDD)
- [ ] Initial message posted with severity and impact
- [ ] Status page updated (if external impact)
- [ ] Leadership notified (P0/P1)
- [ ] Update cadence established
</step>

<step name="Investigate and Diagnose">
Identify root cause systematically:

**Gather Information:**

**Check Recent Changes:**
```bash
# Recent deployments
kubectl rollout history deployment/auth-service -n production

# Recent commits
git log --oneline --since="2 hours ago" main

# Recent configuration changes
kubectl diff -f k8s/production/
```

**Check Logs:**
```bash
# Application logs
kubectl logs -n production -l app=auth-service \
  --since=30m | grep -i error | tail -100

# Look for patterns
kubectl logs -n production -l app=auth-service \
  --since=30m | grep -i "authentication failed" | wc -l
```

**Check Metrics:**
```bash
# Error rate
# Open Datadog/Grafana dashboard
# Check: error rate, latency, throughput

# Database connection issues?
# Check: DB connection count, query times

# External dependency issues?
# Check: API response times from dependencies
```

**Check Infrastructure:**
```bash
# Service health
kubectl get pods -n production -l app=auth-service

# Resource usage
kubectl top pods -n production -l app=auth-service

# Node health
kubectl get nodes
kubectl top nodes
```

**Common Investigation Questions:**
- When did it start? (Correlate with changes)
- What changed recently? (Code, config, infrastructure)
- Is it consistent or intermittent? (Pattern)
- Which components are affected? (Scope)
- Are dependencies healthy? (External factors)

**Document Findings:**
```markdown
# Update incident thread with findings

**Investigation Update - 10:45 UTC**

Findings:
- Auth service deployed 10:15 UTC (15 min before incident)
- Error logs show "Database connection timeout"
- Database connection pool exhausted (100/100 used)
- Previous version had max_connections=50, new has 100 but DB max is 100
- Other services also using connections

Root Cause: New auth service version increased connection pool size,
exhausting database connection limit when combined with other services.

Mitigation Plan: Rollback auth service to previous version.
```
</step>

<step name="Mitigate and Resolve">
Stop the impact and restore service:

**Mitigation Strategies (choose based on situation):**

**1. Rollback Deployment:**
```bash
# Quick fix: revert to previous working version
kubectl rollout undo deployment/auth-service -n production

# Monitor rollback
kubectl rollout status deployment/auth-service -n production

# Verify fix
curl https://api.example.com/auth/health
# Check error rate in monitoring (should decrease)
```

**2. Scale Resources:**
```bash
# If resource exhaustion
kubectl scale deployment/auth-service --replicas=10 -n production

# If database connections
# Temporarily increase DB connection limit (if safe)
psql $DATABASE_URL -c "ALTER SYSTEM SET max_connections = 150;"
psql $DATABASE_URL -c "SELECT pg_reload_conf();"
```

**3. Disable Feature:**
```bash
# If specific feature causing issues
# Use feature flag to disable
curl -X POST https://api.example.com/admin/feature-flags \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"flag": "new_auth_flow", "enabled": false}'
```

**4. Failover:**
```bash
# Switch to backup/redundant system
kubectl patch service auth-service -n production \
  -p '{"spec":{"selector":{"version":"backup"}}}'
```

**5. Clear/Reset State:**
```bash
# If cache corruption
redis-cli FLUSHDB

# If queue backup
# Drain problematic queue
```

**Verification After Mitigation:**
```bash
# Check error rate returned to normal
# Monitor for 5-10 minutes

# Verify key user flows
pytest tests/smoke/auth_flow.py --env=production

# Check user reports
# Monitor support channels for confirmations
```

**Communication After Resolution:**
```markdown
# Update incident channel
✅ **INCIDENT RESOLVED [INC-2025-0120-001]**

**Status:** Resolved
**Resolution:** Rolled back auth-service deployment
**Duration:** 35 minutes (10:30 - 11:05 UTC)
**Impact:** ~30% of login attempts failed during incident

**Root Cause:** Database connection pool exhaustion due to
misconfigured connection limits in new deployment.

**Next Steps:**
- Post-incident review scheduled
- Fix will be re-deployed with correct connection limits
- Monitoring alert added for DB connection saturation

Thanks to @john, @sarah for help investigating!
```
</step>

<step name="Post-Incident Review">
Learn from incident and prevent recurrence:

**Schedule Review (within 48 hours):**
```markdown
# Create meeting invite
Subject: Incident Review - INC-2025-0120-001 (Auth Service Outage)
When: 2025-01-22 2:00 PM
Who: Incident responders, service owners, leadership (for P0/P1)
Agenda:
- Timeline review
- Root cause analysis
- What went well
- What could be improved
- Action items
```

**Incident Report Template:**
```markdown
# Incident Report: INC-2025-0120-001

## Summary
On Jan 20, 2025 at 10:30 UTC, authentication service experienced high
failure rates (~30%) for 35 minutes due to database connection exhaustion.

## Impact
- Duration: 35 minutes
- Users Affected: ~30% of login attempts (estimated 1,500 users)
- Revenue Impact: None (no transactions lost)
- Data Impact: None

## Timeline (UTC)
- 10:15 - Auth service v2.1.0 deployed
- 10:30 - First alert: elevated error rate
- 10:32 - Incident declared (P1)
- 10:35 - Investigation started, logs reviewed
- 10:45 - Root cause identified (DB connection exhaustion)
- 10:48 - Rollback initiated
- 10:52 - Rollback completed
- 11:05 - Incident resolved (error rate normal)

## Root Cause
Auth service v2.1.0 increased max_connections from 50 to 100, intending
to improve performance. However, database max_connections was 100, and
other services were already using ~60 connections. When auth service
scaled up during peak traffic, connection pool was exhausted.

## Detection
- Automated alert (PagerDuty) from elevated error rate
- Detection time: 2 minutes after issue started

## Response
- Time to acknowledge: 2 minutes
- Time to mitigation: 22 minutes
- Total incident duration: 35 minutes

## What Went Well
✅ Quick detection via monitoring
✅ Clear ownership and communication
✅ Effective rollback procedure
✅ Cross-team collaboration

## What Could Be Improved
⚠️ Configuration change wasn't validated against DB limits
⚠️ Staging environment didn't catch this (different DB config)
⚠️ No alerting on DB connection saturation

## Action Items

| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| Add DB connection saturation alert | @sarah | 2025-01-25 | P0 |
| Update deployment checklist with dependency resource checks | @jane | 2025-01-27 | P1 |
| Align staging DB configuration with production | @john | 2025-02-01 | P1 |
| Document connection pool sizing guidelines | @maria | 2025-02-03 | P2 |
| Review all service connection pool configurations | @team | 2025-02-10 | P2 |

## Lessons Learned
1. Always consider resource limits of dependencies when scaling
2. Staging should match production configuration for realistic testing
3. Monitoring should cover resource saturation, not just errors
4. Quick rollback capability is critical for rapid mitigation
```

**Follow-Up:**
- Track action items to completion
- Update runbooks with lessons learned
- Share incident report with team
- Celebrate what went well, learn from what didn't
</step>
</workflow>

<best_practices>
<practice name="Communicate Early and Often">
**Rationale:** Reduces uncertainty and enables help from others.

**Implementation:** Post updates even if no new information ("Still investigating, checking X next").
</practice>

<practice name="Focus on Mitigation First, Root Cause Second">
**Rationale:** Stopping user impact is priority; understanding why can wait.

**Implementation:** Once incident is contained, you can thoroughly investigate.
</practice>

<practice name="Document Everything in Real-Time">
**Rationale:** Memory fades; contemporaneous notes are accurate.

**Implementation:** Timestamp all actions, findings, and decisions during incident.
</practice>

<practice name="Blameless Post-Mortems">
**Rationale:** Focus on system improvements, not individual blame.

**Implementation:** Use "we" not "they"; focus on process gaps, not people.
</practice>

<practice name="Degree of Freedom">
**Low Freedom**: Incident response requires following established procedures for consistency and efficiency. Communication cadence, severity classification, and post-incident review are critical.
</practice>

<practice name="Token Efficiency">
This skill uses approximately **3,500 tokens** when fully loaded.
</practice>
</best_practices>

<common_pitfalls>
<pitfall name="Jumping to Solutions Without Understanding">
**What Happens:** Apply fixes that don't address root cause, potentially making things worse.

**How to Avoid:**
- Gather information before acting
- Verify hypothesis before implementing fix
- For P0, quick mitigation (rollback) then investigate
</pitfall>

<pitfall name="Poor Communication">
**What Happens:** Stakeholders unaware of status, multiple people investigating same thing, confusion.

**How to Avoid:**
- Establish single source of truth (incident channel)
- Regular updates even if no progress
- Clear ownership (incident commander)
</pitfall>

<pitfall name="Skipping Post-Incident Review">
**What Happens:** Same incident repeats; lessons not learned.

**How to Avoid:**
- Schedule review immediately after resolution
- Track action items to completion
- Share learnings with broader team
</pitfall>
</common_pitfalls>

<examples>
<example name="Database Deadlock Incident">
**Detection (14:30):**
```markdown
🚨 INCIDENT - API timeouts
Severity: P1
Impact: 15% of API requests timing out
Owner: @alex
```

**Investigation (14:35):**
```bash
# Check logs
kubectl logs -l app=api --since=10m | grep timeout

# Finding: Database query timeouts
# Check database
psql -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
# Multiple queries waiting on locks
```

**Mitigation (14:42):**
```bash
# Identify blocking query
psql -c "SELECT pid, query FROM pg_stat_activity WHERE wait_event_type = 'Lock';"

# Kill blocking query (after confirming safe)
psql -c "SELECT pg_terminate_backend(12345);"

# Verify resolution
# API timeout rate drops to normal
```

**Resolution (14:45):**
```markdown
✅ RESOLVED
Duration: 15 minutes
Cause: Long-running report query blocked production transactions
Fix: Killed query, added statement timeout for reports
```

**Outcome:** Quick resolution. Follow-up: separate read-replica for reports.
</example>

<example name="Service Outage Due to Configuration">
**Detection (09:15):**
```markdown
🚨 INCIDENT - Complete service outage
Severity: P0
Impact: All users unable to access application (404 errors)
Owner: @sam
```

**Initial Assessment (09:17):**
```bash
# Check service
kubectl get pods -n production
# All pods showing CrashLoopBackOff

# Check recent changes
git log --oneline --since="1 hour ago"
# Recent commit: "Update service configuration"
```

**Investigation (09:20):**
```bash
# Check pod logs
kubectl logs pod/app-7d5f8-xyz -n production
# Error: "Failed to parse config: invalid YAML at line 23"

# Check configuration
kubectl get configmap app-config -o yaml
# Syntax error: missing closing quote on line 23
```

**Mitigation (09:22):**
```bash
# Fix configuration
kubectl edit configmap app-config -n production
# Fix syntax error, save

# Restart pods
kubectl rollout restart deployment/app -n production

# Wait for pods to come up
kubectl wait --for=condition=ready pod -l app=app -n production --timeout=300s
```

**Verification (09:27):**
```bash
# Check application
curl https://api.example.com/health
# ✅ Returns 200 OK

# Check monitoring
# Error rate back to 0%
```

**Resolution (09:30):**
```markdown
✅ RESOLVED
Duration: 15 minutes (complete outage)
Cause: Invalid YAML in configuration file
Fix: Corrected syntax error, restarted pods
Action Items:
- Add YAML validation to CI/CD
- Add config validation tests
- Review config change process
```

**Outcome:** Fast resolution due to good logging and quick config fix. CI improved to prevent similar issues.
</example>
</examples>

<related_skills>
- **deployment-workflow**: Coordinate with deployment procedures
- **database-migration**: Handle database-related incidents
- **monitoring-setup**: Effective monitoring prevents/detects incidents
</related_skills>

<communication_templates>
<template name="Initial Incident Declaration">
```markdown
🚨 **INCIDENT [INC-YYYY-MMDD-NNN]**

**Status:** Investigating
**Severity:** [P0/P1/P2/P3] - [Critical/High/Medium/Low]
**Impact:** [Brief description of user impact]
**Started:** [Timestamp UTC]
**Owner:** @[name]
**War Room:** #incident-YYYYMMDD

**Current Actions:**
- [Action 1]
- [Action 2]

**Next Update:** [Timestamp]
```
</template>

<template name="Status Update">
```markdown
**UPDATE [HH:MM UTC] - [INC-YYYY-MMDD-NNN]**

**Status:** [Still investigating / Mitigation in progress / Resolved]

**Progress:**
- [Finding 1]
- [Action taken 1]

**Current Focus:**
- [What we're doing now]

**Next Update:** [Timestamp]
```
</template>

<template name="Resolution Message">
```markdown
✅ **INCIDENT RESOLVED [INC-YYYY-MMDD-NNN]**

**Status:** Resolved
**Resolution:** [What fixed it]
**Duration:** [X minutes/hours]
**Impact:** [Summary of impact]

**Root Cause:** [Brief explanation]

**Next Steps:**
- [Post-incident review scheduled]
- [Follow-up actions]

Thanks to [@names] for help resolving!
```
</template>
</communication_templates>

<version_history>
**Version 1.0.0 (2025-01-20)**
- Initial creation
- Structured incident response workflow
- Communication templates
- Post-incident review process
</version_history>

<additional_resources>
- [Google SRE Book - Incident Management](https://sre.google/sre-book/managing-incidents/)
- [PagerDuty Incident Response Guide](https://response.pagerduty.com/)
- Internal: Incident Response Runbook at [internal wiki]
- Internal: On-Call Rotation at [internal wiki]
</additional_resources>
