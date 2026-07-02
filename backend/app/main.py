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

        # Força HTTPS por 1 ano, inclui subdomínios
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Bloqueia clickjacking — a página não pode ser embutida em iframe
        response.headers["X-Frame-Options"] = "DENY"

        # Bloqueia MIME sniffing — browser deve respeitar o Content-Type declarado
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Não envia o Referer para outros domínios
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Desabilita APIs do browser desnecessárias para uma API REST
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )

        # CSP — API REST só serve JSON, não HTML/JS, então pode ser restritivo
        response.headers["Content-Security-Policy"] = "default-src 'none'"

        # Remove header que expõe info do servidor
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

# Ordem importa: SecurityHeaders antes do CORS
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
