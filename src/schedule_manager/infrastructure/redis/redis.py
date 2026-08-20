from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis
from redis.commands.core import Script

from schedule_manager.config import settings

from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass(frozen=True)
class RateLimitScope:
    bucket_key: str
    capacity: int
    refill_rate: int
    ttl: int


@dataclass(frozen=True)
class RateLimitRequest:
    scopes: list[RateLimitScope]
    now: datetime = field(default_factory=lambda: datetime.now(UTC))


async def execute_redis_script(script: Script, data: RateLimitRequest) -> bool:
    keys = [scope.bucket_key for scope in data.scopes]
    now = data.now.timestamp()

    argv = [now]
    for scope in data.scopes:
        argv.extend([scope.capacity, scope.refill_rate, scope.ttl])

    result = await script(keys=keys, args=argv)
    return bool(result)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    script = redis.register_script("lua_script")
    app.state.redis = redis

    yield

    await redis.aclose()


app = FastAPI(lifespan=lifespan)
