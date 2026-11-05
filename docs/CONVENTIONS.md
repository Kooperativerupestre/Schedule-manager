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

Services own domain rules, validation, authorization, and orchestration, including eligibility checks. Authorization decisions must never be implemented in repositories: a repository must not allow or deny an operation based on who is requesting it or on domain roles and memberships. Repositories may return persisted facts for a service to evaluate, and may use database constraints or row locks to preserve data integrity and concurrency guarantees. Repositories otherwise perform persistence responsibilities and report outcomes; they do not combine separate domain operations. Services compose repository operations when a workflow needs multiple writes, within the request/task transaction. Use atomic SQL operations with returned outcomes for writes that may race or depend on uniqueness.

### Authentication responsibility

Authentication is exclusively a service responsibility. Authentication repositories only persist and retrieve authentication records; they must never verify credentials, decide whether a user is authenticated, or hash passwords. The service hashes a password before passing its hash to the repository and verifies credentials after retrieving the record.

### Subdomains

Give a subdomain its own package and the layers it needs instead of placing its behavior in a neighboring domain's service or repository. Concepts with separate lifecycle or rules should remain separate subdomains.

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

## Units and memberships

A unit is a child of a business and stores its own identity and business association. Unit membership and unit ownership are distinct associations with their own persistence and rules; do not fold either into the unit's identity or treat membership as ownership.

Business owners manage unit creation and deletion and are the only users who can grant or revoke unit ownership. A user must already be a unit member to become a unit owner. The creator becomes a unit member, but is not made a unit owner automatically.

Unit owners manage unit memberships but cannot grant or revoke ownership. Members can read unit and membership details; only unit owners can add or remove members. A member who is still a unit owner cannot have their membership removed until a business owner revokes that ownership. Deleting a unit also removes its memberships and ownership records.

## Workstations and workers

- Every workstation belongs to exactly one unit. A unit owner may create, rename, and delete workstations belonging to that unit; other users may not manage them.
- Only a unit owner may hire workers for a workstation in that owner's unit. Hiring a user does not require that user to be a member of the unit.
- An owner may hire themselves and work at a workstation they own. Ownership does not prevent someone from also being a worker.
- A user may work at multiple workstations, and a workstation may have multiple workers. The same user may have at most one worker relationship with a given workstation.
- A worker may end only their own work relationship. Ending it removes that relationship without deleting the user or affecting their work relationships with other workstations. Another person, including a unit owner, cannot dismiss the worker.
- Any member of a workstation's unit may read its worker relationships. Reading a relationship does not require the reader to be an owner or worker.
- Deleting a user or workstation removes the worker relationships attached to it. Deleting a unit also removes its workstations and, consequently, their worker relationships.

## Dependencies and validation

- Use `uv` for Python dependency management. Run `uv sync` to synchronize dependencies.
- Update dependency declarations and `uv.lock` through `uv`; do not hand-edit the lockfile.
- Docker and CI install locked dependencies with `uv sync --frozen`.
- Run the smallest relevant test selection while iterating. Before finishing, run relevant tests, Ruff, and Pyright when practical.

## Sensitive configuration and changes

- Never print, expose, copy, or commit credential values from `.env`. Use `.env.example` for variable names and configuration shape.
- Preserve unrelated work already present in the worktree. Stage and commit only files relevant to the requested change.
- Surface failures explicitly; do not silently swallow exceptions or return success-shaped fallbacks.
