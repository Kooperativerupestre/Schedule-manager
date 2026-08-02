# Architecture 1.0

This document tracks architectural decisions for Schedule Manager as a chronological
list of milestones — not a static description of the final system, but a record of
how and why the system got the shape it has, including open questions that haven't
been resolved yet.

---

## Milestone: Capability-based permission model

### Context

An earlier design used a traditional RBAC (Role-Based Access Control) model, where
each person is assigned a fixed role (e.g. "boss", "manager") and that role carries
an implicit, global set of permissions.

This broke down in a multi-tenant setting on edge cases like: *can a boss manage a
unit?* The honest answer is "it depends on which unit, and sometimes on when" — and
RBAC has no vocabulary for "depends on which instance." Avoiding this meant either
creating one role per resource instance (role explosion) or pushing the exception
logic into application code as special-case `if` statements. Both are unmaintainable
in a multi-tenant application long-term.

### Alternatives considered

No alternatives were deeply evaluated beyond RBAC — this decision was made without
extensive prior experience comparing permission models. The chosen approach sits
closer to ABAC (Attribute-Based Access Control) than to RBAC, though it wasn't
explicitly designed against ABAC as a reference point.

### Decision

A capability-based permission model was chosen instead:

- No capability implies any other — capabilities are independent of one another.
- Every capability has a **target**: exactly one of `business_id`, `unit_id`, or
  `workstation_id` is non-null per capability row (enforced by the
  `check_single_target` DB constraint).
- Capabilities carry **temporal validity** — they can expire or be ended
  (`TSTZRANGE`, exclusion constraints for non-overlapping intervals).

### Consequences

- Insertion is more complex than a simple role assignment, since only one of the
  three target columns may be populated at a time.
- Any query needs to determine which target id is non-null before it can use the
  capability — the schema doesn't say "the target," it says "one of these three,
  find out which."
- This complexity is **concentrated in the capabilities repository**, specifically
  in the translation from `CapabilityRow` to `CapabilityAssignment`. The service
  layer and everything above it work only with `CapabilityAssignment` and have no
  knowledge of the underlying nullable-column schema. This is a deliberate
  separation of concerns: the repository absorbs the schema's awkwardness so it
  doesn't leak upward.

---

## Milestone: Multi-tenancy

### Resolution: capability validation does not check business

After working through this, the decision is: **capability validation is scoped to
the resource (unit/workstation/business) it targets, not to the business context
it was granted under.** If a unit changes ownership to a different business, any
existing capability on that unit remains valid — nothing re-checks the unit's
`business_id` at use-time.

This means `business_memberships` and capability validation are **independent
checks that don't cross-reference each other** at use-time.

### Membership is checked only at grant-time

A capability can only be **created** for a person who is currently a member of the
business (via `business_memberships`). This is a grant-time check, not a
continuously enforced invariant — once the capability exists, nothing re-verifies
that the membership still holds.

### Planned: cascading revocation on membership removal

If a person's `business_memberships` row is removed, their capabilities under that
business should be `end()`-ed as a reaction to that removal (not left to go stale).
This is planned but not yet implemented, and the mechanism is undecided:

- **Service-layer rule** — the code path that removes a membership also explicitly
  calls `end()` on the person's capabilities for that business. Simpler, but only
  as reliable as every removal path remembering to do it.
- **Database trigger** — removing a membership automatically ends the related
  capabilities at the DB level. Stronger guarantee, consistent with how
  `check_single_target` and the `TSTZRANGE` exclusion constraints already let the
  database enforce invariants — but moves business logic out of Python.
