"""
Health diagnostics — Verifica estado de cada componente del bridge.
"""

import sys
import time
from typing import Optional

from models import ComponentStatus, HealthResponse


_start_time: float = 0.0


def set_start_time(t: float):
    global _start_time
    _start_time = t


def diagnose(bridge) -> HealthResponse:
    """Evalúa el estado de todos los componentes y devuelve diagnóstico."""
    components: list[ComponentStatus] = []
    errors: list[str] = []
    overall = "healthy"

    # 1. Bridge
    if bridge is None:
        components.append(ComponentStatus(name="bridge", status="error", detail="No inicializado"))
        errors.append("Bridge is None")
        overall = "unhealthy"
    else:
        bridge_ok = bridge.is_authenticated
        components.append(ComponentStatus(
            name="bridge",
            status="ok" if bridge_ok else "degraded",
            detail="Autenticado" if bridge_ok else "No autenticado en ChatGPT"
        ))
        if not bridge_ok:
            errors.append("ChatGPT session not authenticated")
            overall = "degraded"

    # 2. Browser
    try:
        from browser import BrowserManager
        components.append(ComponentStatus(name="browser", status="ok", detail="Playwright + Chromium"))
    except Exception as e:
        components.append(ComponentStatus(name="browser", status="error", detail=str(e)[:80]))
        errors.append(str(e))
        overall = "unhealthy"

    # 3. Python
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    components.append(ComponentStatus(name="python", status="ok", detail=py_ver))

    # 4. Session store
    from session_store import get_store
    convs = get_store().list_all()
    components.append(ComponentStatus(
        name="session_store", status="ok",
        detail=f"{len(convs)} conversaciones guardadas"
    ))

    # 5. Token counter
    try:
        from token_counter import count_tokens
        count_tokens("test")
        components.append(ComponentStatus(name="tiktoken", status="ok", detail="cl100k_base"))
    except Exception:
        components.append(ComponentStatus(name="tiktoken", status="degraded", detail="Fallback len/4"))

    # 6. Queue + Rate Limiter (from global state)
    from queue_manager import RequestQueue
    from rate_limiter import RateLimiter
    from graceful_shutdown import GracefulShutdown
    import server as srv
    if hasattr(srv, 'QUEUE'):
        q = srv.QUEUE
        components.append(ComponentStatus(name="queue", status="ok", detail=f"{q.pending} en cola"))
    if hasattr(srv, 'LIMITER'):
        rl = srv.LIMITER
        components.append(ComponentStatus(name="rate_limiter", status="ok", detail=f"{rl.stats['rpm']} RPM"))
    if hasattr(srv, 'SHUTDOWN'):
        sd = srv.SHUTDOWN
        components.append(ComponentStatus(name="shutdown", status="ok" if not sd.shutting_down else "shutting_down", detail=f"{sd.active_requests} activos"))

    uptime = time.time() - _start_time if _start_time > 0 else 0.0

    return HealthResponse(
        status=overall,
        authenticated=bridge.is_authenticated if bridge else False,
        version="3.3.0",
        components=components,
        errors=errors,
        uptime_seconds=round(uptime, 1),
    )
