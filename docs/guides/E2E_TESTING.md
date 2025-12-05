# E2E Testing Guide for AI Agents

## Overview

End-to-end (E2E) testing is **mandatory** for all user-facing features in the AI_agents system. This guide explains why E2E testing is critical, how to implement it using the webapp-testing skill, and how to integrate it into the agent workflow.

## Why E2E Testing is Mandatory

### The Problem: Passing Unit Tests, Failing Users

A common failure mode in agent-developed code:
- Unit tests pass ✅
- Integration tests pass ✅
- Agent marks feature "complete" ✅
- **But the UI doesn't work for users** ❌

### Real Examples

**Example 1: The Invisible Error**
```javascript
// Unit test (passes)
test('API returns error for invalid login', () => {
  const result = login('bad@email.com', 'wrong');
  expect(result.error).toBe('Invalid credentials');
});

// But in the UI...
// User clicks login → sees blank screen
// Error exists in response but never displayed
```

**Example 2: The Missing Button**
```javascript
// Unit test (passes)
test('handleSubmit processes form data', () => {
  const data = { email: 'test@example.com' };
  expect(handleSubmit(data)).toBeTruthy();
});

// But in the UI...
// Button doesn't render due to CSS issue
// Or onClick handler not attached
// Function works but user can't trigger it
```

**Example 3: The Broken Navigation**
```javascript
// Unit test (passes)
test('router redirects to dashboard after login', () => {
  const result = router.push('/dashboard');
  expect(result).toBe(true);
});

// But in the UI...
// Route is configured but middleware blocks it
// Or dashboard component fails to render
// Navigation triggered but user stuck on loading screen
```

### What E2E Tests Catch

E2E tests verify the **actual user experience**:
- ✅ UI elements render and are visible
- ✅ Buttons are clickable and functional
- ✅ Error messages display to users
- ✅ Loading states show during async operations
- ✅ Success feedback is visible
- ✅ Navigation actually works
- ✅ Forms submit and validate correctly

## The webapp-testing Skill

### What It Is

The webapp-testing skill uses **Playwright** to automate browser testing. It:
- Launches real browsers (Chrome, Firefox, Safari)
- Simulates user interactions (clicks, typing, navigation)
- Verifies what users actually see
- Captures screenshots and videos of failures

### When to Use It

**REQUIRED for:**
- Any feature with a user interface (web, mobile)
- User workflows (login, registration, checkout)
- Form submissions and validation
- Navigation and routing
- Error message display
- Loading states

**NOT NEEDED for:**
- Pure backend APIs (use integration tests)
- Utility functions (use unit tests)
- Database operations (use integration tests)

## E2E Testing Workflow

### 1. QA Tester: Write E2E Tests

When assigned a feature, the QA Tester:

```markdown
## Task: Test user login feature

1. Use webapp-testing skill to create E2E tests
2. Test scenarios:
   - Happy path: Valid credentials → Dashboard
   - Error path: Invalid credentials → Error message displayed
   - Validation: Empty fields → Validation errors shown
   - Edge case: Already logged in → Redirect to dashboard

3. Verify VISUAL elements:
   - Login form renders
   - Error messages are visible (not just in console)
   - Success feedback shows
   - Navigation completes
```

**E2E Test Example:**
```javascript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Login Flow', () => {
  test('successful login redirects to dashboard', async ({ page }) => {
    await page.goto('http://localhost:3000/login');

    // Fill form
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'ValidPass123!');

    // Submit
    await page.click('button[type="submit"]');

    // Wait for navigation
    await page.waitForURL('**/dashboard');

    // Verify user sees dashboard
    expect(page.url()).toContain('/dashboard');

    // Verify welcome message is VISIBLE
    const welcome = await page.locator('.welcome-message').textContent();
    expect(welcome).toContain('Welcome back');
  });

  test('invalid credentials show error message to user', async ({ page }) => {
    await page.goto('http://localhost:3000/login');

    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'WrongPassword');
    await page.click('button[type="submit"]');

    // CRITICAL: Verify error is VISIBLE to user
    const errorMessage = await page.locator('.error-message');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText('Invalid credentials');

    // User should stay on login page
    expect(page.url()).toContain('/login');
  });

  test('empty fields show validation errors', async ({ page }) => {
    await page.goto('http://localhost:3000/login');

    // Try to submit without filling
    await page.click('button[type="submit"]');

    // Verify validation errors are DISPLAYED
    const emailError = page.locator('.email-error');
    const passwordError = page.locator('.password-error');

    await expect(emailError).toBeVisible();
    await expect(passwordError).toBeVisible();
  });

  test('loading state shown during login', async ({ page }) => {
    await page.goto('http://localhost:3000/login');

    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'ValidPass123!');

    // Start login
    await page.click('button[type="submit"]');

    // Verify loading indicator is shown
    const loadingSpinner = page.locator('.loading-spinner');
    await expect(loadingSpinner).toBeVisible();

    // Wait for login to complete
    await page.waitForURL('**/dashboard');
  });
});
```

### 2. Running E2E Tests

```bash
# Install dependencies (first time only)
npm install --save-dev @playwright/test
npx playwright install

# Run E2E tests
npm run test:e2e

# Run in headed mode (see browser)
npm run test:e2e -- --headed

# Run specific test
npm run test:e2e -- login.spec.ts

# Debug mode (pause and inspect)
npm run test:e2e -- --debug
```

### 3. Senior Engineer: Verify E2E Tests Pass

Before approving any feature:

```bash
# 1. Run full test suite
npm test                # Unit + integration tests
npm run test:e2e       # E2E tests

# 2. Verify E2E test files exist
find . -name "*.spec.ts" -o -name "*.e2e.ts"

# 3. Check for E2E coverage
# For each feature, there should be corresponding E2E tests
```

**Senior Engineer Checklist:**
- [ ] E2E test files exist for feature
- [ ] Tests cover happy path
- [ ] Tests cover error cases
- [ ] Tests verify UI elements are visible
- [ ] All E2E tests passing
- [ ] No "skip" or "todo" tests

### 4. Feature Tracking Integration

Update `.ai-agents/state/feature-tracking.json`:

```json
{
  "id": "AUTH-001",
  "description": "User login with email/password",
  "status": "passing",
  "test_file": "tests/e2e/login.spec.ts",
  "test_command": "npm run test:e2e -- login.spec.ts",
  "verified_by": "qa_tester",
  "acceptance_criteria": [
    {
      "criterion": "User can login with valid credentials",
      "met": true
    },
    {
      "criterion": "Error message shown for invalid credentials",
      "met": true
    },
    {
      "criterion": "E2E tests verify UI behavior",
      "met": true
    }
  ]
}
```

## Common E2E Testing Patterns

### Testing Forms

```javascript
test('form validation and submission', async ({ page }) => {
  await page.goto('/contact');

  // Test required field validation
  await page.click('button[type="submit"]');
  await expect(page.locator('.name-error')).toBeVisible();

  // Fill form
  await page.fill('input[name="name"]', 'John Doe');
  await page.fill('input[name="email"]', 'john@example.com');
  await page.fill('textarea[name="message"]', 'Test message');

  // Submit
  await page.click('button[type="submit"]');

  // Verify success message
  await expect(page.locator('.success-message')).toBeVisible();
  await expect(page.locator('.success-message')).toContainText('Message sent');
});
```

### Testing Navigation

```javascript
test('navigation between pages', async ({ page }) => {
  await page.goto('/');

  // Click navigation link
  await page.click('a[href="/about"]');

  // Verify navigation completed
  await page.waitForURL('**/about');
  expect(page.url()).toContain('/about');

  // Verify page content loaded
  await expect(page.locator('h1')).toContainText('About Us');
});
```

### Testing Async Operations

```javascript
test('data loading with async operation', async ({ page }) => {
  await page.goto('/dashboard');

  // Verify loading state
  await expect(page.locator('.loading-spinner')).toBeVisible();

  // Wait for data to load
  await page.waitForSelector('.data-table', { state: 'visible' });

  // Verify data is displayed
  const rows = await page.locator('.data-table tr').count();
  expect(rows).toBeGreaterThan(0);
});
```

### Testing Error States

```javascript
test('network error handling', async ({ page, context }) => {
  // Simulate network failure
  await context.route('**/api/data', route => route.abort());

  await page.goto('/dashboard');

  // Verify error message is shown to user
  await expect(page.locator('.error-banner')).toBeVisible();
  await expect(page.locator('.error-banner')).toContainText('Unable to load data');

  // Verify retry button is available
  await expect(page.locator('button.retry')).toBeVisible();
});
```

## Best Practices

### 1. Test from User Perspective

❌ **Bad: Testing implementation details**
```javascript
test('handleLogin function is called', async ({ page }) => {
  // Testing internal function calls, not user experience
});
```

✅ **Good: Testing user experience**
```javascript
test('user can login and see dashboard', async ({ page }) => {
  // Test what user sees and does
});
```

### 2. Verify Visual Elements

❌ **Bad: Checking data exists**
```javascript
const data = await response.json();
expect(data.message).toBe('Success');
```

✅ **Good: Checking user sees message**
```javascript
await expect(page.locator('.success-message')).toBeVisible();
await expect(page.locator('.success-message')).toContainText('Success');
```

### 3. Use Reliable Selectors

❌ **Bad: Fragile selectors**
```javascript
await page.click('.css-1234567'); // CSS class generated by framework
await page.click('div > div > button'); // Position-based selector
```

✅ **Good: Stable selectors**
```javascript
await page.click('button[type="submit"]'); // Semantic selector
await page.click('[data-testid="login-button"]'); // Test ID
await page.click('text=Login'); // Text content
```

### 4. Handle Async Operations

❌ **Bad: Hard-coded waits**
```javascript
await page.click('button');
await page.waitForTimeout(5000); // Brittle, slow
```

✅ **Good: Wait for specific conditions**
```javascript
await page.click('button');
await page.waitForSelector('.success-message', { state: 'visible' });
// or
await page.waitForURL('**/dashboard');
```

### 5. Clean Test Data

```javascript
test.beforeEach(async ({ page }) => {
  // Set up test data
  await createTestUser('test@example.com', 'password123');
});

test.afterEach(async ({ page }) => {
  // Clean up test data
  await deleteTestUser('test@example.com');
});
```

## Troubleshooting

### Test Fails: Element Not Found

```javascript
// Add explicit waits
await page.waitForSelector('.element', { state: 'visible' });

// Check if element is in shadow DOM
const shadowHost = await page.locator('#shadow-host');
const shadowRoot = await shadowHost.evaluateHandle(el => el.shadowRoot);

// Use debugging
await page.pause(); // Opens Playwright Inspector
```

### Test is Flaky

```javascript
// Increase timeout for slow operations
await page.waitForSelector('.element', { timeout: 10000 });

// Use better waiting strategies
await page.waitForLoadState('networkidle');

// Retry failed tests
test.describe.configure({ retries: 2 });
```

### Can't See What's Happening

```bash
# Run in headed mode
npm run test:e2e -- --headed

# Enable slow motion
npm run test:e2e -- --headed --slow-mo=1000

# Use debug mode
npm run test:e2e -- --debug
```

## Integration with Feature Tracking

Features progress through states based on E2E test status:

```
not_started
    ↓
in_progress (development + unit tests)
    ↓
in_progress (E2E tests written)
    ↓
passing (all tests pass, including E2E) ✅
```

**DO NOT mark as "passing" until:**
1. Unit tests pass
2. Integration tests pass
3. **E2E tests pass** ← Critical gate
4. Code reviewed

## Summary

### For QA Testers
- Use webapp-testing skill for all user-facing features
- Write tests that verify what users actually see
- Cover happy path, error cases, and edge cases
- Test visual elements, not just data

### For Senior Engineers
- Require E2E tests before approving features
- Verify tests actually check user experience
- Ensure tests pass in CI/CD pipeline
- Block merges without E2E coverage

### For Managers
- Features not "complete" without E2E tests
- Update feature-tracking.json with E2E test status
- Prioritize E2E testing in project timelines
- Track E2E test coverage as quality metric

## Resources

- [Playwright Documentation](https://playwright.dev)
- webapp-testing skill documentation
- Example E2E tests: `examples/session-continuity/`
- Feature tracking schema: `schemas/feature-tracking.json`
