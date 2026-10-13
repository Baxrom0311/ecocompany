"""Run ASGI lifespan on the same loop as Passenger's HTTP requests."""
import asyncio
import threading

from a2wsgi import ASGIMiddleware


class LifespanWSGI:
    def __init__(self, app):
        self.app = app
        self.adapter = ASGIMiddleware(app, wait_time=120)
        self._lock = threading.Lock()
        self._ready = threading.Event()
        self._future = None
        self._stop = None
        self._error = None

    async def _serve_lifespan(self):
        try:
            self._stop = asyncio.Event()
            async with self.app.router.lifespan_context(self.app):
                self._ready.set()
                await self._stop.wait()
        except BaseException as exc:
            self._error = exc
            self._ready.set()
            raise

    def __call__(self, environ, start_response):
        with self._lock:
            if self._future is None:
                self._future = asyncio.run_coroutine_threadsafe(self._serve_lifespan(), self.adapter.loop)
        if not self._ready.wait(timeout=60):
            raise RuntimeError("Application startup timed out")
        if self._error is not None:
            raise RuntimeError("Application startup failed") from self._error
        return self.adapter(environ, start_response)

    def close(self):
        if self._future is not None and self._stop is not None:
            self.adapter.loop.call_soon_threadsafe(self._stop.set)
            self._future.result(timeout=15)
        self.adapter.loop.call_soon_threadsafe(self.adapter.loop.stop)
