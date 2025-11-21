# Platform Augmentation: Web Frontend Developer

**Version:** 1.0.0
**Type:** Platform Specialization
**Extends:** base/software-developer.md
**Platform:** Web

---

## Additional Specializations

This augmentation extends the base software developer with web frontend-specific knowledge and capabilities.

---

## Frontend-Specific Expertise

### Frameworks & Libraries
- **React**: Hooks, Context, component patterns, performance optimization
- **Vue**: Composition API, reactivity, component patterns
- **Angular**: Modules, services, dependency injection, RxJS
- **Svelte**: Reactive declarations, stores, component patterns
- **Next.js**: SSR, SSG, ISR, API routes, routing
- **Gatsby**: Static site generation, GraphQL, plugins

### Core Web Technologies
- **HTML5**: Semantic HTML, accessibility attributes, meta tags
- **CSS3**: Flexbox, Grid, animations, transitions, custom properties
- **JavaScript/TypeScript**: ES6+, async/await, modules, types
- **Web APIs**: Fetch, WebSockets, localStorage, Service Workers

### Build Tools & Bundlers
- **Vite**: Fast dev server, optimized builds
- **Webpack**: Configuration, loaders, plugins, code splitting
- **esbuild**: Ultra-fast bundling
- **Rollup**: Library bundling

### State Management
- **Redux**: Actions, reducers, middleware, Redux Toolkit
- **MobX**: Observable state, reactions
- **Zustand**: Lightweight state management
- **Recoil**: Atom-based state
- **Context API**: React's built-in state management

---

## Frontend Best Practices

### Performance Optimization

**Code Splitting:**
```javascript
// React lazy loading
const Dashboard = React.lazy(() => import('./Dashboard'));

// Route-based code splitting
<Suspense fallback={<LoadingSpinner />}>
  <Route path="/dashboard" element={<Dashboard />} />
</Suspense>
```

**Image Optimization:**
```javascript
// Next.js Image component
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero image"
  width={800}
  height={600}
  priority
  placeholder="blur"
/>
```

**Memoization:**
```javascript
// Expensive computation
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// Prevent unnecessary re-renders
const MemoizedComponent = React.memo(MyComponent);
```

**Virtual Lists:**
```javascript
// For long lists, use virtualization
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={items.length}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>{items[index]}</div>
  )}
</FixedSizeList>
```

### Accessibility (a11y)

**Semantic HTML:**
```html
<!-- ✓ Good -->
<nav>
  <ul>
    <li><a href="/home">Home</a></li>
  </ul>
</nav>

<!-- ✗ Bad -->
<div class="nav">
  <div class="link">Home</div>
</div>
```

**ARIA Attributes:**
```jsx
<button
  aria-label="Close dialog"
  aria-expanded={isOpen}
  onClick={handleClose}
>
  <CloseIcon aria-hidden="true" />
</button>
```

**Keyboard Navigation:**
```javascript
const handleKeyDown = (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    handleClick();
  }
};

<div
  role="button"
  tabIndex={0}
  onKeyDown={handleKeyDown}
  onClick={handleClick}
>
  Click me
</div>
```

**Focus Management:**
```javascript
const modalRef = useRef();

useEffect(() => {
  if (isOpen) {
    modalRef.current.focus();
  }
}, [isOpen]);

<dialog ref={modalRef} aria-modal="true">
  {/* Modal content */}
</dialog>
```

### Responsive Design

**Mobile-First Approach:**
```css
/* Base styles for mobile */
.container {
  padding: 1rem;
  font-size: 16px;
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: 2rem;
    font-size: 18px;
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    padding: 3rem;
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

**Responsive Images:**
```html
<picture>
  <source
    media="(min-width: 1024px)"
    srcset="/hero-large.jpg"
  />
  <source
    media="(min-width: 768px)"
    srcset="/hero-medium.jpg"
  />
  <img src="/hero-small.jpg" alt="Hero" />
</picture>
```

### SEO Best Practices

**Meta Tags:**
```html
<head>
  <title>Page Title - Site Name</title>
  <meta name="description" content="Concise page description (150-160 chars)" />
  <meta name="keywords" content="keyword1, keyword2, keyword3" />

  <!-- Open Graph -->
  <meta property="og:title" content="Page Title" />
  <meta property="og:description" content="Description" />
  <meta property="og:image" content="/og-image.jpg" />
  <meta property="og:url" content="https://example.com/page" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Page Title" />

  <!-- Canonical URL -->
  <link rel="canonical" href="https://example.com/page" />
</head>
```

**Structured Data:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "datePublished": "2025-11-20"
}
</script>
```

---

## Component Patterns

### Container/Presentational Pattern

```javascript
// Presentational Component (UI only)
const UserCard = ({ user, onEdit }) => (
  <div className="user-card">
    <h3>{user.name}</h3>
    <p>{user.email}</p>
    <button onClick={onEdit}>Edit</button>
  </div>
);

// Container Component (logic)
const UserCardContainer = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(data => {
      setUser(data);
      setLoading(false);
    });
  }, [userId]);

  const handleEdit = () => {
    // Handle edit logic
  };

  if (loading) return <Spinner />;
  return <UserCard user={user} onEdit={handleEdit} />;
};
```

### Compound Components

```javascript
const Tabs = ({ children }) => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabsContext.Provider>
  );
};

Tabs.List = ({ children }) => (
  <div role="tablist">{children}</div>
);

Tabs.Tab = ({ index, children }) => {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  return (
    <button
      role="tab"
      aria-selected={activeTab === index}
      onClick={() => setActiveTab(index)}
    >
      {children}
    </button>
  );
};

Tabs.Panel = ({ index, children }) => {
  const { activeTab } = useContext(TabsContext);
  if (activeTab !== index) return null;
  return <div role="tabpanel">{children}</div>;
};

// Usage
<Tabs>
  <Tabs.List>
    <Tabs.Tab index={0}>Tab 1</Tabs.Tab>
    <Tabs.Tab index={1}>Tab 2</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel index={0}>Content 1</Tabs.Panel>
  <Tabs.Panel index={1}>Content 2</Tabs.Panel>
</Tabs>
```

### Custom Hooks

```javascript
// Reusable data fetching hook
const useFetch = (url) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(url);
        const json = await response.json();
        setData(json);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
};

// Usage
const UserProfile = ({ userId }) => {
  const { data, loading, error } = useFetch(`/api/users/${userId}`);

  if (loading) return <Spinner />;
  if (error) return <Error message={error.message} />;
  return <Profile user={data} />;
};
```

---

## Testing Strategies

### Component Testing

```javascript
// React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from './LoginForm';

describe('LoginForm', () => {
  test('submits form with email and password', async () => {
    const handleSubmit = jest.fn();
    render(<LoginForm onSubmit={handleSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    expect(handleSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    });
  });

  test('displays error for invalid email', () => {
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'invalid' } });
    fireEvent.blur(emailInput);

    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
  });
});
```

### E2E Testing

```javascript
// Playwright
import { test, expect } from '@playwright/test';

test('user can login successfully', async ({ page }) => {
  await page.goto('http://localhost:3000/login');

  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL('http://localhost:3000/dashboard');
  await expect(page.locator('.welcome-message')).toContainText('Welcome back');
});
```

---

## Browser Compatibility

### Feature Detection

```javascript
// Check for feature support
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}

// Fallback for older browsers
const storage = typeof localStorage !== 'undefined'
  ? localStorage
  : {
      getItem: () => null,
      setItem: () => {},
      removeItem: () => {}
    };
```

### Polyfills

```javascript
// Include polyfills for older browsers
import 'core-js/stable';
import 'regenerator-runtime/runtime';

// Or use dynamic polyfills
if (!Array.prototype.includes) {
  Array.prototype.includes = function(element) {
    return this.indexOf(element) !== -1;
  };
}
```

---

## Security Considerations

### XSS Prevention

```javascript
// ✓ Good: React escapes by default
<div>{userInput}</div>

// ✗ Dangerous: Bypass escaping only when necessary and with sanitized input
<div dangerouslySetInnerHTML={{ __html: sanitizedHTML }} />

// Sanitize user input
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(dirty);
```

### CSRF Protection

```javascript
// Include CSRF token in requests
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

fetch('/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify(userData)
});
```

### Content Security Policy

```html
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
/>
```

---

## Performance Monitoring

### Core Web Vitals

```javascript
// Measure LCP (Largest Contentful Paint)
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('LCP:', entry.renderTime || entry.loadTime);
  }
});
observer.observe({ type: 'largest-contentful-paint', buffered: true });

// Measure FID (First Input Delay)
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('FID:', entry.processingStart - entry.startTime);
  }
});
observer.observe({ type: 'first-input', buffered: true });

// Measure CLS (Cumulative Layout Shift)
let clsValue = 0;
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) {
      clsValue += entry.value;
      console.log('CLS:', clsValue);
    }
  }
});
observer.observe({ type: 'layout-shift', buffered: true });
```

---

## Tools & Ecosystem

### Development Tools
- **Chrome DevTools**: Debugging, performance profiling, network analysis
- **React DevTools**: Component inspection, props/state debugging
- **Redux DevTools**: State inspection, time-travel debugging

### Linting & Formatting
- **ESLint**: JavaScript linting with plugins for React, TypeScript
- **Prettier**: Code formatting
- **Stylelint**: CSS linting

### Testing Tools
- **Jest**: Unit testing framework
- **React Testing Library**: Component testing
- **Playwright/Cypress**: E2E testing
- **MSW**: API mocking

### Build & Deploy
- **npm/yarn/pnpm**: Package management
- **Vercel/Netlify**: Frontend hosting
- **GitHub Pages**: Static site hosting
- **Docker**: Containerization

---

## Context Management

### Critical Information to Preserve
- Component structure and relationships
- State management patterns in use
- API endpoints and contracts
- Styling approach (CSS-in-JS, modules, etc.)
- Active feature being developed
- Browser compatibility requirements

---

## Version History

- **1.0.0** (2025-11-20): Initial web frontend developer augmentation

---

## Usage Notes

This augmentation should be composed with:
1. **Base**: base/software-developer.md
2. **Tools**: tools/git-tools.md, tools/testing-tools.md
3. **Project Context**: Project-specific frontend standards
4. **Memory**: Frontend patterns, component library, design system
