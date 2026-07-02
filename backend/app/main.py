from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routes import auth, transactions, categories, goals, debts, ai_assistant

# ===== RATE LIMITER =====
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# ===== SECURITY HEADERS MIDDLEWARE =====
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Forces HTTPS for 1 year, includes subdomains
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Blocks clickjacking — the page cannot be embedded in an iframe.
        response.headers["X-Frame-Options"] = "DENY"

        # Blocks MIME sniffing — the browser must respect the declared Content-Type.
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Does not send the Referer to other domains
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Disables browser APIs that are unnecessary for a REST API.
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )

        # CSP — REST APIs serve only JSON, not HTML/JS, so it can be restrictive.
        response.headers["Content-Security-Policy"] = "default-src 'none'"

        # Remove header that exposes server info
        for h in ["Server", "X-Powered-By"]:
            try:
                del response.headers[h]
            except KeyError:
                pass

        return response

# ===== APP =====
app = FastAPI(
    title="FinWise API",
    description="FinWise financial education platform API",
    version="1.0.0",
)

# Order matters: SecurityHeaders before CORS.
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
