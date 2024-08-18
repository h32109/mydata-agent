import asyncio
import time
from typing import Callable

import psutil
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class CPULoadControlMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, high_cpu_threshold: float):
        super().__init__(app)
        self.high_cpu_threshold = high_cpu_threshold * 100  # Convert to percentage

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        if cpu_usage > self.high_cpu_threshold:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"message": "CPU 사용량이 너무 높습니다. 잠시 후 다시 시도해주세요."}
            )
        return await call_next(request)


class CPUMonitorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, duration: int, interval: float):
        super().__init__(app)
        self.duration = duration
        self.interval = interval

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        usage_before = psutil.cpu_percent(interval=None)

        response = await call_next(request)

        usage_after = psutil.cpu_percent(interval=None)
        end_time = time.perf_counter()
        processing_time = end_time - start_time

        # Log CPU usage and processing time
        print(f"CPU Usage: Before {usage_before}%, After {usage_after}%")
        print(f"Request processing time: {processing_time:.4f} seconds")

        return response


async def monitor_cpu_usage(duration: float, interval: float) -> None:
    end_time = time.perf_counter() + duration
    while time.perf_counter() < end_time:
        cpu_usage = psutil.cpu_percent(interval=None)
        print(f"Current CPU Usage: {cpu_usage}%")
        await asyncio.sleep(interval)
