# Mobile App Team Example

This example demonstrates how to configure a multi-agent team for cross-platform mobile application development using React Native.

## Team Composition

- **Team Manager**: Coordinates all agents, manages releases, resolves conflicts
- **Mobile Developer**: React Native development for iOS and Android
- **Backend Developer**: Node.js + Express API development
- **Architect**: System architecture and design patterns
- **QA Tester**: Mobile testing and quality assurance

## Skills Integration

This example shows how Anthropic Skills enhance mobile development capabilities.

### Team Manager Skills

**Skills**: `communication/internal-comms`, `documents/pptx`, `documents/xlsx`
**Token Budget**: ~12,000 tokens (3,000 base + ~9,000 skills)

The manager uses skills to:
- Generate release notes and status updates
- Create stakeholder presentations for app store submissions
- Track release metrics and app performance data

**Example Usage**:
```
User: "Create a release summary for version 2.0"
Manager: Uses internal-comms to generate release notes
         Uses xlsx to create release metrics dashboard
```

### Mobile Developer Skills

**Skills**: `design/theme-factory`, `core/web-artifacts-builder`, `core/skill-creator`
**Token Budget**: ~16,000 tokens (3,000 base + 6,000 platforms + ~7,000 skills)

The mobile developer uses skills to:
- Apply consistent themes across mobile UI components
- Leverage React component patterns for React Native
- Create custom mobile-specific development patterns

**Example Usage**:
```
User: "Build a settings screen with theme support"
Mobile Dev: Uses theme-factory to apply consistent mobile theme
            Uses web-artifacts-builder for React component patterns
            Adapts for React Native specific requirements
```

### Backend Developer Skills

**Skills**: `core/mcp-builder`, `core/webapp-testing`, `documents/xlsx`
**Token Budget**: ~12,000 tokens (3,000 base + 3,000 platform + ~6,000 skills)

The backend developer uses skills to:
- Build mobile API integrations using MCP
- Test API endpoints for mobile app consumption
- Generate analytics data exports

**Example Usage**:
```
User: "Create an MCP server for push notifications"
Backend Dev: Uses mcp-builder to design notification service
             Uses webapp-testing to verify API endpoints
```

### Architect Skills

**Skills**: `core/skill-creator`, `documents/pptx`, `communication/internal-comms`
**Token Budget**: ~14,000 tokens (3,000 base + 3,000 platform + ~8,000 skills)

The architect uses skills to:
- Design custom mobile development patterns and skills
- Create architecture presentations for stakeholders
- Document technical decisions and patterns

**Example Usage**:
```
User: "Design offline-first data sync pattern"
Architect: Uses skill-creator to document the pattern
           Uses pptx to create architecture presentation
```

### QA Tester Skills

**Skills**: `core/webapp-testing`, `documents/xlsx`, `documents/pdf`
**Token Budget**: ~11,000 tokens (3,000 base + ~8,000 skills)

The QA tester uses skills to:
- Test React Native web views and components
- Track device matrix and test results
- Generate certification reports for app stores

**Example Usage**:
```
User: "Test the app on all target devices"
QA Tester: Uses webapp-testing for automated component tests
           Uses xlsx to track device compatibility matrix
           Uses pdf to generate certification report
```

### Total Team Token Budget

**Without Skills**: ~15,000 tokens (5 agents x 3,000 base)
**With Skills**: ~65,000 tokens (base + platforms + skills)

This represents a ~4.3x increase in context usage for significantly enhanced mobile development capabilities.

## Project Setup

### 1. Install the AI Agents Library

```bash
# Clone the AI agents library
git clone git@github.com:org/AI_agents.git

# Or add as git submodule
git submodule add git@github.com:org/AI_agents.git .ai-agents/library
```

### 2. Create Project Structure

```bash
# In your React Native project root
mkdir -p .ai-agents/{context,state,checkpoints,memory,workflows}

# Copy the example configuration
cp AI_agents/examples/mobile-app-team/config.yml .ai-agents/config.yml
```

### 3. Create Mobile-Specific Context Files

Create the following files in `.ai-agents/context/`:

**architecture.md**
```markdown
# Mobile App Architecture

## Overview
Cross-platform fitness tracking app using React Native.

## Architecture
- Mobile: React Native for iOS and Android
- Backend: Node.js REST API
- State: Redux Toolkit for client state
- Offline: AsyncStorage + sync queue
- Analytics: Firebase Analytics

## Navigation
React Navigation v6 with bottom tabs and stack navigators.
```

**device-matrix.md**
```markdown
# Device Testing Matrix

## iOS Devices
- iPhone 13 Pro (iOS 16+)
- iPhone SE (iOS 15+)
- iPad Pro 12.9" (iPadOS 16+)

## Android Devices
- Pixel 6 (Android 12+)
- Samsung Galaxy S21 (Android 11+)
- OnePlus 9 (Android 11+)

## Minimum Versions
- iOS: 13.0
- Android: API 21 (Android 5.0)
```

**design-system.md**
```markdown
# Mobile Design System

## Colors
- Primary: #007AFF (iOS Blue)
- Secondary: #34C759 (Success Green)
- Error: #FF3B30 (Error Red)
- Background: #F2F2F7 (Light), #000000 (Dark)

## Typography
- Heading: SF Pro Display (iOS), Roboto (Android)
- Body: SF Pro Text (iOS), Roboto (Android)

## Spacing
- xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px

## Components
- Use React Native Paper for Material Design
- Custom iOS-style components for native feel
```

### 4. Initialize Agent System

```bash
# Compose mobile developer with skills
python scripts/compose-agent.py \
  --config examples/mobile-app-team/config.yml \
  --agent mobile_developer \
  --output .ai-agents/prompts/mobile-developer.md
```

## Usage

### Composing Agents with Skills

```bash
# Compose all mobile team agents
for agent in team_manager mobile_developer backend_developer architect qa_tester; do
  python scripts/compose-agent.py \
    --config examples/mobile-app-team/config.yml \
    --agent $agent \
    --output .ai-agents/prompts/$agent.md
done
```

### Starting a New Feature

1. **Manager receives feature request**
   ```
   User: "Add heart rate tracking feature"
   ```

2. **Manager breaks down tasks using internal-comms**
   ```
   Manager generates task breakdown:

   PROGRESS:
   - Analyzed heart rate tracking requirements
   - Researched HealthKit (iOS) and Google Fit (Android) integration

   PLANS:
   - TASK-001: Design heart rate data architecture (Architect)
   - TASK-002: Implement HealthKit integration (Mobile Dev - iOS)
   - TASK-003: Implement Google Fit integration (Mobile Dev - Android)
   - TASK-004: Create heart rate API endpoints (Backend Dev)
   - TASK-005: Build heart rate UI components (Mobile Dev)
   - TASK-006: Test on all devices (QA Tester)

   PROBLEMS:
   - Need access to test devices with heart rate sensors
   ```

3. **Architect designs the pattern using skill-creator**
   ```
   Architect: Creates custom skill for health data integration patterns
              Documents architecture in pptx presentation
   ```

4. **Mobile Developer implements using skills**
   ```
   Mobile Dev: Uses theme-factory for consistent heart rate charts
               Uses web-artifacts-builder for React component patterns
               Implements platform-specific native modules
   ```

5. **QA Tester validates across devices**
   ```
   QA Tester: Uses webapp-testing for component testing
              Uses xlsx to track device compatibility
              Uses pdf to generate test certification
   ```

## Mobile-Specific Workflows

### Release Management

```bash
# Manager creates release checklist
1. Version bump in package.json and app config
2. Generate release notes (internal-comms skill)
3. Create app store screenshots
4. Update store listings
5. Generate metrics dashboard (xlsx skill)
6. Create stakeholder presentation (pptx skill)
```

### Platform-Specific Testing

```yaml
# iOS Testing
- TestFlight beta distribution
- App Store certification
- iOS-specific gestures and behaviors

# Android Testing
- Google Play internal testing
- Play Store certification
- Android-specific behaviors
```

### Performance Monitoring

```bash
# Backend Dev creates analytics dashboard
1. Use xlsx skill to structure metrics
2. Track: app crashes, API response times, offline sync
3. Generate weekly performance reports
```

## Best Practices

### 1. Platform Parity
Ensure feature parity between iOS and Android while respecting platform conventions.

### 2. Offline-First Design
Design all features to work offline with background sync.

### 3. Device Testing
Test on physical devices, not just simulators/emulators.

### 4. Theme Consistency
Use theme-factory skill to maintain consistent visual design across platforms.

### 5. Release Cadence
- iOS: 2-week review time buffer
- Android: 3-day review time buffer
- Coordinate releases for same-day availability

## Tech Stack

- **Mobile**: React Native 0.72+, TypeScript
- **State**: Redux Toolkit, React Query
- **Navigation**: React Navigation v6
- **UI**: React Native Paper, custom components
- **Testing**: Jest, React Native Testing Library, Detox
- **Backend**: Node.js 18, Express, TypeScript, Prisma
- **Database**: PostgreSQL, Redis
- **Analytics**: Firebase, Custom dashboards
- **CI/CD**: GitHub Actions, Fastlane
- **Distribution**: TestFlight, Google Play Console

## Team Velocity Metrics

Track in `.ai-agents/state/project-state.json`:

- **Features per sprint**: Target: 3-5 major features
- **Bug resolution time**: Target: < 2 days for critical
- **App store review pass rate**: Target: > 90% first submission
- **Test coverage**: Target: > 75%
- **Crash-free rate**: Target: > 99.5%

## Further Reading

- [Skills Catalog](../../skills/CATALOG.md)
- [Mobile Platform Guide](../../platforms/mobile/mobile-developer.md)
- [Testing Guide](TESTING.md)

---

**Last Updated**: 2025-11-20
**Project Type**: React Native Mobile App
**Total Team Token Budget**: ~65,000 tokens
