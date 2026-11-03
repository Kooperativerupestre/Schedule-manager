# How to documentate

- Keep project documentation under `docs/`; keep only concise agent entry-point instructions in the repository-root `AGENTS.yml`.
- Document durable project-wide policies separately from domain-specific conventions when both need their own reference.
- Avoid duplicating the same rule across documents. Link to the authoritative document instead.
- Create separate documents only for distinct topics that benefit from independent use; otherwise consolidate related guidance.
- Keep documentation concise, actionable, and consistent with the code. Update it when the documented behavior or convention changes.
- Record durable decisions and lessons in the appropriate project documentation; do not rely on conversation history to preserve them. This includes architectural boundaries, API/domain contracts, migration policy, testing structure, and other choices likely to guide future work.
- When making a long-term decision, document its rule and relevant rationale where future contributors will look for it, and update that documentation if the decision or implementation changes.
