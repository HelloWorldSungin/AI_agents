# Issue-as-Requirements Pattern

**Version:** 1.0.0
**Category:** Requirements Pattern
**Purpose:** Standardize task creation with embedded acceptance criteria

---

## Overview

The Issue-as-Requirements Pattern ensures every task contains complete, testable requirements. By embedding acceptance criteria and test steps directly in task definitions, agents have everything needed to implement and verify features without ambiguity.

### Key Insight

> A task without acceptance criteria is a task without a definition of "done."
> Embedded requirements eliminate scope creep and enable autonomous verification.

---

## Problem Statement

Without structured requirements:

1. **Ambiguous Scope**: "Implement login" means different things to different agents
2. **Scope Creep**: Features grow beyond original intent
3. **Incomplete Work**: Tasks marked "done" with missing functionality
4. **Verification Gaps**: No clear way to test if requirements are met
5. **Communication Overhead**: Constant clarification needed

---

## Solution: Structured Task Definition

### Task Structure

Every task must include:

```yaml
task:
  # Identity
  id: "TASK-001"
  title: "Implement user authentication"

  # Classification
  priority: 2        # 1=urgent, 2=high, 3=normal, 4=low
  category: "functional"  # functional, style, infrastructure, testing, bugfix

  # Requirements (IMMUTABLE after creation)
  description: |
    Add JWT-based authentication to the API with login, logout,
    and token refresh capabilities.

  acceptance_criteria:
    - "POST /auth/login accepts email and password"
    - "Valid credentials return JWT token and refresh token"
    - "Invalid credentials return 401 with error message"
    - "JWT token expires after 15 minutes"
    - "Refresh token valid for 7 days"
    - "POST /auth/logout invalidates refresh token"
    - "Protected routes return 401 without valid token"

  test_steps:
    - "POST /auth/login with valid credentials"
    - "Verify response contains access_token and refresh_token"
    - "Use access_token on GET /api/protected"
    - "Verify 200 response with user data"
    - "Wait 15 minutes or manually expire token"
    - "Verify 401 on protected route"
    - "POST /auth/refresh with refresh_token"
    - "Verify new access_token returned"

  # Metadata
  labels: ["auth", "backend", "security"]
  dependencies: ["TASK-000"]  # Setup task must complete first
  estimated_complexity: "medium"  # low, medium, high
```

---

## Acceptance Criteria Guidelines

### Writing Good Criteria

**DO:**

```yaml
acceptance_criteria:
  # Specific and testable
  - "Login form has email input with type='email'"
  - "Password field masks input"
  - "Submit button disabled until both fields valid"
  - "Error message appears below form on 401 response"
  - "Success redirects to /dashboard within 2 seconds"
```

**DON'T:**

```yaml
acceptance_criteria:
  # Vague and untestable
  - "Login works"
  - "Good user experience"
  - "Handles errors properly"
  - "Fast performance"
```

### Criteria Checklist

For each criterion, ensure it is:

- [ ] **Specific**: One clear condition, not multiple
- [ ] **Measurable**: Can be objectively verified
- [ ] **Achievable**: Within scope of this task
- [ ] **Relevant**: Directly supports the feature
- [ ] **Testable**: Can write an automated test for it

### Categories of Criteria

```yaml
acceptance_criteria:
  # Functional - What it does
  - "User can submit form"
  - "Data saves to database"

  # Visual - What it looks like
  - "Button has blue background (#0066CC)"
  - "Error text is red and 14px"

  # Performance - How fast it is
  - "Page loads in under 2 seconds"
  - "API responds in under 200ms"

  # Accessibility - Who can use it
  - "Form navigable by keyboard"
  - "Labels associated with inputs"

  # Security - What it prevents
  - "Passwords never logged"
  - "CSRF token required"

  # Edge Cases - What happens when...
  - "Empty form shows validation errors"
  - "Network error shows retry option"
```

---

## Test Steps Guidelines

### Writing Good Test Steps

```yaml
test_steps:
  # Clear, ordered, actionable
  - step: 1
    action: "Navigate to /login"
    expected: "Login form displayed"

  - step: 2
    action: "Enter 'test@example.com' in email field"
    expected: "Email field shows entered text"

  - step: 3
    action: "Enter 'password123' in password field"
    expected: "Password field shows masked text"

  - step: 4
    action: "Click 'Sign In' button"
    expected: "Loading spinner appears"

  - step: 5
    action: "Wait for response"
    expected: "Redirect to /dashboard OR error message shown"
```

### Test Step Templates

**UI Interaction:**
```yaml
- action: "Click [element]"
  expected: "[result]"
```

**API Request:**
```yaml
- action: "POST /api/[endpoint] with {payload}"
  expected: "[status code] with {response shape}"
```

**Verification:**
```yaml
- action: "Verify [condition]"
  expected: "[specific state]"
```

---

## Immutability Rule

### Why Immutable?

Once created, task requirements **MUST NOT change**. This prevents:

- Scope creep during implementation
- Moving goalposts
- Disputed completion status
- Lost context for future sessions

### What Can Change

| Property | Mutable? | Notes |
|----------|----------|-------|
| title | No | Original title preserved |
| description | No | Original description preserved |
| acceptance_criteria | No | Add new task for new requirements |
| test_steps | No | Original steps preserved |
| priority | Yes | Can be reprioritized |
| status | Yes | Updated as work progresses |
| labels | Yes | Can add/remove labels |
| assigned_to | Yes | Can reassign |
| comments | Yes (append only) | Can add clarifications |

### Handling Scope Changes

If requirements need to change:

1. **Don't modify original task**
2. Create new task with updated requirements
3. Link to original: "Supersedes TASK-001"
4. Close original as "Superseded"

```yaml
task:
  id: "TASK-002"
  title: "Implement user authentication (revised)"
  description: |
    Supersedes TASK-001.

    Updated requirements based on security review:
    - Added MFA requirement
    - Changed token expiry

  # New acceptance criteria
  acceptance_criteria:
    - "All original TASK-001 criteria"
    - "MFA option during login"
    - "JWT expires in 5 minutes (was 15)"
```

---

## Progress Tracking

### Criteria Checkboxes

Track progress by checking off criteria:

```markdown
## Acceptance Criteria

- [x] POST /auth/login accepts email and password
- [x] Valid credentials return JWT token and refresh token
- [ ] Invalid credentials return 401 with error message
- [ ] JWT token expires after 15 minutes
- [ ] Refresh token valid for 7 days
- [ ] POST /auth/logout invalidates refresh token
- [ ] Protected routes return 401 without valid token

Progress: 2/7 (29%)
```

### Completion Requirements

Task can only be marked "Done" when:

1. **All** acceptance criteria checked
2. **All** test steps pass
3. Regression tests pass
4. Visual verification (if UI task)

---

## Integration

### Task Creation Command

```bash
/create-task "Implement password reset"
```

Creates structured task interactively:

```
Creating task: Implement password reset

Category? [functional/style/infrastructure/testing/bugfix]: functional
Priority? [1-4]: 2

Enter acceptance criteria (empty line to finish):
> User can request password reset via email
> Reset link sent to registered email
> Reset link expires after 24 hours
> New password must meet complexity requirements
> Success message after password update
>

Enter test steps (empty line to finish):
> Navigate to /forgot-password
> Enter registered email
> Click "Send Reset Link"
> Check email for reset link
> Click link and enter new password
> Verify login with new password works
>

Labels (comma-separated): auth, security, email

Task TASK-045 created.
```

### With State Provider

```python
provider.create_task({
    "title": "Implement password reset",
    "priority": 2,
    "category": "functional",
    "description": "Password reset flow with email verification",
    "acceptance_criteria": [
        "User can request password reset via email",
        "Reset link sent to registered email",
        "Reset link expires after 24 hours",
        "New password must meet complexity requirements",
        "Success message after password update"
    ],
    "test_steps": [
        "Navigate to /forgot-password",
        "Enter registered email",
        "Click 'Send Reset Link'",
        "Check email for reset link",
        "Click link and enter new password",
        "Verify login with new password works"
    ],
    "labels": ["auth", "security", "email"]
})
```

---

## Templates

### Functional Feature Template

```yaml
task:
  title: "Implement [feature name]"
  priority: 3
  category: "functional"
  description: |
    [Brief description of feature and why it's needed]

  acceptance_criteria:
    - "[Primary function works]"
    - "[Secondary function works]"
    - "[Error handling works]"
    - "[Edge case handled]"

  test_steps:
    - "Navigate to [location]"
    - "Perform [action]"
    - "Verify [result]"
    - "Test [error case]"
    - "Verify [error handling]"

  labels: ["feature"]
```

### Bug Fix Template

```yaml
task:
  title: "Fix: [bug description]"
  priority: 2
  category: "bugfix"
  description: |
    ## Bug Report
    [What's happening]

    ## Expected Behavior
    [What should happen]

    ## Steps to Reproduce
    [How to trigger the bug]

    ## Root Cause
    [If known]

  acceptance_criteria:
    - "Bug no longer reproducible"
    - "Original functionality preserved"
    - "Regression test added"

  test_steps:
    - "Follow original repro steps"
    - "Verify bug no longer occurs"
    - "Verify related functionality unaffected"
    - "Run regression suite"

  labels: ["bugfix"]
```

### Style/UI Template

```yaml
task:
  title: "Style: [component/feature]"
  priority: 3
  category: "style"
  description: |
    [What needs styling and design requirements]

  acceptance_criteria:
    - "[Visual requirement 1 with specifics]"
    - "[Visual requirement 2 with specifics]"
    - "[Responsive requirement]"
    - "[Accessibility requirement]"

  test_steps:
    - "View on desktop (1920x1080)"
    - "View on tablet (768x1024)"
    - "View on mobile (375x667)"
    - "Test keyboard navigation"
    - "Verify contrast ratios"

  visual_verification:
    - "Desktop screenshot"
    - "Mobile screenshot"
    - "Before/after comparison"

  labels: ["style", "ui"]
```

---

## Validation

### Schema Validation

```json
{
  "type": "object",
  "required": ["title", "priority", "category", "acceptance_criteria"],
  "properties": {
    "title": {
      "type": "string",
      "minLength": 10,
      "maxLength": 100
    },
    "priority": {
      "type": "integer",
      "minimum": 1,
      "maximum": 4
    },
    "category": {
      "type": "string",
      "enum": ["functional", "style", "infrastructure", "testing", "bugfix"]
    },
    "acceptance_criteria": {
      "type": "array",
      "minItems": 1,
      "items": { "type": "string", "minLength": 10 }
    },
    "test_steps": {
      "type": "array",
      "items": { "type": "string", "minLength": 5 }
    }
  }
}
```

### Validation Checks

```python
def validate_task(task):
    errors = []

    # Must have acceptance criteria
    if not task.acceptance_criteria:
        errors.append("Task must have at least one acceptance criterion")

    # Criteria must be specific
    vague_terms = ["properly", "correctly", "good", "works"]
    for criterion in task.acceptance_criteria:
        for term in vague_terms:
            if term in criterion.lower():
                errors.append(f"Criterion too vague: '{criterion}'")

    # Should have test steps
    if not task.test_steps:
        errors.append("Task should have test steps (warning)")

    # UI tasks need visual verification
    if task.category in ["style", "frontend"]:
        if not task.visual_verification:
            errors.append("UI task requires visual verification criteria")

    return errors
```

---

## Version History

- **1.0.0** (2024-01-15): Initial issue-as-requirements pattern
