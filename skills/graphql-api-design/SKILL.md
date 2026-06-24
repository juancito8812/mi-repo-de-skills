---
name: graphql-api-design
description: Use when designing, reviewing, or refactoring GraphQL APIs to enforce consistent schema design, resolver patterns, N+1 prevention, auth, pagination via connections, and error handling. Triggers on GraphQL schemas, SDL files, resolvers, type definitions, or any GraphQL interface definition.
version: "1.0.0"
license: MIT
metadata:
  author: juancito8812
  languages: typescript, python
---

# GraphQL API Design

## Checklist

- [ ] Schema uses clear, consistent naming (PascalCase for types, camelCase for fields)
- [ ] Queries return what they name (no surprise fields)
- [ ] Mutations return a payload type with the mutated resource
- [ ] N+1 queries prevented with DataLoader or similar batching
- [ ] Auth enforced at resolver or schema level (not in business logic)
- [ ] Errors use structured error types (not just null on error)
- [ ] Pagination uses Relay Connection spec (edges, node, pageInfo)
- [ ] Input types defined for mutations with 2+ fields
- [ ] Subscriptions use clear event names and payload types

## When to Use

- Designing a new GraphQL schema from scratch
- Reviewing schema design for consistency, performance, or security
- Refactoring resolvers plagued by N+1 queries
- Defining mutations with proper input and payload types
- Implementing pagination for list fields
- Setting up authentication and authorization in GraphQL
- Migrating from REST to GraphQL

## When NOT to Use

- Simple CRUD APIs with fixed data requirements (use REST)
- When file uploads or binary data dominate (REST handles these better)
- Teams unfamiliar with GraphQL's caching and complexity trade-offs

## Core Rules

### 1. Schema Naming

```graphql
# ✅ Correct
type User {
  id: ID!
  fullName: String!
  email: String!
  posts(first: Int = 10, after: String): PostConnection!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  body: String!
  author: User!
}

# ❌ Incorrect
type user {
  id: ID!
  full_name: String!       # snake_case in schema
  email: String!
  getPosts: [Post]!         # verb prefix
  created_at: DateTime!     # snake_case
}
```

- **Types**: PascalCase (`User`, `PostConnection`)
- **Fields**: camelCase (`fullName`, `createdAt`)
- **Enums**: PascalCase with SCREAMING_SNAKE_CASE values

```graphql
enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

enum UserRole {
  ADMIN
  MODERATOR
  USER
}
```

⚠️ **Never** remove or rename enum values once published — clients may depend on them. Only append new values.
- **Inputs**: PascalCase + `Input` suffix (`CreatePostInput`)
- **Payloads**: PascalCase + `Payload` suffix (`CreatePostPayload`) or just the resource name

### 2. Queries & Mutations

```graphql
type Query {
  # Single resource by unique identifier
  user(id: ID!): User
  post(id: ID!): Post

  # Collections with pagination
  users(first: Int, after: String, query: String): UserConnection!
  posts(first: Int, after: String, status: PostStatus): PostConnection!

  # No verbs — GraphQL queries are inherently fetching
  # ❌ getUser(id: ID!): User
  # ✅ user(id: ID!): User
}

type Mutation {
  # Verb + resource
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeleteUserPayload!

  # ❌ userCreate(input: ...) — inconsistent word order
  # ✅ createUser(input: ...)
}
```

- **Queries** are nouns — the fact that you're reading is implied
- **Mutations** are verb+noun — explicit that you're writing
- **Always return a payload type** from mutations so you can add fields later
- **Every mutation input type** should be non-null (`!`)
- **List the mutated resource** in the payload for immediate refetch

### 3. Mutation Payloads

```graphql
# ✅ Good — extensible payload
type CreateUserPayload {
  user: User!
  query: Query!  # Enables batched mutations
}

# ❌ Bad — returns the type directly, cannot extend
# createUser(input: ...): User!
```

Include `query: Query!` in mutation payloads for [Relay-compatible batched mutations](https://relay.dev/docs/guided-tour/mutations/):

```graphql
mutation {
  createUser(input: { name: "Alice" }) {
    user { id fullName }
    query {  # Enables further reads in same round-trip
      users(first: 5) { edges { node { id fullName } } }
    }
  }
}
```

### 4. Pagination — Relay Connection Spec

```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Query {
  users(first: Int!, after: String, last: Int, before: String): UserConnection!
}
```

- **Always** use the Relay Connection spec for list fields
- `first`/`after` for forward pagination, `last`/`before` for backward
- Enforce a **maximum** `first`/`last` (e.g., 100)
- Return `hasNextPage`/`hasPreviousPage` so clients know when to stop
- **Never** return raw arrays without pagination
- ⚠️ **Exception:** Only omit pagination for fields guaranteed to return ≤ ~50 items (e.g., `user.roles`)

### 5. Resolvers & DataLoader (N+1 Prevention)

```typescript
// ❌ N+1 — one query per item
const resolvers = {
  Post: {
    author: async (post) => {
      return db.users.findById(post.authorId); // 1 query per post
    },
  },
};

// ✅ Batched with DataLoader
import DataLoader from 'dataloader';

const userLoader = new DataLoader(async (ids: readonly string[]) => {
  const users = await db.users.findByIds(ids); // 1 query total
  return ids.map((id) => users.find((u) => u.id === id));
});

const resolvers = {
  Post: {
    author: (post) => userLoader.load(post.authorId),
  },
};
```

- **Always use DataLoader** for any resolver that fetches related resources
- Create a **new DataLoader per request** (context-based) to prevent stale cache
- DataLoader batches and deduplicates — two `Post` with same `authorId` → 1 DB call

### 6. Error Handling

```graphql
# ✅ Structured error types
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}

type CreateUserPayload {
  user: User
  errors: [UserError!]!
}

type UserError {
  field: String!
  code: String!
  message: String!
}
```

```typescript
// ✅ Resolver with structured errors
const resolvers = {
  Mutation: {
    createUser: async (_, { input }, context) => {
      const errors: UserError[] = [];

      if (!isValidEmail(input.email)) {
        errors.push({ field: 'email', code: 'INVALID_FORMAT', message: 'Must be a valid email' });
      }
      if (input.name.length < 2) {
        errors.push({ field: 'name', code: 'TOO_SHORT', message: 'Must be at least 2 characters' });
      }

      if (errors.length > 0) {
        return { user: null, errors };
      }

      try {
        const user = await createUser(input);
        return { user, errors: [] };
      } catch (err) {
        if (err instanceof DuplicateEmailError) {
          return { user: null, errors: [{ field: 'email', code: 'DUPLICATE', message: 'Email already exists' }] };
        }
        throw err; // Let global error handler catch unexpected errors
      }
    },
  },
};
```

- **Return errors in the payload**, don't throw on validation failures
- Throwing should be reserved for unexpected/internal errors (caught by a global format)
- Use a consistent `errors: [Error!]!` field on every mutation payload
- The `field` property links the error to the input field for client-side form mapping

### 7. Authentication & Authorization

```typescript
import { GraphQLError } from 'graphql';

// Auth at the context level
const server = new ApolloServer({
  context: async ({ req }) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) return { user: null };
    try {
      const user = await verifyToken(token);
      return { user };
    } catch {
      return { user: null };
    }
  },
});

// Authorization at the resolver level
const resolvers = {
  Query: {
    drafts: async (_, __, { user }) => {
      if (!user) throw new GraphQLError('Not authenticated', { extensions: { code: 'UNAUTHENTICATED' } });
      return db.posts.findByAuthorId(user.id);
    },
  },
  Post: {
    body: async (post, _, { user }) => {
      if (post.status === 'draft' && post.authorId !== user?.id) {
        return null; // Hide draft content from non-authors
      }
      return post.body;
    },
  },
};
```

- **Authentication** at the context/transport layer (verify token once)
- **Authorization** at the resolver layer (field-level checks)
- Return `null` or throw a structured error for unauthorized access
- Use directive-based auth (`@auth`, `@hasRole`) for coarse-grained control; resolver-level for fine-grained

### 8. Subscriptions

```graphql
type Subscription {
  # VerbNoun in past tense — event already happened
  postCreated: PostCreatedPayload!
  postUpdated(userId: ID): PostUpdatedPayload!
  notificationReceived(userId: ID!): NotificationPayload!

  # ❌ onPostCreate — prefix is unnecessary
  # ✅ postCreated — past tense, clear
}

type PostCreatedPayload {
  post: Post!
  publishedBy: User!
}

type PostUpdatedPayload {
  post: Post!
  changedFields: [String!]!
}
```

- Use **past tense** for subscription names (`postCreated`, not `onPostCreate`)
- Always define a **payload type** (same as mutations)
- Include a filter argument (`userId: ID`) to scope events server-side
- **Never** send raw domain events to clients — always wrap in a typed payload
- Document which events trigger each subscription in the schema description

### 9. Query Complexity & Depth Limiting

For production GraphQL APIs, prevent abusive queries:

```typescript
import depthLimit from 'graphql-depth-limit';
import { createComplexityRule, simpleEstimator } from 'graphql-query-complexity';

const server = new ApolloServer({
  validationRules: [
    depthLimit(10),                      // Max nesting: 10 levels
    createComplexityRule({
      estimators: [simpleEstimator({ defaultComplexity: 1 })],
      maximumComplexity: 1000,           // Max total cost
      onComplete: (cost) => console.log(`Query cost: ${cost}`),
    }),
  ],
});
```

- **Depth limit**: prevents massively nested queries (e.g., `user → posts → author → posts → ...`)
- **Complexity limit**: assigns a cost to each field, rejects queries over the limit
- Without limits, a single query can cause a denial-of-service by requesting thousands of related records

### 10. Input Types

```graphql
# ✅ Always define an input type for mutations with 2+ fields
input CreateUserInput {
  fullName: String!
  email: String!
  age: Int
  avatar: Upload
}

input UpdateUserInput {
  fullName: String
  email: String
  age: Int
}

input UserFilter {
  query: String
  status: UserStatus
  createdAtRange: DateRangeInput
}

input DateRangeInput {
  gte: DateTime
  lte: DateTime
}
```

- **All required fields** in create inputs should be non-null
- **All fields** in update inputs should be nullable (partial updates)
- Reuse input types across queries (filters) and mutations (create/update)
- Use `Upload` scalar from `graphql-upload` package (`npm install graphql-upload`) for file uploads — requires special Apollo Server or Express middleware setup

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Returning raw arrays without pagination | Wrap in Connection type with edges, node, pageInfo |
| N+1 queries from field resolvers | Add DataLoader for every relation fetch |
| Exposing internal errors to client | Return structured errors in payload, throw only for 5xx |
| Mutations return the type directly | Return a payload type for extensibility |
| No input type for mutations | Define `Input` type for every mutation with 2+ fields |
| Using verbs in query names | Queries are nouns: `user(id:)` not `getUser(id:)` |
| Deeply nested queries without complexity limits | Implement query depth/complexity limiting |
| No auth on resolver level | Context-level auth + resolver-level authorization |
| Enum values changing after release | Always append new enum values, never remove or rename |

## Exit Criteria

- [ ] Schema naming consistent (PascalCase types, camelCase fields)
- [ ] All list fields use Relay Connection pagination (except small guaranteed lists)
- [ ] DataLoader implemented for all relation resolvers
- [ ] Mutation payloads include the resource and `errors` array
- [ ] Auth enforced at context (authentication) and resolver (authorization) levels
- [ ] Input types defined for all mutations with 2+ fields
- [ ] Enum values stable — only appended, never removed
- [ ] Query complexity/depth limits in place for production
