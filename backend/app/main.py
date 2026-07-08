from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routes import auth, transactions, categories, goals, debts, ai_assistant
from app.logger import security_logger, log_rate_limit, log_internal_error
from app.monitor import record_error_event, check_suspicious_ip
import time
import os

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
IS_PRODUCTION = os.environ.get("ENVIRONMENT", "production").lower() == "production"

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        for h in ["Server", "X-Powered-By"]:
            try:
                del response.headers[h]
            except KeyError:
                pass
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        ip = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method

        # Checks suspicious IP before processing
        check_suspicious_ip(ip=ip, path=path)

        response = await call_next(request)

        duration_ms = round((time.time() - start) * 1000)
        status = response.status_code

        if status == 429:
            log_rate_limit(ip=ip, path=path)
        elif status == 401:
            security_logger.warning(
                f'HTTP_401 | method={method} | path={path} | ip={ip} | duration={duration_ms}ms'
            )
        elif status == 403:
            security_logger.warning(
                f'HTTP_403 | method={method} | path={path} | ip={ip} | duration={duration_ms}ms'
            )
        elif status >= 500:
            log_internal_error(path=path, error_type=f'HTTP_{status}', ip=ip)
            record_error_event(path=path, status=status, ip=ip)
        elif path.startswith('/auth/'):
            security_logger.info(
                f'AUTH_REQUEST | method={method} | path={path} | status={status} | ip={ip} | duration={duration_ms}ms'
            )

        return response

app = FastAPI(
    title="FinWise API",
    description="FinWise financial education platform API",
    version="1.0.0",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://finwise-zeta-amber.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router,         prefix="/auth",         tags=["Auth"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(categories.router,   prefix="/categories",   tags=["Categories"])
app.include_router(goals.router,        prefix="/goals",        tags=["Goals"])
app.include_router(debts.router,        prefix="/debts",        tags=["Debts"])
app.include_router(ai_assistant.router, prefix="/ai",           tags=["AI"])

@app.get("/")
def root():
    return {"status": "FinWise API is running"}
