# How to Create Tests

## What to Test

Create a test only when it explicitly verifies at least one of:

- A system invariant that must always hold.
- A meaningful system property or behavior.
- An integration between components.
- An end-to-end user or API workflow.

Do not add tests for behavior that is obvious from straightforward implementation and whose failure would be easy to discover and harmless in production. Avoid tests that merely restate implementation details or verify framework behavior.

## Test Granularity

- Each test should verify one independent invariant, property, or behavior.
- Split independent outcomes into separate tests so each failure identifies the behavior that regressed.
- Keep tests for distinct layers or concerns in separate files, following the source domain and subdomain layout under `tests/`.
- Use `conftest.py` for shared setup, not to combine unrelated test scenarios.

## Test Types

- Unit tests verify focused domain behavior or invariants without exercising unrelated layers.
- Integration tests verify meaningful interactions between components, including database behavior when relevant.
- End-to-end tests exercise a complete user or API workflow across its relevant layers.
- Concurrency tests must use independent database sessions/connections and verify the resulting invariant, not merely that concurrent calls completed.
