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

Services own domain rules, validation, authorization, and orchestration. Repositories perform persistence and report database outcomes; they do not decide whether a caller is authorized. Use atomic SQL operations with returned outcomes for writes that may race or depend on uniqueness.

## Error organization

- Put domain-specific errors in `src/schedule_manager/<domain>/errors.py`.
- Put only cross-domain errors in `src/schedule_manager/core/errors.py`.
- Derive domain errors from corresponding core errors when they represent shared conditions.

## Database sessions and tests

- Use one `AsyncSession` per request or task. Do not share a session between concurrently running asyncio tasks.
- Database tests must use `POSTGRES_TEST_DB` and the shared `test_session` fixture from `tests/conftest.py`.
- Put shared fixtures in `tests/conftest.py`.
- Organize behavior tests in `tests/business/` and authorization/capability tests in `tests/capabilities/`.
- Concurrency tests must use independent sessions/connections.

## Dependencies and validation

- Use `uv` for Python dependency management. Run `uv sync` to synchronize dependencies.
- Update dependency declarations and `uv.lock` through `uv`; do not hand-edit the lockfile.
- Docker and CI install locked dependencies with `uv sync --frozen`.
- Run the smallest relevant test selection while iterating. Before finishing, run relevant tests, Ruff, and Pyright when practical.

## Sensitive configuration and changes

- Never print, expose, copy, or commit credential values from `.env`. Use `.env.example` for variable names and configuration shape.
- Preserve unrelated work already present in the worktree. Stage and commit only files relevant to the requested change.
- Surface failures explicitly; do not silently swallow exceptions or return success-shaped fallbacks.
