---
name: postgresql-table-design
description: Use this skill when designing or reviewing a PostgreSQL-specific schema. Covers best-practices, data types, indexing, constraints, performance patterns, and advanced features.
version: "1.1.0"
license: MIT
metadata:
  author: juancito8812
  database: postgresql
---

# PostgreSQL Table Design

## Checklist

- [ ] PRIMARY KEY defined (BIGINT IDENTITY or UUID)
- [ ] NOT NULL on all semantically required columns
- [ ] Foreign keys indexed manually
- [ ] Appropriate data types (TIMESTAMPTZ, NUMERIC, TEXT, JSONB)
- [ ] No banned types (timestamp, char(n), varchar(n), money, timetz, serial)
- [ ] Indexes for access paths (FK, filters, sorts, joins)
- [ ] Constraints defined (CHECK, UNIQUE, EXCLUDE as needed)

## Core Rules

- Define a **PRIMARY KEY** for reference tables. Prefer `BIGINT GENERATED ALWAYS AS IDENTITY`; use `UUID` only when global uniqueness/opacity is needed.
- **Normalize first (to 3NF)**; denormalize only for measured, high-ROI reads.
- Add **NOT NULL** everywhere semantically required; use **DEFAULT**s for common values.
- Create **indexes for access paths you query**: PK/unique (auto), **FK columns (manual!)**, frequent filters/sorts, join keys.
- Prefer **TIMESTAMPTZ** for event time; **NUMERIC** for money; **TEXT** for strings; **BIGINT** for integers.

## Data Types

- **IDs**: `BIGINT GENERATED ALWAYS AS IDENTITY` preferred; `UUID` for distributed/federated systems
- **Strings**: prefer `TEXT`; use `CHECK (LENGTH(col) <= n)` instead of `VARCHAR(n)`
- **Money**: `NUMERIC(p,s)` — never float
- **Time**: `TIMESTAMPTZ` for timestamps, `DATE` for date-only, `INTERVAL` for durations
- **JSONB**: preferred over JSON; index with **GIN**. Only for optional/semi-structured attrs
- **DO NOT use**: `timestamp`, `char(n)`, `varchar(n)`, `money`, `timetz`, `serial`

## Example DDL

```sql
CREATE TABLE orders (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(id),
    status      TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
    total       NUMERIC(10,2) NOT NULL CHECK (total >= 0),
    currency    TEXT NOT NULL DEFAULT 'USD',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata    JSONB
);

CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status) WHERE status = 'pending';
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
```

## Indexing

- **B-tree**: default for equality/range (`=`, `<`, `>`, `BETWEEN`, `ORDER BY`)
- **Composite**: order matters — most selective/filtered column first
- **Covering**: `CREATE INDEX ON tbl (id) INCLUDE (name, email)`
- **Partial**: for hot subsets (`WHERE status = 'active'`)
- **GIN**: JSONB containment (`@>`), arrays, full-text search
- **GiST**: ranges, geometry, exclusion constraints
- **BRIN**: very large, naturally ordered data (time-series)

## Table Types

- **Regular**: default, fully durable
- **TEMPORARY**: session-scoped, auto-dropped
- **UNLOGGED**: persistent but not crash-safe — faster writes

## Partitioning

- For very large tables (>100M rows) where queries filter on partition key
- **RANGE**: time-series (`PARTITION BY RANGE (created_at)`)
- **LIST**: discrete values (`PARTITION BY LIST (region)`)
- **HASH**: even distribution (`PARTITION BY HASH (user_id)`)
- Prefer declarative partitioning. Do NOT use table inheritance.

## Constraints

- **PK**: implicit UNIQUE + NOT NULL; creates B-tree index
- **FK**: specify `ON DELETE/UPDATE`; add explicit index on referencing column
- **UNIQUE**: allows multiple NULLs unless `NULLS NOT DISTINCT` (PG15+)
- **CHECK**: row-local; NULL passes (three-valued logic) — combine with `NOT NULL`
- **EXCLUDE**: prevents overlapping values (double-booking prevention)

## Migration Example

```sql
-- Safe ALTER TABLE pattern
BEGIN;
ALTER TABLE orders ADD COLUMN discount NUMERIC(5,2) CHECK (discount >= 0 AND discount <= 100);
ALTER TABLE orders ALTER COLUMN discount SET DEFAULT 0;
UPDATE orders SET discount = 0 WHERE discount IS NULL;
ALTER TABLE orders ALTER COLUMN discount SET NOT NULL;
COMMIT;
```

## PostgreSQL Gotchas

- Unquoted identifiers → lowercased. Use `snake_case`.
- FK columns are **not** auto-indexed — add them.
- Sequences/identity have gaps (normal — don't "fix").
- Heap storage: no clustered PK by default.
- MVCC: updates/deletes leave dead tuples — vacuum handles them.

## Extensions (Common)

- `pgcrypto` — `gen_random_uuid()`, cryptographic functions
- `uuid-ossp` — UUID generation (legacy; prefer pgcrypto)
- `pg_stat_statements` — query performance monitoring

## Exit Criteria

- [ ] Schema normalized to 3NF (or documented denormalization)
- [ ] All FK columns indexed
- [ ] Banned data types avoided
- [ ] Constraints enforce data integrity
- [ ] Index strategy documented for query patterns
