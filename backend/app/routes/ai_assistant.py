from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.database import supabase
from app.dependencies import get_current_user, get_token
from app.config import ANTHROPIC_API_KEY
import anthropic

router = APIRouter()
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

class MessageRequest(BaseModel):
    content: str

@router.get("/history")
async def get_history(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("ai_messages")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at")\
        .execute()
    return res.data

@router.post("/chat")
async def chat(data: MessageRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    # Busca histórico
    history_res = supabase.postgrest.auth(token).from_("ai_messages")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at")\
        .limit(20)\
        .execute()

    # Busca resumo financeiro
    transactions_res = supabase.postgrest.auth(token).from_("transactions")\
        .select("type, amount, title")\
        .eq("user_id", user_id)\
        .order("date", desc=True)\
        .limit(50)\
        .execute()

    total_income = sum(t["amount"] for t in transactions_res.data if t["type"] == "income")
    total_expense = sum(t["amount"] for t in transactions_res.data if t["type"] == "expense")

    # Monta histórico de mensagens
    messages = []
    for msg in history_res.data:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": data.content})

    # Chama Claude
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=f"""Você é o FinBot, assistente financeiro pessoal do FinWise.
Seja direto, amigável e prático. Use linguagem simples e exemplos brasileiros.
Dados financeiros recentes do usuário:
- Total de receitas: R$ {total_income:.2f}
- Total de despesas: R$ {total_expense:.2f}
- Saldo: R$ {total_income - total_expense:.2f}
Ajude com dicas, análises e planejamento financeiro baseado nesses dados.""",
        messages=messages
    )

    assistant_reply = response.content[0].text

    # Salva no histórico
    supabase.postgrest.auth(token).from_("ai_messages").insert([
        {"user_id": user_id, "role": "user", "content": data.content},
        {"user_id": user_id, "role": "assistant", "content": assistant_reply}
    ]).execute()

    return {"reply": assistant_reply}

@router.delete("/history")
async def clear_history(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    supabase.postgrest.auth(token).from_("ai_messages")\
        .delete()\
        .eq("user_id", user_id)\
        .execute()
    return {"message": "Histórico limpo"}