---
name: restful-api-design
description: Use when designing, reviewing, or refactoring REST APIs to enforce consistent resource naming, HTTP semantics, error formats, pagination, versioning, and security patterns. Triggers on endpoints, routes, controllers, API specs, or any HTTP interface definition.
version: "1.0.0"
license: MIT
metadata:
  author: juancito8812
  languages: typescript, python
---

# RESTful API Design

## Checklist

- [ ] Resources named as plural nouns (`/users`, not `/getUser`)
- [ ] HTTP methods map to CRUD semantics (GET=read, POST=create, PUT=replace, PATCH=update, DELETE=delete)
- [ ] Status codes are specific and correct (200, 201, 204, 400, 401, 403, 404, 409, 422, 500)
- [ ] Error responses follow a consistent schema (code, message, details)
- [ ] Pagination implemented for list endpoints (cursor or offset)
- [ ] Versioning strategy defined (URL prefix or header)
- [ ] Authentication enforced on all private endpoints
- [ ] Input validation with clear error messages
- [ ] OpenAPI/Swagger spec exists and stays in sync

## When to Use

- Designing a new API from scratch
- Reviewing an existing API for consistency and correctness
- Refactoring routes, controllers, or request handlers
- Defining API contracts between frontend and backend teams
- Writing OpenAPI/Swagger specifications
- Debugging integration issues caused by non-standard APIs

## Core Rules

### 1. Resource Naming

| ✅ Correct | ❌ Incorrect |
|------------|-------------|
| `GET /users` | `GET /getUsers` |
| `GET /users/:id` | `GET /user?id=123` |
| `POST /users` | `POST /createUser` |
| `GET /users/:id/orders` | `GET /getUserOrders` |
| `PATCH /users/:id` | `POST /updateUser` |

- Use **plural nouns** for collections
- Use **kebab-case** for multi-word resources: `/order-items`
- Nest to show ownership: `/users/:id/orders/:orderId`
- **Avoid nesting deeper than 3 levels** — flatten with query params instead
- Use **query params** for filtering, sorting, and pagination: `GET /orders?status=pending&sort=created_at`

### 2. HTTP Methods & Status Codes

| Method | Action | Success | Failure |
|--------|--------|---------|---------|
| `GET` | Read | `200 OK` | `404 Not Found` |
| `POST` | Create | `201 Created` | `400 Bad Request`, `409 Conflict`, `422 Unprocessable` |
| `PUT` | Full replace | `200 OK` | `400`, `404`, `409`, `422` |
| `PATCH` | Partial update | `200 OK` | `400`, `404`, `409`, `422` |
| `DELETE` | Delete | `204 No Content` | `404 Not Found` |

```typescript
// Example: Express-like route definitions
router.get('/users',          listUsers);      // 200
router.post('/users',         createUser);      // 201
router.get('/users/:id',      getUser);         // 200 | 404
router.patch('/users/:id',    updateUser);      // 200 | 404 | 422
router.delete('/users/:id',   deleteUser);      // 204 | 404
```

**Key rules:**
- `POST` for creation returns `201` (not `200`) with a `Location` header pointing to the new resource
- `DELETE` returns `204` with no body (not `200` with empty body)
- `PUT` replaces the **entire** resource; missing fields are reset to defaults
- `PATCH` applies partial changes; only send the fields being modified

### 3. Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request body contains invalid fields",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Must be a valid email address"
      },
      {
        "field": "age",
        "code": "MINIMUM",
        "message": "Must be at least 18",
        "value": 15
      }
    ],
    "requestId": "req_abc123"
  }
}
```

- Use a **consistent error envelope** across all endpoints
- Include a machine-readable `code` for programmatic handling
- Include a human-readable `message` for debugging
- Add `details` array for field-level validation errors
- Include `requestId` for traceability in logs

### 4. Pagination

```json
// Request
GET /users?page=2&per_page=25

// Response
{
  "data": [],
  "pagination": {
    "page": 2,
    "perPage": 25,
    "total": 142,
    "totalPages": 6,
    "hasNext": true,
    "hasPrev": true
  }
}
```

Prefer **cursor-based pagination** for real-time or high-throughput APIs:
```json
GET /events?cursor=abc123&limit=25

{
  "data": [],
  "pagination": {
    "cursor": "xyz789",
    "hasMore": true
  }
}
```

- Always include `hasMore`/`hasNext` so clients know when to stop
- Set a **maximum** `per_page` (e.g., 100) to prevent abuse
- Default to a reasonable page size (25-50)

### 5. Versioning

```text
# URL prefix (recommended)
GET /v1/users
GET /v2/users

# Or Accept header
Accept: application/vnd.api+json; version=2
```

- URL prefix is simpler and more visible — **prefer `/v1/`, `/v2/`**
- Never remove a version without a deprecation notice and migration window
- Document deprecation in the `Deprecation` and `Sunset` HTTP headers

### 6. Filtering & Sorting

```text
# Filtering
GET /orders?status=active
GET /orders?status=active,completed
GET /orders?created_at[gte]=2024-01-01&created_at[lte]=2024-12-31

# Sorting
GET /orders?sort=created_at
GET /orders?sort=-created_at          # descending
GET /orders?sort=status,created_at    # multi-field
```

## Example: Complete Endpoint

```typescript
import { Router, Request, Response } from 'express';

const router = Router();

interface CreateUserBody {
  email: string;
  name: string;
  age: number;
}

router.post('/users', async (req: Request, res: Response) => {
  const { email, name, age } = req.body as CreateUserBody;
  const errors: Array<{ field: string; code: string; message: string }> = [];

  // Validation
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.push({ field: 'email', code: 'INVALID_FORMAT', message: 'Must be a valid email' });
  }
  if (!name || name.length < 2) {
    errors.push({ field: 'name', code: 'TOO_SHORT', message: 'Name must be at least 2 characters' });
  }
  if (typeof age !== 'number' || age < 18) {
    errors.push({ field: 'age', code: 'MINIMUM', message: 'Must be at least 18' });
  }

  if (errors.length > 0) {
    return res.status(422).json({
      error: { code: 'VALIDATION_ERROR', message: 'Invalid request body', details: errors }
    });
  }

  try {
    const user = await createUser({ email, name, age });
    return res.status(201)
      .location(`/users/${user.id}`)
      .json({ data: user });
  } catch (err) {
    if (err instanceof DuplicateEmailError) {
      return res.status(409).json({
        error: { code: 'DUPLICATE_EMAIL', message: 'Email already registered' }
      });
    }
    throw err; // Let the global error handler catch unexpected errors
  }
});
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `GET /getUsers` or `POST /updateUser` | Use resource nouns, not RPC-style actions |
| Returning `200` for creation | Use `201 Created` with `Location` header |
| Returning `200` for deletion | Use `204 No Content` with no body |
| Inconsistent error format | Define a single error schema for all responses |
| Nesting deeper than 3 levels | Flatten with query params: `/users/:id/items` not `/a/:a/b/:b/c/:c/items` |
| No pagination on list endpoints | Always paginate — default to 25 items per page |
| Exposing internal error details | Return generic messages to clients, log full details server-side |
| No versioning strategy | Start with `/v1/` from day one — retrofitting is painful |
| PUT instead of PATCH | Use PUT for full replace, PATCH for partial update |

## Exit Criteria

- [ ] All endpoints use plural resource nouns with correct HTTP methods
- [ ] Status codes match the action (201 for create, 204 for delete, etc.)
- [ ] Error responses follow the consistent envelope format
- [ ] List endpoints include pagination with max page size enforced
- [ ] API version prefix (`/v1/`, `/v2/`) applied consistently
- [ ] Input validation with structured error responses
- [ ] Authentication enforced on non-public endpoints
- [ ] OpenAPI/Swagger spec documents the API contract
