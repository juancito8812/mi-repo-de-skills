---
name: vercel-react-best-practices
description: React and Next.js performance optimization guidelines from Vercel Engineering. Use when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements.
license: MIT
version: "1.1.0"
metadata:
  author: vercel
  source: https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices
---

# Vercel React Best Practices

## Checklist

- [ ] Waterfall requests identified and parallelized
- [ ] Bundle size checked: no barrel imports, dynamic imports for heavy components
- [ ] Server components used where possible (no client-side fetching if server can do it)
- [ ] Re-renders optimized: memo, useMemo, useCallback where measured benefit
- [ ] No inline component definitions
- [ ] Suspense boundaries for async content
- [ ] Data serialized minimally to client

## When to Apply

Reference these guidelines when:
- Writing new React components or Next.js pages
- Implementing data fetching (client or server-side)
- Reviewing code for performance issues
- Refactoring existing React/Next.js code
- Optimizing bundle size or load times

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Eliminating Waterfalls | CRITICAL | `async-` |
| 2 | Bundle Size Optimization | CRITICAL | `bundle-` |
| 3 | Server-Side Performance | HIGH | `server-` |
| 4 | Client-Side Data Fetching | MEDIUM-HIGH | `client-` |
| 5 | Re-render Optimization | MEDIUM | `rerender-` |
| 6 | Rendering Performance | MEDIUM | `rendering-` |
| 7 | JavaScript Performance | LOW-MEDIUM | `js-` |
| 8 | Advanced Patterns | LOW | `advanced-` |

## Key Rules

### 1. Eliminating Waterfalls (CRITICAL)
- `async-parallel` — Use `Promise.all()` for independent operations
- `async-suspense-boundaries` — Use Suspense to stream content
- `async-defer-await` — Move await into branches where actually used
- `async-cheap-condition-before-await` — Check cheap conditions before awaiting

### 2. Bundle Size Optimization (CRITICAL)
- `bundle-barrel-imports` — Import directly, avoid barrel files
- `bundle-dynamic-imports` — Use `next/dynamic` for heavy components
- `bundle-analyzable-paths` — Prefer statically analyzable import paths
- `bundle-defer-third-party` — Load analytics/logging after hydration

### 3. Server-Side Performance (HIGH)
- `server-cache-react` — Use `React.cache()` for per-request deduplication
- `server-parallel-fetching` — Restructure components to parallelize fetches
- `server-serialization` — Minimize data passed to client components
- `server-after-nonblocking` — Use `after()` for non-blocking operations

### 4. Re-render Optimization (MEDIUM)
- `rerender-memo` — Extract expensive work into memoized components
- `rerender-derived-state` — Derive state during render, not effects
- `rerender-transitions` — Use `startTransition` for non-urgent updates
- `rerender-use-deferred-value` — Defer expensive renders
- `rerender-no-inline-components` — Don't define components inside components

### 5. Rendering Performance (MEDIUM)
- `rendering-content-visibility` — Use `content-visibility` for long lists
- `rendering-hoist-jsx` — Extract static JSX outside components
- `rendering-activity` — Use Activity component for show/hide

### 6. JavaScript Performance (LOW-MEDIUM)
- `js-set-map-lookups` — Use Set/Map for O(1) lookups
- `js-batch-dom-css` — Group CSS changes via classes or cssText
- `js-early-exit` — Return early from functions
- `js-hoist-regexp` — Hoist RegExp creation outside loops

## How to Use

For the complete guide with all 70 rules expanded, see the original source at `https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices`

## Performance Audit Steps

1. **Check waterfalls**: `Promise.all()` for parallel fetches, Suspense boundaries
2. **Check bundle**: dynamic imports for heavy libs, no barrel imports
3. **Check components**: no inline definitions, proper memo usage
4. **Check rendering**: `content-visibility` for lists, `startTransition` for non-urgent
5. **Check data flow**: minimize client data, cache server responses

## Exit Criteria

- [ ] No critical waterfalls identified
- [ ] Bundle size optimized (dynamic imports, no barrel files)
- [ ] Server/client split appropriate
- [ ] No unnecessary re-renders
- [ ] Performance measured before/after
