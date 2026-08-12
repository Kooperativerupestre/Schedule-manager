# Schedule Manager

A multi-tenant application for schedule management.

## Problems It Solves

### Schedule Overlaps

The project uses PostgreSQL range types with GiST-backed exclusion constraints to guarantee at the database level that time intervals do not overlap.

This avoids the common "check, then insert" approach, which can introduce race conditions under concurrent requests.

### Rigid Roles

The project does not rely on a role-based capability model where every capability must belong to a predefined role.

Capabilities are handled independently, allowing permissions to be composed more flexibly according to the application's needs.

### Exceptions and Holidays

The application supports exceptions with active/inactive status and holidays at the Business, Unit, and Workstation levels.

This allows schedules to accommodate ordinary exceptions and unexpected changes without modifying the underlying schedule structure.

## Architecture

The application is based on the following hierarchy:

```text
Business
    └── Unit
        └── Workstation
```
It also includes relationships such as Business Memberships, which influence how capabilities are assigned and evaluated.

For more information, see [architecture](docs/architecture.md)

# Running

Clone the repository:

git clone <repository>
cd schedule-manager

Start the application with Docker Compose:

docker compose up --build

The API will be started together with its required services.

# Tech Stack
- Python 3.14
- uv
- pytest
- GitHub Actions
- PostgreSQL
- FastAPI
- Docker

# License

Apache 2.0

See [LICENSE](LICENSE).