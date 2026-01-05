# React Frontend Best Practices Reference

A concise reference guide for building modern React applications with Vite and Tailwind CSS.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Component Design](#2-component-design)
3. [State Management](#3-state-management)
4. [Data Fetching](#4-data-fetching)
5. [Forms & Validation](#5-forms--validation)
6. [Styling with Tailwind](#6-styling-with-tailwind)
7. [Performance](#7-performance)
8. [Hooks Patterns](#8-hooks-patterns)
9. [Routing](#9-routing)
10. [Error Handling](#10-error-handling)
11. [Testing](#11-testing)
12. [Accessibility](#12-accessibility)
13. [Anti-Patterns](#13-anti-patterns)

---

## 1. Project Structure

### Feature-Based Structure (Recommended)

```
src/
├── features/
│   ├── habits/
│   │   ├── components/
│   │   │   ├── HabitCard.jsx
│   │   │   ├── HabitForm.jsx
│   │   │   └── HabitList.jsx
│   │   ├── hooks/
│   │   │   └── useHabits.js
│   │   ├── api/
│   │   │   └── habits.js
│   │   └── index.js           # Public exports
│   └── calendar/
│       ├── components/
│       ├── hooks/
│       └── index.js
├── components/                 # Shared/common components
│   ├── ui/
│   │   ├── Button.jsx
│   │   ├── Card.jsx
│   │   └── Modal.jsx
│   └── layout/
│       ├── Header.jsx
│       └── Layout.jsx
├── hooks/                      # Shared hooks
│   └── useLocalStorage.js
├── lib/                        # Utilities
│   ├── api.js                  # API client
│   └── utils.js
├── pages/                      # Route pages
│   ├── Dashboard.jsx
│   └── HabitDetail.jsx
├── App.jsx
├── main.jsx
└── index.css
```

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `HabitCard.jsx` |
| Hooks | camelCase, `use` prefix | `useHabits.js` |
| Utilities | camelCase | `formatDate.js` |
| Constants | SCREAMING_SNAKE_CASE | `API_BASE_URL` |
| CSS/styles | kebab-case | `habit-card.css` |

### Barrel Exports

```javascript
// features/habits/index.js
export { HabitCard } from './components/HabitCard';
export { HabitForm } from './components/HabitForm';
export { useHabits } from './hooks/useHabits';

// Usage elsewhere
import { HabitCard, useHabits } from '@/features/habits';
```

**Note**: Barrel exports can hurt tree-shaking and build times in large projects. Use judiciously.

---

## 2. Component Design

### Functional Components

```jsx
// Simple component
function HabitCard({ habit, onComplete }) {
  return (
    <div className="p-4 border rounded">
      <h3>{habit.name}</h3>
      <button onClick={() => onComplete(habit.id)}>Complete</button>
    </div>
  );
}

// With default props
function HabitCard({ habit, onComplete, showStreak = true }) {
  // ...
}

// Destructure in parameters
function HabitCard({ habit: { id, name, streak }, onComplete }) {
  // ...
}
```

### Component Composition

```jsx
// Compound components pattern
function Card({ children, className }) {
  return <div className={`border rounded ${className}`}>{children}</div>;
}

Card.Header = function CardHeader({ children }) {
  return <div className="p-4 border-b font-bold">{children}</div>;
};

Card.Body = function CardBody({ children }) {
  return <div className="p-4">{children}</div>;
};

// Usage
<Card>
  <Card.Header>Habit Details</Card.Header>
  <Card.Body>Content here</Card.Body>
</Card>
```

### Props Design

```jsx
// Prefer specific props over spreading
// Good
function Button({ onClick, disabled, children, variant = 'primary' }) {
  return <button onClick={onClick} disabled={disabled}>{children}</button>;
}

// Avoid excessive spreading
// Bad - hard to know what props are accepted
function Button(props) {
  return <button {...props} />;
}

// Accept className for styling flexibility
function Card({ children, className = '' }) {
  return <div className={`base-styles ${className}`}>{children}</div>;
}
```

### Children Pattern

```jsx
// Children for composition
function Layout({ children }) {
  return (
    <div className="container mx-auto">
      <Header />
      <main>{children}</main>
      <Footer />
    </div>
  );
}

// Render props for more control
function HabitList({ habits, renderItem }) {
  return (
    <ul>
      {habits.map(habit => (
        <li key={habit.id}>{renderItem(habit)}</li>
      ))}
    </ul>
  );
}

// Usage
<HabitList
  habits={habits}
  renderItem={(habit) => <HabitCard habit={habit} />}
/>
```

---

## 3. State Management

### When to Use What

| State Type | Solution |
|------------|----------|
| Server/async data | TanStack Query |
| Form state | react-hook-form or useState |
| Local UI state | useState |
| Shared UI state | Context or Zustand |
| URL state | React Router |

### useState Best Practices

```jsx
// Group related state
const [habit, setHabit] = useState({ name: '', description: '' });

// vs multiple useState (fine for independent values)
const [name, setName] = useState('');
const [isOpen, setIsOpen] = useState(false);

// Functional updates for state based on previous value
setCount(prev => prev + 1);

// Initialize expensive state lazily
const [data, setData] = useState(() => expensiveComputation());
```

### Lifting State Up

```jsx
// Parent owns the state, children receive via props
function Dashboard() {
  const [selectedDate, setSelectedDate] = useState(new Date());

  return (
    <>
      <DatePicker date={selectedDate} onChange={setSelectedDate} />
      <HabitList date={selectedDate} />
      <Stats date={selectedDate} />
    </>
  );
}
```

### Context API

```jsx
// Create context
const HabitContext = createContext(null);

// Provider component
function HabitProvider({ children }) {
  const [habits, setHabits] = useState([]);

  const value = {
    habits,
    addHabit: (habit) => setHabits(prev => [...prev, habit]),
    removeHabit: (id) => setHabits(prev => prev.filter(h => h.id !== id)),
  };

  return (
    <HabitContext.Provider value={value}>
      {children}
    </HabitContext.Provider>
  );
}

// Custom hook for consuming context
function useHabitContext() {
  const context = useContext(HabitContext);
  if (!context) {
    throw new Error('useHabitContext must be used within HabitProvider');
  }
  return context;
}

// Usage
function HabitList() {
  const { habits, removeHabit } = useHabitContext();
  // ...
}
```

### Zustand (Simple Alternative to Redux)

```javascript
// store/habits.js
import { create } from 'zustand';

const useHabitStore = create((set) => ({
  selectedHabitId: null,
  filterStatus: 'all',
  setSelectedHabit: (id) => set({ selectedHabitId: id }),
  setFilter: (status) => set({ filterStatus: status }),
}));

// Usage in component
function HabitFilter() {
  const { filterStatus, setFilter } = useHabitStore();
  // ...
}
```

---

## 4. Data Fetching

### TanStack Query Setup

```jsx
// main.jsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router />
    </QueryClientProvider>
  );
}
```

### Basic Query

```javascript
// hooks/useHabits.js
import { useQuery } from '@tanstack/react-query';
import { fetchHabits } from '../api/habits';

export function useHabits() {
  return useQuery({
    queryKey: ['habits'],
    queryFn: fetchHabits,
  });
}

// Usage in component
function HabitList() {
  const { data: habits, isLoading, error } = useHabits();

  if (isLoading) return <Spinner />;
  if (error) return <Error message={error.message} />;

  return (
    <ul>
      {habits.map(habit => <HabitCard key={habit.id} habit={habit} />)}
    </ul>
  );
}
```

### Query with Parameters

```javascript
export function useHabit(habitId) {
  return useQuery({
    queryKey: ['habits', habitId],
    queryFn: () => fetchHabit(habitId),
    enabled: !!habitId, // Only run if habitId exists
  });
}

export function useCompletions(habitId, month) {
  return useQuery({
    queryKey: ['completions', habitId, month],
    queryFn: () => fetchCompletions(habitId, month),
  });
}
```

### Mutations

```javascript
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function useCreateHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createHabit,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['habits'] });
    },
  });
}

export function useCompleteHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ habitId, date }) => completeHabit(habitId, date),
    onSuccess: (_, { habitId }) => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      queryClient.invalidateQueries({ queryKey: ['completions', habitId] });
    },
  });
}

// Usage
function HabitCard({ habit }) {
  const { mutate: complete, isPending } = useCompleteHabit();

  return (
    <button
      onClick={() => complete({ habitId: habit.id, date: today })}
      disabled={isPending}
    >
      {isPending ? 'Saving...' : 'Complete'}
    </button>
  );
}
```

### Optimistic Updates

```javascript
export function useCompleteHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: completeHabit,
    onMutate: async ({ habitId, date }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['habits'] });

      // Snapshot previous value
      const previousHabits = queryClient.getQueryData(['habits']);

      // Optimistically update
      queryClient.setQueryData(['habits'], (old) =>
        old.map(h => h.id === habitId
          ? { ...h, completedToday: true, currentStreak: h.currentStreak + 1 }
          : h
        )
      );

      return { previousHabits };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      queryClient.setQueryData(['habits'], context.previousHabits);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
    },
  });
}
```

### API Client

```javascript
// lib/api.js
const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'An error occurred');
  }

  if (response.status === 204) return null;
  return response.json();
}

// api/habits.js
export const fetchHabits = () => request('/habits');
export const fetchHabit = (id) => request(`/habits/${id}`);
export const createHabit = (data) => request('/habits', { method: 'POST', body: JSON.stringify(data) });
export const completeHabit = (id, date) => request(`/habits/${id}/complete`, { method: 'POST', body: JSON.stringify({ date }) });
```

---

## 5. Forms & Validation

### React Hook Form + Zod

```jsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const habitSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  description: z.string().max(500).optional(),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/, 'Invalid color').default('#10B981'),
});

function HabitForm({ onSubmit, defaultValues }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm({
    resolver: zodResolver(habitSchema),
    defaultValues,
  });

  const handleFormSubmit = async (data) => {
    await onSubmit(data);
    reset();
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)}>
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          {...register('name')}
          className={errors.name ? 'border-red-500' : ''}
        />
        {errors.name && <span className="text-red-500">{errors.name.message}</span>}
      </div>

      <div>
        <label htmlFor="description">Description</label>
        <textarea id="description" {...register('description')} />
        {errors.description && <span className="text-red-500">{errors.description.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save'}
      </button>
    </form>
  );
}
```

### Simple Controlled Form

```jsx
function SimpleForm({ onSubmit }) {
  const [name, setName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Name is required');
      return;
    }
    onSubmit({ name });
    setName('');
    setError('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Habit name"
      />
      {error && <span className="text-red-500">{error}</span>}
      <button type="submit">Add</button>
    </form>
  );
}
```

---

## 6. Styling with Tailwind

### Vite Configuration

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});

// tailwind.config.js
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#10B981',
      },
    },
  },
  plugins: [],
};

// src/index.css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Component Styling Patterns

```jsx
// Inline classes
function Button({ children, variant = 'primary' }) {
  const baseClasses = 'px-4 py-2 rounded font-medium transition-colors';
  const variantClasses = {
    primary: 'bg-primary text-white hover:bg-primary/90',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-500 text-white hover:bg-red-600',
  };

  return (
    <button className={`${baseClasses} ${variantClasses[variant]}`}>
      {children}
    </button>
  );
}

// Using clsx for conditional classes
import clsx from 'clsx';

function HabitCard({ habit, isCompleted }) {
  return (
    <div className={clsx(
      'p-4 border rounded',
      isCompleted && 'bg-green-50 border-green-200',
      !isCompleted && 'bg-white border-gray-200'
    )}>
      {habit.name}
    </div>
  );
}
```

### Responsive Design

```jsx
// Mobile-first approach
<div className="
  p-2 md:p-4 lg:p-6
  grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4
  text-sm md:text-base
">
  {/* Content */}
</div>

// Breakpoints: sm(640px) md(768px) lg(1024px) xl(1280px) 2xl(1536px)
```

### Common Patterns

```jsx
// Card
<div className="bg-white rounded-lg shadow-md p-4">

// Flex centering
<div className="flex items-center justify-center">

// Grid layout
<div className="grid grid-cols-7 gap-1">

// Truncate text
<p className="truncate">Long text...</p>

// Focus ring
<button className="focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2">

// Disabled state
<button className="disabled:opacity-50 disabled:cursor-not-allowed" disabled={isPending}>
```

---

## 7. Performance

### React.memo

```jsx
// Only re-renders when props change
const HabitCard = memo(function HabitCard({ habit, onComplete }) {
  return (
    <div>
      <h3>{habit.name}</h3>
      <button onClick={() => onComplete(habit.id)}>Complete</button>
    </div>
  );
});

// Custom comparison
const HabitCard = memo(function HabitCard({ habit, onComplete }) {
  // ...
}, (prevProps, nextProps) => {
  return prevProps.habit.id === nextProps.habit.id &&
         prevProps.habit.completedToday === nextProps.habit.completedToday;
});
```

### useCallback and useMemo

```jsx
// useCallback - memoize functions passed to child components
function HabitList({ habits }) {
  const handleComplete = useCallback((id) => {
    // ...
  }, []); // Empty deps = stable reference

  return habits.map(h => (
    <HabitCard key={h.id} habit={h} onComplete={handleComplete} />
  ));
}

// useMemo - memoize expensive calculations
function Stats({ completions }) {
  const stats = useMemo(() => {
    return calculateExpensiveStats(completions);
  }, [completions]);

  return <div>{stats.average}</div>;
}
```

**When to use**:
- `useCallback`: Functions passed to memoized children
- `useMemo`: Expensive calculations, referential equality for deps

**When NOT to use**:
- Simple calculations
- Primitive values
- Functions not passed to children

### Code Splitting

```jsx
import { lazy, Suspense } from 'react';

// Lazy load routes
const Settings = lazy(() => import('./pages/Settings'));
const Analytics = lazy(() => import('./pages/Analytics'));

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Suspense>
  );
}
```

### List Virtualization

```jsx
// For very long lists (1000+ items), use react-window
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }) {
  return (
    <FixedSizeList
      height={400}
      width="100%"
      itemCount={items.length}
      itemSize={50}
    >
      {({ index, style }) => (
        <div style={style}>{items[index].name}</div>
      )}
    </FixedSizeList>
  );
}
```

---

## 8. Hooks Patterns

### Custom Hooks

```javascript
// useLocalStorage
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}

// useDebounce
function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// useToggle
function useToggle(initialValue = false) {
  const [value, setValue] = useState(initialValue);
  const toggle = useCallback(() => setValue(v => !v), []);
  return [value, toggle];
}
```

### useEffect Patterns

```jsx
// Cleanup function
useEffect(() => {
  const controller = new AbortController();

  fetch('/api/data', { signal: controller.signal })
    .then(res => res.json())
    .then(setData);

  return () => controller.abort(); // Cleanup on unmount
}, []);

// Event listeners
useEffect(() => {
  const handleResize = () => setWidth(window.innerWidth);
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);

// Sync with external system
useEffect(() => {
  const subscription = externalStore.subscribe(setData);
  return () => subscription.unsubscribe();
}, []);
```

### useEffect Pitfalls

```jsx
// BAD: Missing dependency
useEffect(() => {
  fetchData(userId); // userId not in deps - stale closure
}, []);

// GOOD: Include all dependencies
useEffect(() => {
  fetchData(userId);
}, [userId]);

// BAD: Object/array in deps (new reference every render)
useEffect(() => {
  doSomething(options); // options = {} creates new object each render
}, [options]);

// GOOD: Memoize or use primitive values
const memoizedOptions = useMemo(() => options, [options.key1, options.key2]);
useEffect(() => {
  doSomething(memoizedOptions);
}, [memoizedOptions]);
```

---

## 9. Routing

### React Router v6 Setup

```jsx
// App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="habits/:habitId" element={<HabitDetail />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

### Layout Route

```jsx
// Layout.jsx
import { Outlet, Link } from 'react-router-dom';

function Layout() {
  return (
    <div className="min-h-screen">
      <nav className="bg-white shadow">
        <Link to="/">Dashboard</Link>
        <Link to="/settings">Settings</Link>
      </nav>
      <main className="container mx-auto p-4">
        <Outlet /> {/* Child routes render here */}
      </main>
    </div>
  );
}
```

### Route Parameters

```jsx
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';

function HabitDetail() {
  const { habitId } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const month = searchParams.get('month') || getCurrentMonth();

  return (
    <div>
      <button onClick={() => navigate('/')}>Back</button>
      <button onClick={() => setSearchParams({ month: 'next' })}>
        Next Month
      </button>
    </div>
  );
}
```

### Navigation

```jsx
import { Link, NavLink, useNavigate } from 'react-router-dom';

// Simple link
<Link to="/settings">Settings</Link>

// Active styling
<NavLink
  to="/"
  className={({ isActive }) => isActive ? 'text-primary' : 'text-gray-600'}
>
  Dashboard
</NavLink>

// Programmatic navigation
const navigate = useNavigate();
navigate('/habits/1');
navigate(-1); // Go back
navigate('/', { replace: true }); // Replace history
```

---

## 10. Error Handling

### Error Boundaries

```jsx
import { Component } from 'react';

class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
    // Send to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 text-red-500">
          <h2>Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>
```

### Async Error Handling

```jsx
function HabitList() {
  const { data, error, isError } = useHabits();

  if (isError) {
    return (
      <div className="p-4 bg-red-50 text-red-700 rounded">
        <p>Failed to load habits: {error.message}</p>
        <button onClick={() => refetch()}>Retry</button>
      </div>
    );
  }

  return <ul>{/* ... */}</ul>;
}
```

### Toast Notifications

```jsx
// Using a toast library like react-hot-toast
import toast from 'react-hot-toast';

function useCreateHabit() {
  return useMutation({
    mutationFn: createHabit,
    onSuccess: () => {
      toast.success('Habit created!');
    },
    onError: (error) => {
      toast.error(`Failed: ${error.message}`);
    },
  });
}
```

---

## 11. Testing

### Setup with Vitest

```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
  },
});

// src/test/setup.js
import '@testing-library/jest-dom';
```

### Component Testing

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('HabitCard', () => {
  it('renders habit name', () => {
    render(<HabitCard habit={{ id: 1, name: 'Exercise' }} />);
    expect(screen.getByText('Exercise')).toBeInTheDocument();
  });

  it('calls onComplete when button clicked', async () => {
    const onComplete = vi.fn();
    render(<HabitCard habit={{ id: 1, name: 'Exercise' }} onComplete={onComplete} />);

    await userEvent.click(screen.getByRole('button', { name: /complete/i }));

    expect(onComplete).toHaveBeenCalledWith(1);
  });
});
```

### Testing with Providers

```jsx
// test/utils.jsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
}

export function renderWithProviders(ui) {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {ui}
      </BrowserRouter>
    </QueryClientProvider>
  );
}
```

### Mocking API Calls

```jsx
import { vi } from 'vitest';
import * as api from '../api/habits';

vi.mock('../api/habits');

it('loads and displays habits', async () => {
  api.fetchHabits.mockResolvedValue([
    { id: 1, name: 'Exercise' },
  ]);

  renderWithProviders(<HabitList />);

  await waitFor(() => {
    expect(screen.getByText('Exercise')).toBeInTheDocument();
  });
});
```

---

## 12. Accessibility

### Semantic HTML

```jsx
// Use semantic elements
<header>...</header>
<nav>...</nav>
<main>...</main>
<article>...</article>
<aside>...</aside>
<footer>...</footer>

// Use headings properly (h1 > h2 > h3)
<h1>Dashboard</h1>
<section>
  <h2>Today's Habits</h2>
</section>
```

### ARIA Attributes

```jsx
// Labels
<button aria-label="Close modal">×</button>

// Live regions (for dynamic content)
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// States
<button aria-pressed={isCompleted}>Complete</button>
<button aria-expanded={isOpen}>Menu</button>

// Roles
<div role="alert">{errorMessage}</div>
```

### Focus Management

```jsx
// Focus trap in modals
function Modal({ isOpen, onClose, children }) {
  const modalRef = useRef();

  useEffect(() => {
    if (isOpen) {
      modalRef.current?.focus();
    }
  }, [isOpen]);

  return isOpen ? (
    <div
      ref={modalRef}
      tabIndex={-1}
      role="dialog"
      aria-modal="true"
      onKeyDown={(e) => e.key === 'Escape' && onClose()}
    >
      {children}
    </div>
  ) : null;
}
```

### Keyboard Navigation

```jsx
// Handle keyboard interactions
function ListItem({ onSelect }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={handleKeyDown}
    >
      Item
    </div>
  );
}
```

---

## 13. Anti-Patterns

### Common Mistakes

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Props drilling | Hard to maintain | Context or composition |
| Huge components | Hard to test/maintain | Split into smaller components |
| useEffect for derived state | Unnecessary complexity | Compute during render |
| Index as key | Bugs with reordering | Use stable unique IDs |
| Direct DOM manipulation | Conflicts with React | Use refs sparingly |

### Code Examples

```jsx
// BAD: Derived state in useEffect
const [fullName, setFullName] = useState('');
useEffect(() => {
  setFullName(`${firstName} ${lastName}`);
}, [firstName, lastName]);

// GOOD: Compute during render
const fullName = `${firstName} ${lastName}`;

// BAD: Index as key (causes bugs when list changes)
{items.map((item, index) => <Item key={index} item={item} />)}

// GOOD: Stable unique ID
{items.map(item => <Item key={item.id} item={item} />)}

// BAD: Fetching in useEffect without cleanup
useEffect(() => {
  fetch('/api/data').then(res => res.json()).then(setData);
}, []);

// GOOD: Use TanStack Query or add cleanup
useEffect(() => {
  let cancelled = false;
  fetch('/api/data')
    .then(res => res.json())
    .then(data => { if (!cancelled) setData(data); });
  return () => { cancelled = true; };
}, []);
```

---

## Quick Reference

### Common Imports

```jsx
// React
import { useState, useEffect, useCallback, useMemo, useRef, memo, createContext, useContext } from 'react';

// React Router
import { BrowserRouter, Routes, Route, Link, useParams, useNavigate } from 'react-router-dom';

// TanStack Query
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Form
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
```

---

## Resources

- [React Documentation](https://react.dev/)
- [TanStack Query](https://tanstack.com/query/latest)
- [React Router](https://reactrouter.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Hook Form](https://react-hook-form.com/)
- [Zod](https://zod.dev/)
