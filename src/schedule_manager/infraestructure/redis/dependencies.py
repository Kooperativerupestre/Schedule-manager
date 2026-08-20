import inspect
import string
from uuid import UUID
from fastapi import Depends, HTTPException, Request
from schedule_manager.auth.dependencies import get_current_person_id
from schedule_manager.infraestructure.redis.redis import (
    RateLimitScope,
    RateLimitRequest,
    execute_redis_script,
)

FIELD_TYPES: dict[str, type] = {
    "business_id": UUID,
    "target_person_id": UUID,
    "unit_id": UUID,
    "workstation_id": UUID,
    "holiday_id": UUID,
    "invite_id": UUID,
    "schedule_id": UUID,
}


def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def rate_limit(scope_templates: list[RateLimitScope]):
    field_names: set[str] = set()
    for template in scope_templates:
        field_names.update(
            name
            for _, name, _, _ in string.Formatter().parse(template.bucket_key)
            if name
        )

    needs_person_id = "person_id" in field_names
    needs_ip = "ip" in field_names

    field_names.discard("person_id")
    field_names.discard("ip")

    params = [
        inspect.Parameter(
            "request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request
        ),
    ]

    if needs_person_id:
        params.append(
            inspect.Parameter(
                "person_id",
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(get_current_person_id),
                annotation=UUID,
            )
        )

    for name in sorted(field_names):
        params.append(
            inspect.Parameter(
                name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=FIELD_TYPES.get(name, UUID),
            )
        )

    async def dependency(**kwargs):
        request: Request = kwargs["request"]
        script = getattr(request.app.state, "rate_limit_script", None)
        if script is None:
            return

        context = {name: kwargs[name] for name in field_names}
        if needs_person_id:
            context["person_id"] = kwargs["person_id"]
        if needs_ip:
            context["ip"] = get_client_ip(request)

        scopes = [
            RateLimitScope(
                bucket_key=t.bucket_key.format(**context),
                capacity=t.capacity,
                refill_rate=t.refill_rate,
                ttl=t.ttl,
            )
            for t in scope_templates
        ]

        allowed = await execute_redis_script(script, RateLimitRequest(scopes=scopes))
        if not allowed:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    dependency.__signature__ = inspect.Signature(params)  # type: ignore
    return dependency
