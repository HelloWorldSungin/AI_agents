# Browser Verification Skill

**Version:** 1.0.0
**Category:** Testing
**Purpose:** Visual verification of UI changes through browser automation

---

## Description

The Browser Verification Skill enables visual verification of UI changes through automated browser testing. It ensures that UI-related tasks have verifiable visual evidence, not just backend tests passing.

This skill is **mandatory** for any task tagged with `frontend`, `ui`, or `style` categories.

---

## When to Use

Invoke this skill when:

- Implementing UI components
- Making CSS/styling changes
- Modifying page layouts
- Adding interactive elements
- Fixing visual bugs
- Verifying responsive design

---

## Capabilities

### 1. Screenshot Capture

Capture screenshots at key verification points:

```javascript
// Puppeteer example
const browser = await puppeteer.launch();
const page = await browser.newPage();

// Navigate to page
await page.goto('http://localhost:3000/login');

// Capture screenshot
await page.screenshot({
  path: 'screenshots/login-page.png',
  fullPage: true
});

// Capture specific element
const element = await page.$('.login-form');
await element.screenshot({
  path: 'screenshots/login-form.png'
});
```

### 2. Viewport Testing

Test across multiple viewports:

```javascript
const viewports = [
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1920, height: 1080 }
];

for (const viewport of viewports) {
  await page.setViewport(viewport);
  await page.screenshot({
    path: `screenshots/${feature}-${viewport.name}.png`
  });
}
```

### 3. Console Error Detection

Capture and report console errors:

```javascript
const consoleErrors = [];

page.on('console', msg => {
  if (msg.type() === 'error') {
    consoleErrors.push(msg.text());
  }
});

// After interactions
if (consoleErrors.length > 0) {
  throw new Error(`Console errors detected: ${consoleErrors.join(', ')}`);
}
```

### 4. Visual Diff (Optional)

Compare screenshots with baseline:

```javascript
const { diffImageToSnapshot } = require('jest-image-snapshot');

const result = diffImageToSnapshot({
  receivedImageBuffer: currentScreenshot,
  snapshotIdentifier: 'login-page',
  snapshotsDir: 'screenshots/baseline'
});

if (!result.pass) {
  console.log(`Visual diff detected: ${result.diffRatio}% difference`);
}
```

### 5. Interaction Verification

Verify interactive elements work:

```javascript
// Click button
await page.click('#submit-button');

// Wait for navigation or state change
await page.waitForNavigation();
// OR
await page.waitForSelector('.success-message');

// Verify result
const message = await page.$eval('.success-message', el => el.textContent);
expect(message).toContain('Success');

// Screenshot the result
await page.screenshot({ path: 'screenshots/after-submit.png' });
```

---

## Required Evidence

For UI tasks, the following evidence is **required**:

### Minimum Evidence Set

```yaml
visual_verification:
  required:
    - before_screenshot: "State before changes (if modifying)"
    - after_screenshot: "State after changes"
    - mobile_screenshot: "Mobile viewport (375px)"
    - console_clean: "No console errors"

  recommended:
    - tablet_screenshot: "Tablet viewport (768px)"
    - visual_diff: "Comparison with baseline"
    - interaction_recording: "GIF of interaction flow"
```

### Evidence Location

```
.ai-agents/evidence/
└── {task_id}/
    ├── before-desktop.png
    ├── after-desktop.png
    ├── after-mobile.png
    ├── after-tablet.png
    ├── console-log.txt
    └── verification-report.md
```

### Verification Report Format

```markdown
# Visual Verification Report

**Task**: {task_id}
**Feature**: {feature_name}
**Date**: {timestamp}

## Screenshots

### Desktop (1920x1080)
![Desktop](./after-desktop.png)

### Mobile (375x667)
![Mobile](./after-mobile.png)

### Tablet (768x1024)
![Tablet](./after-tablet.png)

## Console Status
- Errors: 0
- Warnings: 2 (acceptable - deprecation notices)

## Interactions Verified
- [x] Form submission works
- [x] Error states display correctly
- [x] Success redirect functions

## Visual Diff
- Baseline match: 98.5%
- Acceptable threshold: 95%
- Status: PASS

## Notes
{any additional observations}
```

---

## Integration

### With Task Flow

```
UI Task Selected
       │
       ▼
┌─────────────────┐
│ Start Dev       │
│ Server          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Capture Before  │──── If modifying existing UI
│ Screenshots     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Implement       │
│ Changes         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Run Browser     │──FAIL──► Fix Issues
│ Verification    │              │
└────────┬────────┘              │
         │ PASS                  │
         ▼                       │
┌─────────────────┐              │
│ Generate        │◄─────────────┘
│ Evidence Report │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Attach to Task  │
│ Mark Complete   │
└─────────────────┘
```

### With Acceptance Criteria

```yaml
task:
  title: "Implement login form"
  category: "frontend"
  acceptance_criteria:
    - "Login form displays email and password fields"
    - "Submit button is disabled until valid input"
    - "Error message shows on invalid credentials"
    - "Success redirects to dashboard"
  visual_verification:
    - "Screenshot of empty form"
    - "Screenshot of filled form"
    - "Screenshot of error state"
    - "Screenshot of success redirect"
    - "Mobile screenshot shows responsive layout"
```

---

## MCP Integration

This skill can use MCP Puppeteer or Playwright servers:

### Puppeteer MCP

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-puppeteer"]
    }
  }
}
```

### Playwright MCP

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-server-playwright"]
    }
  }
}
```

---

## Commands

### Browser Verification Commands

```bash
# Run visual verification for a task
/verify-ui {task_id}

# Capture baseline screenshots
/capture-baseline {page_path}

# Compare with baseline
/visual-diff {task_id}
```

---

## Configuration

```yaml
visual_verification:
  # Requirement level
  requirement: "required"  # "required", "recommended", "disabled"

  # Browser tool
  browser_tool: "puppeteer"  # "puppeteer", "playwright"

  # Viewports to test
  viewports:
    - name: "mobile"
      width: 375
      height: 667
    - name: "tablet"
      width: 768
      height: 1024
    - name: "desktop"
      width: 1920
      height: 1080

  # Evidence storage
  evidence_dir: ".ai-agents/evidence"

  # Screenshot options
  screenshots:
    full_page: true
    format: "png"
    quality: 90

  # Visual diff settings
  diff:
    enabled: true
    threshold: 0.05  # 5% difference allowed
    baseline_dir: ".ai-agents/baselines"

  # Console monitoring
  console:
    fail_on_error: true
    ignore_warnings: false
    ignored_messages:
      - "DevTools"
      - "Download the React DevTools"
```

---

## Enforcement

### For UI Tasks

UI tasks **cannot** be marked complete without:

1. At least one screenshot proving the feature works
2. Mobile viewport screenshot
3. Console error check (0 errors)

### Task Validation

```python
def validate_ui_task_completion(task):
    if task.category not in ['frontend', 'ui', 'style']:
        return True  # Non-UI task, no visual verification needed

    evidence_dir = Path(f".ai-agents/evidence/{task.id}")

    required_files = [
        evidence_dir / "after-desktop.png",
        evidence_dir / "after-mobile.png",
        evidence_dir / "verification-report.md"
    ]

    for file in required_files:
        if not file.exists():
            raise ValidationError(f"Missing visual evidence: {file}")

    # Check console report
    report = (evidence_dir / "verification-report.md").read_text()
    if "Errors: 0" not in report:
        raise ValidationError("Console errors detected in verification")

    return True
```

---

## Version History

- **1.0.0** (2024-01-15): Initial browser verification skill
