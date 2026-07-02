from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routes import auth, transactions, categories, goals, debts, ai_assistant

# Rate limiter global — identifies by IP address
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title="FinWise API",
    description="FinWise financial education platform API",
    version="1.0.0",
    # Disables automatic exposure of docs in production (optional — comment out if you want to keep /docs)
    # docs_url=None,
    # redoc_url=None,
)

# Registers the limiter and the 429 error handler.
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
