---
name: error-handling-patterns
description: Master error handling patterns across languages including exceptions, Result types, error propagation, and graceful degradation to build resilient applications. Use when implementing error handling, designing APIs, or improving application reliability.
version: "1.1.0"
license: MIT
metadata:
  author: juancito8812
  languages: python, typescript, rust
---

# Error Handling Patterns

## Checklist

- [ ] No empty catch blocks — every catch logs or handles
- [ ] Error messages are user-friendly (no raw stack traces to users)
- [ ] Async errors handled (unhandled promise rejections, uncaught exceptions)
- [ ] Retry logic for transient failures (network, rate limits)
- [ ] Error context preserved (correlation IDs, timestamps)
- [ ] Recovery vs non-recovery distinction made

## When to Use

- Implementing error handling in new features
- Designing error-resilient APIs
- Debugging production issues
- Improving application reliability
- Implementing retry and circuit breaker patterns
- Handling async/concurrent errors
- Building fault-tolerant distributed systems

## Core Concepts

### Error Handling Philosophies

- **Exceptions**: Traditional try-catch, disrupts control flow (Python, Java, C#)
- **Result Types**: Explicit success/failure, functional approach (Rust, TypeScript with discriminated unions)
- **Error Codes**: C-style, requires discipline
- **Option/Maybe Types**: For nullable values

### Error Categories

**Recoverable:** Network timeouts, missing files, invalid input, API rate limits
**Unrecoverable:** Out of memory, stack overflow, programming bugs

## Best Practices

1. **Fail Fast**: Validate input early, fail quickly
2. **Preserve Context**: Include stack traces, metadata, timestamps
3. **Meaningful Messages**: Explain what happened and how to fix it
4. **Log Appropriately**: Error = log, expected failure = don't spam logs
5. **Handle at Right Level**: Catch where you can meaningfully handle
6. **Don't Swallow Errors**: Log or re-throw, don't silently ignore
7. **Type-Safe Errors**: Use typed errors when possible

### Python

```python
def process_order(order_id: str) -> Order:
    try:
        if not order_id:
            raise ValidationError("Order ID is required")
        order = db.get_order(order_id)
        if not order:
            raise NotFoundError("Order", order_id)
        try:
            payment_result = payment_service.charge(order.total)
        except PaymentServiceError as e:
            logger.error(f"Payment failed for order {order_id}: {e}")
            raise ExternalServiceError(
                "Payment processing failed",
                service="payment_service",
                details={"order_id": order_id, "amount": order.total}
            ) from e
        order.status = "completed"
        order.payment_id = payment_result.id
        db.save(order)
        return order
    except ApplicationError:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing order {order_id}")
        raise ApplicationError("Order processing failed", code="INTERNAL_ERROR") from e
```

### TypeScript

```typescript
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

async function processOrder(orderId: string): Promise<Result<Order, AppError>> {
  try {
    if (!orderId) return { ok: false, error: { code: 'VALIDATION', message: 'Order ID required' } };
    const order = await db.getOrder(orderId);
    if (!order) return { ok: false, error: { code: 'NOT_FOUND', message: `Order ${orderId} not found` } };
    const payment = await paymentService.charge(order.total);
    order.status = 'completed';
    order.paymentId = payment.id;
    await db.save(order);
    return { ok: true, value: order };
  } catch (err) {
    logger.error({ orderId, err }, 'Order processing failed');
    return { ok: false, error: { code: 'INTERNAL', message: 'Order processing failed' } };
  }
}
```

### Rust

```rust
#[derive(Debug, thiserror::Error)]
pub enum OrderError {
    #[error("validation error: {0}")]
    Validation(String),
    #[error("order {0} not found")]
    NotFound(String),
    #[error("payment failed: {0}")]
    Payment(String),
    #[error("internal error")]
    Internal(#[from] anyhow::Error),
}

async fn process_order(order_id: &str) -> Result<Order, OrderError> {
    if order_id.is_empty() {
        return Err(OrderError::Validation("order ID required".into()));
    }
    let order = db::get_order(order_id)
        .await
        .ok_or_else(|| OrderError::NotFound(order_id.into()))?;
    let payment = payment_service::charge(order.total)
        .await
        .map_err(|e| OrderError::Payment(e.to_string()))?;
    order.status = "completed";
    order.payment_id = payment.id;
    db::save(&order).await?;
    Ok(order)
}
```

## Retry Pattern

```python
import asyncio
from functools import wraps

def retry(max_attempts=3, base_delay=1.0, backoff=2.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (TimeoutError, ConnectionError) as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        delay = base_delay * (backoff ** attempt)
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator
```

## Common Pitfalls

- **Catching Too Broadly**: `except Exception` hides bugs
- **Empty Catch Blocks**: Silently swallowing errors
- **Logging and Re-throwing**: Creates duplicate log entries
- **Poor Error Messages**: "Error occurred" is not helpful
- **Ignoring Async Errors**: Unhandled promise rejections

## Exit Criteria

- [ ] No empty catch blocks in codebase
- [ ] All API errors sanitized before reaching user
- [ ] Retry with backoff implemented for transient failures
- [ ] Async error handlers registered (unhandledrejection, etc.)
