"""Limiter cliks implementation."""

from math import ceil
from typing import Callable
from typing import Optional

import aioredis
from fastapi import HTTPException
from pydantic import conint
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


class MyException(Exception):
    """Exception implementation."""

    pass


async def default_identifier(request: Request):
    """."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0]
    else:
        ip = request.client.host
    return ip + ":" + request.scope["path"]


async def default_callback(request: Request, response: Response, param_expire: int):
    """
    default callback when too many requests
    :param request:
    :param param_expire: The remaining milliseconds
    :param response:
    :return:
    """
    expire = ceil(param_expire / 1000)
    raise HTTPException(
        HTTP_429_TOO_MANY_REQUESTS, "api121",
        headers={"Retry-After": str(expire)}
    )


class FastAPILimiter:
    """."""

    redis: aioredis.Redis = None
    prefix: str
    lua_sha: str
    identifier: Callable = None
    callback: Callable = None
    lua_script = """ local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local expire_time = ARGV[2]
        local current = tonumber(redis.call('get', key) or "0")
        if current > 0 then
         if current + 1 > limit then
         return redis.call("PTTL",key)
         else
                redis.call("INCR", key)
         return 0
         end
        else
            redis.call("SET", key, 1,"px",expire_time)
         return 0
        end
    """

    @classmethod
    async def init(
        cls,
        redis: aioredis.Redis,
        prefix: str = "fastapi-limiter",
        identifier: Callable = default_identifier,
        callback: Callable = default_callback,
    ):
        """."""
        cls.redis = redis
        cls.prefix = prefix
        cls.identifier = identifier
        cls.callback = callback
        cls.lua_sha = await redis.script_load(cls.lua_script)

    @classmethod
    async def close(cls):
        """."""
        await cls.redis.close()


class RateLimiter:
    """Rate Limit implementation."""

    def __init__(
            self,
            times: conint(ge=0) = 1,
            milliseconds: conint(ge=-1) = 0,
            seconds: conint(ge=-1) = 0,
            minutes: conint(ge=-1) = 0,
            hours: conint(ge=-1) = 0,
            identifier: Optional[Callable] = None,
            callback: Optional[Callable] = None,
    ):
        """Initialize method."""
        self.times = times
        self.milliseconds = \
            milliseconds + 1000 * seconds + 60000 * minutes + 3600000 * hours
        self.time_to_block = 2 * 60000
        self.identifier = identifier
        self.callback = callback

    async def __call__(self, request: Request, response: Response):
        """Call implementation."""
        if not FastAPILimiter.redis:
            raise MyException("You must call FastAPILimiter.init "
                              "in startup event of fastapi")
        index = 0
        for route in request.app.router.routes:
            if route.path == request.scope["path"]:
                for idx, dependency in enumerate(route.dependencies):
                    if self is dependency.dependency:
                        index = idx
                        break
        # moved here because constructor run before app startup
        identifier = self.identifier or FastAPILimiter.identifier
        callback = self.callback or FastAPILimiter.callback
        redis = FastAPILimiter.redis
        rate_key = await identifier(request)
        key = f"{FastAPILimiter.prefix}:{rate_key}:{index}"
        param_expire = await redis.evalsha(
            FastAPILimiter.lua_sha, 1, key, str(self.times),
            str(self.time_to_block)
        )
        if param_expire != 0:
            return await callback(request, response, param_expire)
