# Workstation appointments

Appointments are a workstation subdomain, persisted in the existing `appointments` table. An appointment has a maker, assigned worker, workstation, half-open time period (`[begin, end)`), and one of `pending`, `cancelled`, or `successful`.

## Timezone and ranges

All application datetimes must be timezone-aware and UTC. Naive values are invalid; values with another explicit offset are normalized to UTC. PostgreSQL stores appointment periods as `TSTZRANGE`. Periods must be non-empty, finite, lower-inclusive, and upper-exclusive. Adjacent appointments (one ending when another begins) do not overlap.

`AppointmentService.get_in_range` returns appointments whose periods overlap the requested range, including appointments that begin before the range but extend into it. Canceled appointments remain retrievable, but do not prevent scheduling.

## Scheduling and concurrency

`WorkstationService.can_schedule` (implemented by the appointments subdomain) is an advisory read that returns whether an active appointment currently overlaps the requested period. It is not a reservation and its result can become stale immediately.

`AppointmentService.create` does not perform a pre-insert overlap query. PostgreSQL's `no_overlapping_appointments` exclusion constraint is authoritative and protects concurrent requests. It returns `True` on insertion and `False` only when that constraint rejects an overlapping active appointment; other database errors are raised. The database operation is isolated in a savepoint so a rejected appointment does not invalidate the caller's transaction.

The exclusion constraint is scoped to one workstation and excludes canceled appointments. Concurrency tests must use independent sessions/connections and verify that simultaneous overlapping requests cannot create more than one active appointment.

## Cancellation and completion

Only the appointment maker, its assigned worker, or a unit owner can cancel it. Only its assigned worker can mark it successful. These transitions apply only while the appointment is pending and use an atomic conditional update. The service returns a result enum that distinguishes success, missing appointments, unauthorized requests, and appointments already canceled or completed. Deleting a worker keeps appointment history and clears the worker assignment; that detached appointment can still be canceled by its maker or a unit owner but cannot be completed by a worker.

Migration `0000006` adds worker assignment to the existing appointments table and requires the table to be empty when applied because existing appointments cannot be safely assigned to workers automatically.

## HTTP API

The authenticated endpoints are nested under `/workstations/{workstation_id}/appointments`. Users must be unit members to list, create, inspect, or delete appointments at a workstation. New appointments use the authenticated user as their maker; the maker ID is not accepted from the request body.

- `POST /workstations/{workstation_id}/appointments` accepts `worker_id`, `begin_at`, and `end_at`, then creates an appointment using the authenticated user as maker. It returns `{"created": true}` (201) or `{"created": false}` on overlap (200).
- `GET /workstations/{workstation_id}/appointments?begin_at=...&end_at=...` lists overlapping appointments.
- `GET /workstations/{workstation_id}/appointments/availability?begin_at=...&end_at=...` returns the advisory `can_schedule` result.
- `GET` and `DELETE /workstations/{workstation_id}/appointments/{appointment_id}` inspect or remove one appointment.
- `POST /workstations/{workstation_id}/appointments/{appointment_id}/cancel` and `/complete` return the service action result enum. Cancellation/completion authorization is based on the appointment maker, assigned worker, or unit owner as described above, not on general unit membership.
