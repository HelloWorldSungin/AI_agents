---
name: code-review-checklist
description: Comprehensive code review checklist following team standards. Use when reviewing pull requests or preparing code for review. Covers code quality, security, performance, testing, and documentation requirements.
version: 1.0.0
author: Engineering Team
category: custom
token_estimate: ~2800
---

# Code Review Checklist Skill

## Purpose

This skill provides a systematic checklist for conducting thorough code reviews that maintain high code quality, security, and maintainability standards. It ensures consistency across reviewers and helps catch common issues before code reaches production.

## When to Use This Skill

Use this skill when:

- Reviewing a pull request
- Preparing your own code for review (self-review)
- Conducting a security review of code changes
- Auditing code quality for a feature branch
- Training new team members on review standards

Do NOT use this skill when:

- Doing high-level architecture review (use architecture review skill)
- Reviewing configuration-only changes (use simpler config review)
- Emergency hotfixes (use abbreviated critical-path review)

## Prerequisites

Before using this skill, ensure:

- Pull request is created with clear description
- CI/CD pipeline has run and results are available
- Code changes are reasonably sized (< 500 lines preferred)
- Sufficient context is provided in PR description
- Related issues or tickets are linked

## Instructions

### Step 1: Understand the Context

Before diving into code, understand what and why:

**Review PR Description:**
```bash
# Fetch PR details
gh pr view <pr-number>

# Check linked issues
gh issue view <issue-number>
```

**Understand the change:**
- What problem does this solve?
- What approach was taken?
- Are there alternative approaches?
- What's the expected behavior?
- What edge cases should be handled?

**Check CI/CD results:**
```bash
# View check status
gh pr checks <pr-number>

# Review test results
# All checks should be passing before detailed review
```

### Step 2: Code Quality Review

Review code for readability, maintainability, and best practices:

**Readability:**
- [ ] Code is easy to understand without excessive comments
- [ ] Variable and function names are descriptive and clear
- [ ] Functions are focused and do one thing well
- [ ] Code follows team style guide (linting passes)
- [ ] Complex logic has explanatory comments
- [ ] No commented-out code (remove or explain)

**Structure:**
- [ ] Code is properly organized into logical modules/classes
- [ ] No circular dependencies
- [ ] Appropriate use of design patterns
- [ ] DRY principle followed (no unnecessary duplication)
- [ ] Proper separation of concerns

**Error Handling:**
- [ ] Errors are caught and handled appropriately
- [ ] Error messages are helpful and actionable
- [ ] No silent failures or swallowed exceptions
- [ ] Edge cases are handled
- [ ] Proper use of exceptions vs. error returns

**Example Quality Check:**
```python
# Bad: Unclear, poor error handling
def p(u):
    r = requests.get(u)
    return r.json()['data']

# Good: Clear, with error handling
def fetch_user_profile(user_id: str) -> dict:
    """Fetch user profile from API.

    Args:
        user_id: Unique identifier for the user

    Returns:
        User profile dictionary

    Raises:
        UserNotFoundError: If user doesn't exist
        APIError: If API request fails
    """
    try:
        response = requests.get(f"{API_BASE}/users/{user_id}")
        response.raise_for_status()
        return response.json()['data']
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise UserNotFoundError(f"User {user_id} not found")
        raise APIError(f"Failed to fetch user profile: {e}")
```

### Step 3: Security Review

Check for common security vulnerabilities:

**Authentication & Authorization:**
- [ ] Proper authentication checks before sensitive operations
- [ ] Authorization verified (user can access this resource)
- [ ] No hardcoded credentials or secrets
- [ ] API tokens/keys loaded from environment or secrets manager
- [ ] Session management is secure (if applicable)

**Input Validation:**
- [ ] All user input is validated
- [ ] Proper sanitization to prevent injection attacks
- [ ] Type checking for expected input types
- [ ] Size limits on input data
- [ ] No SQL injection vulnerabilities (use parameterized queries)

**Data Protection:**
- [ ] Sensitive data (PII, passwords) is encrypted at rest and in transit
- [ ] No sensitive data in logs
- [ ] Proper access controls on data
- [ ] PII is handled according to privacy policy
- [ ] Passwords are hashed (bcrypt, argon2), never stored plaintext

**Common Vulnerabilities:**
- [ ] No XSS vulnerabilities (proper output encoding)
- [ ] No CSRF vulnerabilities (proper token validation)
- [ ] No path traversal vulnerabilities
- [ ] No command injection vulnerabilities
- [ ] Dependencies are up-to-date (no known CVEs)

**Security Checklist Example:**
```python
# Bad: SQL injection vulnerability
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# Good: Parameterized query
def get_user(username: str) -> Optional[User]:
    query = "SELECT * FROM users WHERE username = ?"
    result = db.execute(query, (username,))
    return User.from_db(result) if result else None

# Bad: Sensitive data in logs
logger.info(f"User logged in: {user.email}, password: {user.password}")

# Good: No sensitive data in logs
logger.info(f"User logged in: user_id={user.id}")
```

### Step 4: Performance Review

Assess performance implications:

**Efficiency:**
- [ ] No unnecessary database queries (N+1 problem avoided)
- [ ] Proper indexing for database queries
- [ ] Efficient algorithms (appropriate time/space complexity)
- [ ] No unnecessary loops or iterations
- [ ] Caching used where appropriate

**Scalability:**
- [ ] Code will scale with increased load
- [ ] No unbounded resource usage (memory leaks, file handles)
- [ ] Proper pagination for large datasets
- [ ] Async operations where appropriate
- [ ] No blocking operations in critical paths

**Resource Usage:**
- [ ] Memory usage is reasonable
- [ ] No excessive CPU usage
- [ ] File handles and connections properly closed
- [ ] No resource leaks

**Performance Example:**
```python
# Bad: N+1 query problem
def get_users_with_posts():
    users = User.query.all()
    for user in users:
        user.posts = Post.query.filter_by(user_id=user.id).all()  # N queries!
    return users

# Good: Single query with join
def get_users_with_posts():
    return User.query.options(joinedload(User.posts)).all()

# Bad: Loading entire dataset into memory
def process_all_records():
    records = Record.query.all()  # Could be millions!
    for record in records:
        process(record)

# Good: Batch processing
def process_all_records():
    batch_size = 1000
    offset = 0
    while True:
        records = Record.query.limit(batch_size).offset(offset).all()
        if not records:
            break
        for record in records:
            process(record)
        offset += batch_size
```

### Step 5: Testing Review

Verify adequate test coverage and quality:

**Test Coverage:**
- [ ] New code has unit tests
- [ ] Critical paths have integration tests
- [ ] Edge cases are tested
- [ ] Error conditions are tested
- [ ] Test coverage meets team threshold (e.g., 80%)

**Test Quality:**
- [ ] Tests are readable and well-named
- [ ] Tests are independent (no test interdependencies)
- [ ] Tests use appropriate assertions
- [ ] No flaky tests
- [ ] Tests run quickly (< 1s for unit tests)

**Test Organization:**
```bash
# Check test coverage
pytest --cov=myapp --cov-report=html tests/

# Review coverage report
open htmlcov/index.html

# Look for:
# - Uncovered critical paths
# - Missing edge case tests
# - Low coverage modules
```

**Test Example:**
```python
# Good test: Clear name, arrange-act-assert pattern
def test_user_registration_with_valid_data_creates_user():
    # Arrange
    user_data = {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    }

    # Act
    result = register_user(user_data)

    # Assert
    assert result.success is True
    assert result.user.email == "test@example.com"
    assert User.query.filter_by(email="test@example.com").first() is not None

# Good test: Edge case
def test_user_registration_with_duplicate_email_returns_error():
    # Arrange
    existing_user = create_user(email="test@example.com")
    new_user_data = {"email": "test@example.com", "password": "pass"}

    # Act
    result = register_user(new_user_data)

    # Assert
    assert result.success is False
    assert "already exists" in result.error_message.lower()
```

### Step 6: Documentation Review

Ensure code is properly documented:

**Code Documentation:**
- [ ] Public APIs have docstrings
- [ ] Complex logic has explanatory comments
- [ ] TODO/FIXME comments have issue references
- [ ] No outdated comments
- [ ] Function signatures are clear (type hints in Python)

**External Documentation:**
- [ ] README updated if public interface changed
- [ ] API documentation updated (OpenAPI, etc.)
- [ ] Migration guide provided for breaking changes
- [ ] Architecture diagrams updated if structure changed
- [ ] Changelog/release notes entry added

**Documentation Example:**
```python
# Good: Comprehensive docstring
def calculate_user_score(
    user: User,
    time_period: timedelta,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Calculate weighted activity score for a user.

    Score is based on various user activities weighted by importance.
    Higher scores indicate more engaged users.

    Args:
        user: User object to calculate score for
        time_period: How far back to look for activities
        weights: Optional custom weights for each activity type.
                 Defaults to standard weights if not provided.

    Returns:
        Float between 0.0 and 100.0 representing user engagement score

    Raises:
        ValueError: If time_period is negative

    Example:
        >>> user = User.get(123)
        >>> score = calculate_user_score(user, timedelta(days=30))
        >>> print(f"User engagement score: {score:.2f}")
        User engagement score: 78.50
    """
    if time_period.total_seconds() < 0:
        raise ValueError("time_period must be positive")

    weights = weights or DEFAULT_WEIGHTS
    # ... implementation
```

### Step 7: Final Checklist and Feedback

Complete final checks and provide constructive feedback:

**Final Checks:**
- [ ] No debugging code left in (print statements, debugger breaks)
- [ ] No temporary files or test data committed
- [ ] Dependencies properly declared (requirements.txt, package.json)
- [ ] Configuration files updated if needed
- [ ] No sensitive data in commit history
- [ ] Commit messages are clear and descriptive
- [ ] Branch is up-to-date with main

**Provide Feedback:**

Use constructive, specific feedback:

**Good feedback:**
```markdown
**Security Concern**: Line 45 is vulnerable to SQL injection.
Please use parameterized queries instead of string interpolation.

Example:
```python
# Instead of:
query = f"SELECT * FROM users WHERE id = {user_id}"

# Use:
query = "SELECT * FROM users WHERE id = ?"
db.execute(query, (user_id,))
```

**Performance Issue**: Lines 120-135 have an N+1 query problem.
Consider using `joinedload` to fetch posts in a single query.

**Nice!**: The error handling in `process_payment()` is excellent.
Clear error messages and proper logging.
```

**Poor feedback:**
```markdown
❌ "This is bad"
❌ "Rewrite this"
❌ "I don't like this approach"
```

**Approval Criteria:**

Approve if:
- All critical issues are addressed
- Code meets quality, security, and performance standards
- Adequate test coverage
- Documentation is complete

Request changes if:
- Security vulnerabilities present
- Critical functionality missing tests
- Performance issues that will impact users
- Code quality issues that harm maintainability

## Best Practices

### 1. Review in Small Batches

**Rationale:** Review effectiveness drops significantly for PRs over 400 lines. Cognitive load makes it hard to catch issues in large reviews.

**Implementation:**
- Encourage smaller, focused PRs
- For large PRs, review in multiple sessions
- Request breaking large PRs into smaller ones when feasible

### 2. Use a Checklist Mindset

**Rationale:** Systematic checklists catch more issues than ad-hoc reviews.

**Implementation:**
- Work through each section methodically
- Don't skip sections even if code looks simple
- Use GitHub review features to track progress

### 3. Balance Speed with Thoroughness

**Rationale:** Fast feedback enables team velocity, but thoroughness prevents bugs.

**Implementation:**
- Aim for review within 24 hours
- For urgent fixes, focus on critical path
- For major features, take time for thorough review

### 4. Degree of Freedom

**Medium Freedom**: Core quality and security checks must be performed, but:
- Review depth can vary based on change risk/complexity
- Feedback style can match team culture
- Tools and techniques can be adapted
- Order of checklist items is flexible

### 5. Token Efficiency

This skill uses approximately **2,800 tokens** when fully loaded.

**Optimization Strategy:**
- Core checklist: Always loaded (~1,800 tokens)
- Examples: Load for reference (~800 tokens)
- Detailed security guidelines: Load if security-sensitive code (~200 tokens on-demand)

## Common Pitfalls

### Pitfall 1: Focusing Only on Style

**What Happens:** Review catches formatting issues but misses logic bugs, security flaws, or performance problems.

**Why It Happens:** Style issues are easiest to spot; deeper issues require more analysis.

**How to Avoid:**
1. Use automated linting for style issues
2. Focus review time on logic, security, performance
3. Work through checklist systematically
4. Don't let style issues distract from critical issues

**Recovery:** If approved with issues, create follow-up tickets for missed concerns.

### Pitfall 2: Rubber-Stamp Approval

**What Happens:** Approve PR without thorough review, trusting tests will catch issues.

**Why It Happens:** Time pressure, trust in author, or reviewer fatigue.

**How to Avoid:**
1. Block time for thoughtful review
2. Use checklist to ensure thoroughness
3. If lacking time, ask colleague to review or postpone
4. Remember: reviewer shares responsibility for code quality

**Warning Signs:**
- Approving within minutes of PR creation
- Not asking any questions
- Not running/testing code locally
- Skipping sections of checklist

### Pitfall 3: Overly Critical or Nitpicky

**What Happens:** Review focuses on minor preferences, blocking PRs for subjective style choices.

**Why It Happens:** Different coding preferences, perfectionism, or miscommunication.

**How to Avoid:**
1. Distinguish between "must fix" and "nit/suggestion"
2. Defer style debates to team style guide discussion
3. Focus on objective issues (bugs, security, performance)
4. Praise good decisions, not just critique

**Recovery:** If feedback was too harsh, follow up with positive message acknowledging good aspects.

## Examples

### Example 1: Reviewing a Simple Bug Fix

**Context:** Small PR fixing a null pointer exception in user profile page.

**PR Details:**
- Files changed: 1
- Lines changed: +5, -3
- Description: "Fix NPE when user has no profile picture"

**Review Process:**

1. **Understand context:**
```bash
gh pr view 1234
# Issue: Users without profile pictures get 500 error
# Fix: Add null check before accessing picture URL
```

2. **Quick quality check:**
```python
# Changed code:
def get_profile_picture_url(user):
    if user.profile_picture is None:  # ✓ Good: null check added
        return DEFAULT_AVATAR_URL
    return user.profile_picture.url
```

3. **Security check:**
- No security concerns (simple null check)
- No user input involved

4. **Performance check:**
- No performance impact
- Single attribute access

5. **Testing check:**
```python
# Test added:
def test_user_without_profile_picture_returns_default_avatar():
    user = User(profile_picture=None)
    url = get_profile_picture_url(user)
    assert url == DEFAULT_AVATAR_URL
```
✓ Edge case tested

6. **Documentation check:**
- Code is self-explanatory
- No documentation needed

**Feedback:**
```markdown
LGTM! ✓

Good fix. The null check is clear and the test covers the edge case well.

One suggestion (optional): Consider adding a docstring to clarify when
DEFAULT_AVATAR_URL is returned, for future maintainers.
```

**Outcome:** Approved. Simple, well-tested fix. Review took 5 minutes.

---

### Example 2: Reviewing a New API Endpoint

**Context:** PR adds new REST API endpoint for creating user posts.

**PR Details:**
- Files changed: 4 (controller, model, tests, docs)
- Lines changed: +180, -10
- Description: "Add POST /api/v1/posts endpoint with auth and validation"

**Review Process:**

1. **Understand context:**
```bash
gh pr view 1235
# Feature: Users can create posts via API
# Includes: Authentication, validation, rate limiting
# Tests: Unit and integration tests included
```

2. **Code quality review:**
```python
# Controller code (simplified):
@app.route('/api/v1/posts', methods=['POST'])
@require_auth  # ✓ Good: auth required
def create_post():
    data = request.get_json()

    # ✓ Good: input validation
    if not data or 'content' not in data:
        return jsonify({'error': 'Content required'}), 400

    if len(data['content']) > 10000:  # ✓ Good: size limit
        return jsonify({'error': 'Content too long'}), 400

    # ✓ Good: uses current user from auth
    post = Post(
        user_id=current_user.id,
        content=data['content']
    )

    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_dict()), 201
```

Quality: Good structure, clear logic ✓

3. **Security review:**
- ✓ Authentication required
- ✓ Authorization implicit (user can only create own posts)
- ✓ Input validation present
- ✓ Size limit prevents abuse
- ⚠️ **Issue found**: No XSS protection on content

**Feedback on security:**
```markdown
**Security Issue**: Line 45 - User content is not sanitized before storage.
This could allow XSS attacks if content is rendered without escaping.

Recommendation: Use bleach or similar library to sanitize HTML:
```python
import bleach

content = bleach.clean(
    data['content'],
    tags=['p', 'br', 'strong', 'em'],  # Allow safe tags only
    strip=True
)
```

Or ensure frontend always escapes content when rendering.
```

4. **Performance review:**
- ✓ Single database insert
- ✓ No N+1 queries
- ⚠️ **Issue found**: No rate limiting implemented despite PR description

**Feedback on performance:**
```markdown
**Missing Feature**: PR description mentions rate limiting, but I don't see
it implemented. This endpoint could be abused to spam posts.

Suggestion: Add rate limiter decorator:
```python
@app.route('/api/v1/posts', methods=['POST'])
@require_auth
@rate_limit(max=10, period=60)  # 10 posts per minute
def create_post():
    ...
```
```

5. **Testing review:**
```python
# Tests included:
def test_create_post_with_valid_data():
    """Test successful post creation."""
    # ✓ Good: tests happy path

def test_create_post_without_auth():
    """Test auth required."""
    # ✓ Good: tests security

def test_create_post_with_empty_content():
    """Test validation."""
    # ✓ Good: tests validation

# ⚠️ Missing: test for content length limit
# ⚠️ Missing: test for XSS prevention (once implemented)
```

**Feedback on testing:**
```markdown
**Testing Gap**: Missing test for content length validation (line 47).
Please add:
```python
def test_create_post_with_too_long_content_returns_400():
    content = "x" * 10001  # Exceeds 10000 char limit
    response = client.post('/api/v1/posts',
                          json={'content': content},
                          headers=auth_headers)
    assert response.status_code == 400
    assert 'too long' in response.json['error'].lower()
```
```

6. **Documentation review:**
```yaml
# OpenAPI spec updated:
/api/v1/posts:
  post:
    summary: Create a new post
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              content:
                type: string
                maxLength: 10000
    responses:
      201:
        description: Post created successfully
      400:
        description: Invalid input
      401:
        description: Authentication required
```
✓ Good: API docs updated

**Final Feedback:**
```markdown
Nice work on the endpoint structure and tests! A few issues to address:

## Required Changes:

1. **Security**: Add XSS protection on user content (see comment on line 45)
2. **Feature**: Implement rate limiting as mentioned in PR description
3. **Testing**: Add test for content length validation

## Suggestions (optional):

- Consider adding a `published_at` timestamp for posts
- Might want to return created post with full details including user info

Once these are addressed, this will be ready to merge. Let me know if you
have questions!
```

**Outcome:** Requested changes. Issues found before they reached production. Author addressed concerns and PR was approved on second review.

---

### Example 3: Reviewing Database Migration

**Context:** PR adds database migration for new feature.

**PR Details:**
- Files changed: 2 (migration, model)
- Lines changed: +45, -5
- Description: "Add notifications table and user preferences"

**Review Process:**

1. **Check migration file:**
```python
# Migration: add_notifications_table.py
def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
    )
    op.create_index('idx_user_notifications', 'notifications', ['user_id', 'created_at'])

def downgrade():
    op.drop_index('idx_user_notifications')
    op.drop_table('notifications')
```

2. **Migration review checklist:**
- ✓ Both upgrade and downgrade provided
- ✓ Index added for common query pattern
- ✓ Foreign key relationship defined
- ⚠️ **Issue**: Index on `read` column might be needed for querying unread notifications
- ⚠️ **Issue**: No index on `type` if notifications are filtered by type

**Feedback:**
```markdown
**Performance Suggestion**: Consider adding index on `read` column if you'll
query for unread notifications frequently:

```python
op.create_index('idx_unread_notifications', 'notifications',
               ['user_id', 'read', 'created_at'])
```

This composite index will help queries like:
`SELECT * FROM notifications WHERE user_id = ? AND read = false ORDER BY created_at DESC`

**Question**: Will notifications be filtered by type frequently? If so,
consider including `type` in the index as well.
```

3. **Model review:**
```python
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')
```
✓ Model matches migration

4. **Testing check:**
- ⚠️ **Issue**: No test for migration
- ⚠️ **Issue**: No test for model

**Feedback:**
```markdown
**Testing Gap**: Please add test to verify migration runs successfully and
model works as expected:

```python
def test_notification_model():
    user = User(email="test@example.com")
    notification = Notification(
        user=user,
        type="mention",
        content="You were mentioned in a post"
    )
    db.session.add_all([user, notification])
    db.session.commit()

    assert notification.id is not None
    assert notification.read is False
    assert notification.user == user
```
```

**Outcome:** Suggested improvements. Migration is safe but could be optimized. After addressing performance suggestion and adding tests, approved.

## Troubleshooting

### Issue 1: Unsure If Security Issue Is Serious

**Symptoms:**
- Code looks potentially vulnerable but you're not certain
- Author claims it's safe but you have doubts

**Solution:**
1. Research the specific vulnerability (SQLi, XSS, etc.)
2. Try to write an exploit in test environment
3. Consult security team or senior engineer
4. When in doubt, flag it and discuss

**Better safe than sorry** - flag potential security issues even if uncertain.

### Issue 2: PR Too Large to Review Effectively

**Symptoms:**
- PR has 500+ lines changed
- Multiple unrelated changes
- Difficulty understanding the full impact

**Solution:**
1. Ask author to split into smaller PRs
2. Review in multiple sessions if splitting not feasible
3. Focus on critical paths and security issues first
4. Consider pair reviewing with another engineer

### Issue 3: Tests Pass But Code Seems Wrong

**Symptoms:**
- All tests green but logic looks suspicious
- Tests might not cover the actual usage

**Solution:**
1. Check out the branch locally
2. Run the code with realistic data
3. Add tests for the scenario you're concerned about
4. Discuss your concerns with author

**Trust your instincts** - if something feels wrong, investigate further.

## Related Skills

This skill works well with:

- **security-audit**: For deep security review of sensitive changes
- **api-design**: When reviewing new API endpoints
- **database-design**: When reviewing database schema changes
- **testing-strategy**: For evaluating test coverage approach

## Notes

### Limitations

- Checklist focuses on web application code; adapt for other domains
- Security section covers common issues but not comprehensive security audit
- Performance section provides general guidance; may need profiling for specific concerns

### Assumptions

- Code is in a pull request or branch
- CI/CD pipeline is set up and running
- Team has agreed-upon coding standards
- Author has provided adequate context in PR description

## Version History

### Version 1.0.0 (2025-01-20)
- Initial creation
- Comprehensive checklist covering quality, security, performance, testing, documentation
- Examples for different PR types
- Troubleshooting guide

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Common security vulnerabilities
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)
- Internal: Team coding standards at [internal wiki]
