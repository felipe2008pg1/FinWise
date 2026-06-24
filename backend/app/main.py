from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, transactions, categories, goals, debts, ai_assistant

app = FastAPI(
    title="FinWise API",
    description="FinWise financial education platform API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://finwise-zeta-amber.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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