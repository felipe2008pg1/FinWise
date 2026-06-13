from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, transactions, categories, goals, debts, ai_assistant

app = FastAPI(
    title="FinWise API",
    description="API da plataforma de educação financeira FinWise",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,         prefix="/auth",         tags=["Auth"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transações"])
app.include_router(categories.router,   prefix="/categories",   tags=["Categorias"])
app.include_router(goals.router,        prefix="/goals",        tags=["Metas"])
app.include_router(debts.router,        prefix="/debts",        tags=["Dívidas"])
app.include_router(ai_assistant.router, prefix="/ai",           tags=["IA"])

@app.get("/")
def root():
    return {"status": "FinWise API rodando"}