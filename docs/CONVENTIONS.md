# Project conventions

## Domain structure

Keep domain behavior in `src/schedule_manager/<domain>/`. Follow the existing domain patterns and add only the layers the domain needs:

- `model.py`: SQLAlchemy persistence models.
- `repository.py`: database reads and writes.
- `service.py`: domain behavior and orchestration.
- `schemas.py`: request and response data models.
- `schema_translator.py`: conversion between schemas and persistence models.
- `router.py`: HTTP endpoints and transport-level error mapping.
- `errors.py`: errors specific to the domain.

Services own domain rules, validation, authorization, and orchestration. Repositories perform a single persistence responsibility where practical and report database outcomes; they do not combine separate domain operations or decide whether a caller is authorized. Services compose repository operations when a workflow needs multiple writes, within the request/task transaction. Use atomic SQL operations with returned outcomes for writes that may race or depend on uniqueness.

### Authentication responsibility

Authentication is exclusively a service responsibility. Authentication repositories only persist and retrieve authentication records; they must never verify credentials, decide whether a user is authenticated, or hash passwords. The service hashes a password before passing its hash to the repository and verifies credentials after retrieving the record.

### Subdomains

Give a subdomain its own package and the layers it needs instead of adding its behavior to a neighboring domain's service or repository. For example, business membership code belongs in `business/memberships/`, with its own model, repository, service, schemas, and router as needed.

## Error organization

- Put domain-specific errors in `src/schedule_manager/<domain>/errors.py`.
- Put only cross-domain errors in `src/schedule_manager/core/errors.py`.
- Derive domain errors from corresponding core errors when they represent shared conditions.
- Keep HTTP error translation in `src/schedule_manager/core/exception_handlers.py`, not in routers. Domain errors returned through the API must inherit a core error type with a registered handler. When adding a new core error category, register its HTTP handler and add a test for its response.

## Database sessions and tests

- Use one `AsyncSession` per request or task. Do not share a session between concurrently running asyncio tasks.
- Database tests must use `POSTGRES_TEST_DB` and the shared `test_session` fixture from `tests/conftest.py`.
- Put broadly shared fixtures in `tests/conftest.py` and domain/subdomain fixtures in the corresponding test package's `conftest.py`.
- Mirror the source domain and subdomain layout under `tests/`, such as `tests/business/memberships/`, and separate tests by layer or concern. See [HOW_TO_CREATE_TESTS](../tests/HOW_TO_CREATE_TESTS.md) for test selection and granularity.
- Keep authorization tests with their domain/subdomain behavior tests; use `tests/capabilities/` for cross-domain capability behavior.
- Concurrency tests must use independent sessions/connections.

## Migrations

- Treat an applied migration as immutable. Add a new incremental migration for schema changes that must reach databases where earlier revisions are already recorded.
- Editing an old migration is appropriate only when it has not been applied in any environment that must be supported. When a schema change needs both a fresh-install definition and an upgrade path, keep the initial schema accurate and make the later migration safe for already-migrated databases.

## Dependencies and validation

- Use `uv` for Python dependency management. Run `uv sync` to synchronize dependencies.
- Update dependency declarations and `uv.lock` through `uv`; do not hand-edit the lockfile.
- Docker and CI install locked dependencies with `uv sync --frozen`.
- Run the smallest relevant test selection while iterating. Before finishing, run relevant tests, Ruff, and Pyright when practical.

## Sensitive configuration and changes

- Never print, expose, copy, or commit credential values from `.env`. Use `.env.example` for variable names and configuration shape.
- Preserve unrelated work already present in the worktree. Stage and commit only files relevant to the requested change.
- Surface failures explicitly; do not silently swallow exceptions or return success-shaped fallbacks.
