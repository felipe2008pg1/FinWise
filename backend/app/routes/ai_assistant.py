from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.database import supabase
from app.dependencies import get_current_user, get_token
from app.config import ANTHROPIC_API_KEY
from postgrest.exceptions import APIError
import anthropic

router = APIRouter()
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

def handle_supabase_error(e: APIError):
    msg = str(e)
    if "JWT expired" in msg or "PGRST303" in msg:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    raise HTTPException(status_code=500, detail="An internal error occurred. Please try again.")

@router.get("/history")
async def get_history(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("ai_messages")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at")\
            .execute()
        return res.data
    except APIError as e:
        handle_supabase_error(e)

@router.post("/chat")
async def chat(data: MessageRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        history_res = supabase.postgrest.auth(token).from_("ai_messages")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at")\
            .limit(20)\
            .execute()

        transactions_res = supabase.postgrest.auth(token).from_("transactions")\
            .select("type, amount, title")\
            .eq("user_id", user_id)\
            .order("date", desc=True)\
            .limit(50)\
            .execute()

        total_income = sum(t["amount"] for t in transactions_res.data if t["type"] == "income")
        total_expense = sum(t["amount"] for t in transactions_res.data if t["type"] == "expense")

        messages = []
        for msg in history_res.data:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": data.content})

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=f"""You are FinBot, FinWise's personal financial assistant.
Be direct, friendly, and practical. Use simple language and real-world examples.
The user's recent financial data:
- Total income: ${total_income:.2f}
- Total expenses: ${total_expense:.2f}
- Balance: ${total_income - total_expense:.2f}
Provide tips, insights, and financial planning advice based on this data.""",
            messages=messages
        )

        assistant_reply = response.content[0].text

        supabase.postgrest.auth(token).from_("ai_messages").insert([
            {"user_id": user_id, "role": "user", "content": data.content},
            {"user_id": user_id, "role": "assistant", "content": assistant_reply}
        ]).execute()

        return {"reply": assistant_reply}
    except HTTPException:
        raise
    except APIError as e:
        handle_supabase_error(e)
    except anthropic.APIError:
        raise HTTPException(status_code=503, detail="AI service temporarily unavailable. Please try again later.")
    except Exception:
        raise HTTPException(status_code=500, detail="An internal error occurred. Please try again.")

@router.delete("/history")
async def clear_history(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        supabase.postgrest.auth(token).from_("ai_messages")\
            .delete()\
            .eq("user_id", user_id)\
            .execute()
        return {"message": "History cleared"}
    except APIError as e:
        handle_supabase_error(e)
