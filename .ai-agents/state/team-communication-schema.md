# Team Communication JSON Schema

## Overview

This file defines the structure of `team-communication.json` used for inter-agent communication.

## Schema

### Base Structure

```json
{
  "manager_instructions": { ... },
  "agent_updates": [ ... ],
  "infrastructure_status": { ... },
  "integration_requests": { ... },
  "scrum_master_updates": { ... }  // NEW: Optional
}
```

### scrum_master_updates Section (NEW - Optional)

**When enabled:** Scrum Master agent is active and tracking project

```json
{
  "scrum_master_updates": {
    "tracking_status": "inactive" | "setup" | "active",
    "appflowy_workspace_url": "http://appflowy.local/workspace/123",
    "appflowy_database_id": "db-456",
    "last_sync": "2025-11-22T15:30:00Z",
    
    "daily_summary": {
      "date": "2025-11-22",
      "completed_today": ["TASK-001", "TASK-002"],
      "in_progress": ["TASK-003"],
      "blocked": ["TASK-005"],
      "velocity": 2.5
    },
    
    "sprint_metrics": {
      "sprint_id": "SPRINT-2025-11-01",
      "start_date": "2025-11-20",
      "end_date": "2025-11-27",
      "total_tasks": 10,
      "completed": 7,
      "in_progress": 2,
      "blocked": 1,
      "average_velocity": 2.5
    },
    
    "blocker_escalations": [
      {
        "task_id": "TASK-005",
        "blocker": "Waiting for API credentials",
        "reported_by": "frontend-dev",
        "reported_at": "2025-11-22T14:00:00Z",
        "escalated_to": "manager",
        "status": "pending"
      }
    ]
  }
}
```

### Field Descriptions

**tracking_status:**
- `inactive`: Scrum Master not enabled
- `setup`: Scrum Master configuring AppFlowy
- `active`: Scrum Master actively tracking

**daily_summary:**
- Updated daily by Scrum Master
- Shows completed, in-progress, and blocked tasks
- Includes velocity calculation

**sprint_metrics:**
- Overall sprint progress
- Velocity tracking
- Completion percentages

**blocker_escalations:**
- Tasks that are blocked
- Who reported the blocker
- Escalation status

## Example: Full team-communication.json with Scrum Master

```json
{
  "manager_instructions": {
    "current_focus": "User authentication feature",
    "active_tasks": [
      {
        "task_id": "TASK-001",
        "assigned_to": "backend-dev",
        "description": "Implement JWT authentication API",
        "priority": "high",
        "branch": "feature/auth-api",
        "appflowy_task_id": "af-12345"
      }
    ],
    "scrum_master_enabled": true,
    "appflowy_workspace_url": "http://appflowy.local/workspace/auth-feature"
  },
  
  "agent_updates": [
    {
      "agent_id": "backend-dev",
      "task_id": "TASK-001",
      "status": "completed",
      "timestamp": "2025-11-22T15:30:00Z",
      "test_summary": "24 tests passed",
      "branch": "feature/auth-api"
    }
  ],
  
  "scrum_master_updates": {
    "tracking_status": "active",
    "appflowy_workspace_url": "http://appflowy.local/workspace/auth-feature",
    "appflowy_database_id": "db-auth-123",
    "last_sync": "2025-11-22T15:35:00Z",
    
    "daily_summary": {
      "date": "2025-11-22",
      "completed_today": ["TASK-001"],
      "in_progress": ["TASK-002"],
      "blocked": [],
      "velocity": 1.0
    },
    
    "sprint_metrics": {
      "sprint_id": "AUTH-SPRINT-001",
      "start_date": "2025-11-20",
      "end_date": "2025-11-27",
      "total_tasks": 5,
      "completed": 1,
      "in_progress": 1,
      "blocked": 0,
      "average_velocity": 1.0
    },
    
    "blocker_escalations": []
  }
}
```

## Usage

### Manager Reading Scrum Master Updates

```python
# Read daily summary
if 'scrum_master_updates' in communication_data:
    summary = communication_data['scrum_master_updates']['daily_summary']
    print(f"Completed: {summary['completed_today']}")
    print(f"Blocked: {summary['blocked']}")
```

### Scrum Master Writing Updates

```python
# Write daily summary
communication_data['scrum_master_updates'] = {
    'tracking_status': 'active',
    'last_sync': datetime.utcnow().isoformat() + 'Z',
    'daily_summary': {
        'date': today,
        'completed_today': completed_tasks,
        'in_progress': active_tasks,
        'blocked': blocked_tasks,
        'velocity': len(completed_tasks) / days_elapsed
    }
}
```

## Backward Compatibility

**Important:** The `scrum_master_updates` section is **optional**.

- If Scrum Master is not enabled, this section may be absent or have `tracking_status: "inactive"`
- All other agents should handle this section being missing
- Manager prompts check `if scrum_master_enabled` before reading this section

---

**Version:** 1.0.0 (2025-11-22)
