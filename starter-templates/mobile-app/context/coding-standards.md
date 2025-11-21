# {{PROJECT_NAME}} - Mobile Coding Standards

## General Principles
- Write platform-agnostic code when possible
- Follow platform-specific guidelines for native features
- Maintain consistent styling and UX patterns

## Code Style
[React Native / Flutter / Native specific guidelines]

## Component Structure
- One component per file
- Props/State properly typed
- Hooks at top level
- Proper cleanup in useEffect

## Platform-Specific Code
```typescript
// Example for React Native
import { Platform } from 'react-native';

const styles = Platform.select({
  ios: { paddingTop: 20 },
  android: { paddingTop: 0 },
});
```

## Performance
- Lazy load screens
- Optimize images
- Minimize re-renders
- Use FlatList for long lists

## Testing
- Unit tests for utils and services
- Component tests for UI
- E2E tests for critical flows
