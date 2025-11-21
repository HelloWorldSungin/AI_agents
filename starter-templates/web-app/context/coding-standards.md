# {{PROJECT_NAME}} - Coding Standards

## Overview

This document defines the coding standards and conventions for {{PROJECT_NAME}}. All team members and AI agents must follow these guidelines.

---

## General Principles

1. **Code should be readable** - Write code for humans, not machines
2. **Consistency is key** - Follow existing patterns in the codebase
3. **Don't repeat yourself** (DRY) - Extract reusable logic
4. **Keep it simple** (KISS) - Avoid unnecessary complexity
5. **You ain't gonna need it** (YAGNI) - Don't add features prematurely

---

## TypeScript / JavaScript

### General Rules
- ✅ **Always use TypeScript** - No plain JavaScript files
- ✅ **Strict mode enabled** - `"strict": true` in tsconfig.json
- ❌ **No `any` types** - Use `unknown` or proper types
- ✅ **Explicit return types** - For all functions
- ✅ **Use `const`** by default - Only use `let` when reassignment needed

### Naming Conventions

```typescript
// Variables and functions: camelCase
const userName = "John";
function getUserData() { }

// Classes and interfaces: PascalCase
class UserService { }
interface UserData { }

// Types: PascalCase
type UserId = string;

// Constants: UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = "https://api.example.com";

// Private properties: prefix with underscore
class Service {
  private _cache = new Map();
}

// Boolean variables: is/has/should prefix
const isActive = true;
const hasPermission = false;
const shouldRetry = true;
```

### Code Organization

```typescript
// Order of elements in a file:
// 1. Imports (grouped and sorted)
import { useState, useEffect } from 'react';
import type { User } from '@/types';

// 2. Types and interfaces
interface Props {
  userId: string;
}

// 3. Constants
const DEFAULT_LIMIT = 20;

// 4. Main component/function
export function UserProfile({ userId }: Props) {
  // ...
}

// 5. Helper functions (not exported)
function formatDate(date: Date): string {
  // ...
}
```

### Prefer Interfaces Over Types

```typescript
// ✅ Good - Use interface for objects
interface User {
  id: string;
  name: string;
  email: string;
}

// ❌ Avoid - Type for objects (use for unions/primitives)
type User = {
  id: string;
  name: string;
}

// ✅ Good - Type for unions and primitives
type Status = 'active' | 'inactive' | 'pending';
type UserId = string;
```

---

## React

### Component Structure

```typescript
// ✅ Good - Functional component with proper typing
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

export function Button({
  label,
  onClick,
  variant = 'primary',
  disabled = false,
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
    >
      {label}
    </button>
  );
}
```

### File Naming

```
✅ PascalCase for components: Button.tsx, UserProfile.tsx
✅ camelCase for hooks: useAuth.ts, useLocalStorage.ts
✅ camelCase for utils: formatDate.ts, apiClient.ts
```

### Component Organization

```
components/
├── Button/
│   ├── Button.tsx          # Main component
│   ├── Button.test.tsx     # Tests
│   ├── Button.stories.tsx  # Storybook stories (if used)
│   └── index.ts            # Re-export
```

### Props

- **One component per file**
- **Props interface** named `ComponentNameProps`
- **Destructure props** in function signature
- **Default values** using ES6 default parameters
- **Children** should use `ReactNode` type

```typescript
interface CardProps {
  title: string;
  children: ReactNode;
  onClose?: () => void;
}
```

### Hooks Rules

- **Custom hooks** start with `use`
- **Call hooks** at the top level (not in conditionals)
- **Dependencies** in useEffect must be complete
- **Cleanup functions** in useEffect when needed

```typescript
// ✅ Good custom hook
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchUser() {
      const data = await api.getUser(userId);
      if (!cancelled) {
        setUser(data);
        setLoading(false);
      }
    }

    fetchUser();

    return () => {
      cancelled = true; // Cleanup
    };
  }, [userId]);

  return { user, loading };
}
```

---

## Backend (Node.js / Express)

### Architecture Pattern

**Controller → Service → Repository**

```typescript
// Controller: Handle HTTP requests/responses
export class UserController {
  async getUser(req: Request, res: Response) {
    const user = await userService.getUser(req.params.id);
    res.json({ success: true, data: user });
  }
}

// Service: Business logic
export class UserService {
  async getUser(id: string): Promise<User> {
    const user = await userRepository.findById(id);
    if (!user) throw new NotFoundError('User not found');
    return user;
  }
}

// Repository: Database access
export class UserRepository {
  async findById(id: string): Promise<User | null> {
    return await prisma.user.findUnique({ where: { id } });
  }
}
```

### Error Handling

```typescript
// ✅ Custom error classes
export class NotFoundError extends Error {
  statusCode = 404;
  constructor(message: string) {
    super(message);
    this.name = 'NotFoundError';
  }
}

// ✅ Centralized error middleware
export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  if (err instanceof NotFoundError) {
    return res.status(404).json({
      success: false,
      error: { code: 'NOT_FOUND', message: err.message }
    });
  }
  // ... handle other errors
}
```

### Async/Await

- ✅ **Use async/await** - No callbacks
- ✅ **Try/catch blocks** for error handling
- ❌ **No .then() chains** - Use async/await instead

```typescript
// ✅ Good
async function getUser(id: string): Promise<User> {
  try {
    const user = await db.users.findOne({ id });
    return user;
  } catch (error) {
    logger.error('Failed to fetch user', error);
    throw error;
  }
}
```

---

## Testing

### Test Structure

```typescript
describe('UserService', () => {
  // Arrange - setup
  beforeEach(() => {
    // Setup test data
  });

  // Tests
  describe('getUser', () => {
    it('should return user when found', async () => {
      // Arrange
      const userId = '123';
      const expectedUser = { id: userId, name: 'John' };

      // Act
      const result = await userService.getUser(userId);

      // Assert
      expect(result).toEqual(expectedUser);
    });

    it('should throw NotFoundError when user does not exist', async () => {
      // Arrange
      const userId = 'nonexistent';

      // Act & Assert
      await expect(userService.getUser(userId))
        .rejects
        .toThrow(NotFoundError);
    });
  });
});
```

### Test File Naming

```
src/components/Button.tsx      →  src/components/Button.test.tsx
src/services/userService.ts   →  src/services/userService.test.ts
```

### Coverage Requirements

- **Minimum 80%** overall coverage
- **100%** for critical business logic
- **All error paths** must be tested

---

## Git Workflow

### Branch Naming

```
feature/short-description      - New features
fix/bug-description            - Bug fixes
refactor/description           - Code refactoring
docs/description               - Documentation
test/description               - Test additions
chore/description              - Maintenance tasks
```

### Commit Messages

Follow **Conventional Commits** format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(auth): add JWT authentication

fix(api): handle null values in user response

docs(readme): update installation instructions

refactor(utils): extract date formatting logic
```

### Pull Request Requirements

1. ✅ All tests passing
2. ✅ No linting errors
3. ✅ Code review from at least one team member
4. ✅ PR description explains the change
5. ✅ Related issue linked (if applicable)

---

## File and Directory Naming

### Frontend
```
PascalCase:  Components, Pages
camelCase:   hooks, utils, services
kebab-case:  CSS files, asset files
```

### Backend
```
camelCase:   Most files (controllers, services, utils)
PascalCase:  Classes
kebab-case:  Config files
```

---

## Comments and Documentation

### When to Comment

✅ **Do comment:**
- Complex algorithms or business logic
- Workarounds or non-obvious solutions
- Public API functions (JSDoc)
- TODOs with ticket references

❌ **Don't comment:**
- Obvious code (good code is self-documenting)
- Commented-out code (delete it, git remembers)

### JSDoc for Public APIs

```typescript
/**
 * Fetches user data from the API
 *
 * @param userId - The unique identifier of the user
 * @returns Promise resolving to user data
 * @throws {NotFoundError} When user doesn't exist
 *
 * @example
 * ```ts
 * const user = await getUser('123');
 * console.log(user.name);
 * ```
 */
export async function getUser(userId: string): Promise<User> {
  // implementation
}
```

---

## Code Formatting

### Prettier Configuration

All code is automatically formatted with Prettier:

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

### ESLint Rules

Key rules:
- No unused variables
- No console.log in production
- Explicit function return types
- Consistent naming conventions

---

## Security Best Practices

1. ✅ **Never commit** secrets, API keys, or passwords
2. ✅ **Validate all input** on both frontend and backend
3. ✅ **Sanitize user input** to prevent XSS
4. ✅ **Use parameterized queries** to prevent SQL injection
5. ✅ **Implement rate limiting** on API endpoints
6. ✅ **Use HTTPS** everywhere
7. ✅ **Keep dependencies updated** (run `npm audit` regularly)

---

## Performance Guidelines

1. ✅ **Lazy load** routes and heavy components
2. ✅ **Memoize** expensive computations (useMemo, useCallback)
3. ✅ **Debounce** search inputs and frequent events
4. ✅ **Optimize images** and use modern formats (WebP, AVIF)
5. ✅ **Code split** large bundles
6. ✅ **Index** database queries properly
7. ✅ **Cache** API responses when appropriate

---

**Last Updated**: [Date]
**Version**: 1.0
