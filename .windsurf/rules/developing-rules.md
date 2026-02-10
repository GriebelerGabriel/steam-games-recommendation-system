---
trigger: model_decision
---

# Software Quality Rules (Windsurf Paste)

## Core Principles
- **Clarity over cleverness**: optimize for readability and maintainability.
- **Small, focused changes**: keep PRs minimal, reversible, and reviewable.
- **Single source of truth**: avoid duplicated logic; centralize business rules.
- **Fail fast, fail safe**: validate inputs early; handle errors explicitly.

## Architecture & Design
- **Separation of concerns**: keep API/controllers, services/use-cases, domain, and persistence isolated.
- **Dependency direction**: domain/use-cases must not depend on frameworks or I/O; adapt with interfaces.
- **High cohesion, low coupling**: prefer composition over inheritance.
- **Explicit boundaries**: define modules/packages by business capability, not by technical layer only.
- **Data contracts**: define DTOs/schemas; do not leak persistence models outside repositories.

## Coding Standards
- **Naming**: use precise names; avoid abbreviations unless widely understood, but also don't gave too long names.
- **Functions**: small, single-purpose; avoid deep nesting; early returns when appropriate.
- **Immutability by default**: avoid shared mutable state; minimize side effects.
- **No magic values**: use constants/enums/configuration.
- **No dead code**: remove unused code/flags; do not leave commented-out blocks.
- **No hidden behavior**: avoid implicit global state, reflection tricks, or action-at-a-distance.

## Error Handling & Observability
- **Typed/structured errors**: wrap with context; never swallow exceptions silently.
- **Actionable messages**: include what failed, why, and next steps.
- **Logging**:
  - **Structured logs** (key/value), no log spam.
  - **Do not log secrets** (tokens, passwords, PII).
  - **Include correlation/request IDs** where available.
- **Metrics**: track latency, error rate, throughput for critical paths.

## Testing (Definition of Done)
- **Coverage where it matters**: focus on business rules and critical flows, not trivial getters.
- **Test pyramid**:
  - **Unit tests** for pure logic.
  - **Integration tests** for DB/queues/HTTP boundaries.
  - **E2E tests** for the most important user journeys.
- **Deterministic tests**: avoid time/network randomness; use fakes/mocks; freeze time.
- **Arrange-Act-Assert**: clear structure; one behavior per test.
- **Assertions**: verify outcomes and side effects; avoid overly broad snapshot tests.

## Security
- **Input validation**: validate and sanitize all external inputs.
- **AuthZ before data**: enforce authorization checks prior to accessing sensitive resources.
- **Least privilege**: minimal permissions for services, DB users, and tokens.
- **Secret management**: no secrets in code, logs, or commits; use env/secret stores.
- **Dependencies**: keep libraries up to date; address known CVEs.

## Performance & Reliability
- **Complexity awareness**: avoid unnecessary N+1 calls; prefer batching.
- **Resource limits**: timeouts, retries with backoff, circuit breakers for unstable dependencies.
- **Idempotency**: make handlers safe for retries; use idempotency keys when relevant.
- **Concurrency safety**: avoid races; use proper locking/transactions.
- **Pagination**: required for list endpoints; avoid unbounded queries.

## Data Quality
- **Schema migrations**: backward compatible when possible; include rollback strategy.
- **Constraints**: enforce invariants in DB (FKs, uniques) in addition to app-level checks.
- **Time handling**: store timestamps in UTC; convert at the edges.

## API & Compatibility
- **Explicit contracts**: version APIs or maintain backward compatibility.
- **Consistent errors**: standard error envelope with code/message/details.
- **HTTP semantics**: correct status codes; GET is side-effect free.

## Code Review Checklist (Quick)
- **Correctness**: handles edge cases; no hidden behavior.
- **Security**: no secrets/PII leaks; auth/authz enforced.
- **Tests**: meaningful and stable; covers critical paths.
- **Maintainability**: readable, documented by code (not comments), minimal duplication.
- **Operational readiness**: logs/metrics, timeouts, retries, failure modes considered.

## CI/CD & Delivery
- **Automate quality gates**: formatting, lint, tests, type checks, security scanning.
- **PR hygiene**: clear description, scope, and risk; include screenshots/logs when relevant.
- **Feature flags**: use for risky changes; ensure safe defaults.
- **Rollback plan**: every deploy must be reversible.

## Non-Negotiables
- **No breaking changes without coordination**.
- **No merge with failing tests/linters**.
- **No plaintext secrets**.
- **No silent failures**.