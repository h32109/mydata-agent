import asyncio
import time
import psutil

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class CPULoadControlMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, high_cpu_threshold: float):
        super().__init__(app)
        self.high_cpu_threshold = high_cpu_threshold

    async def dispatch(self, request: Request, call_next):
        cpu_usage = psutil.cpu_percent(interval=0.1)
        if cpu_usage > self.high_cpu_threshold * 100:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"message": "CPU 사용량이 너무 높습니다. 잠시 후 다시 시도해주세요."}
            )

        response = await call_next(request)

        return response


async def monitor_cpu_usage(duration, interval):
    start_time = time.time()
    while time.time() - start_time < duration:
        cpu_usage = psutil.cpu_percent(interval=None)
        print(f"Current CPU Usage: {cpu_usage}%")
        await asyncio.sleep(interval)


class CPUMonitorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, duration: int, interval: float):
        super().__init__(app)
        self.duration = duration
        self.interval = interval

    async def dispatch(self, request: Request, call_next):
        usage_before = psutil.cpu_percent(interval=None)
        print(f"CPU Usage Before: {usage_before}%")
        start_time = time.time()
        monitor_task = asyncio.create_task(monitor_cpu_usage(self.duration, self.interval))
        response = await call_next(request)
        await monitor_task
        usage_after = psutil.cpu_percent(interval=None)
        print(f"CPU Usage After: {usage_after}%")
        end_time = time.time()
        print(f"Request processing time: {end_time - start_time} seconds")
        return response
