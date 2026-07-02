from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from app.database import supabase
from app.dependencies import get_current_user, get_token
from postgrest.exceptions import APIError

router = APIRouter()

class TransactionRequest(BaseModel):
    category_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(income|expense)$")
    date: date
    notes: Optional[str] = Field(None, max_length=500)

def handle_supabase_error(e: APIError):
    msg = str(e)
    if "JWT expired" in msg or "PGRST303" in msg:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    raise HTTPException(status_code=500, detail="An internal error occurred. Please try again.")

@router.get("/")
async def get_transactions(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("transactions")\
            .select("*, categories(name, color, icon)")\
            .eq("user_id", user_id)\
            .order("date", desc=True)\
            .execute()
        return res.data
    except APIError as e:
        handle_supabase_error(e)

@router.post("/")
async def create_transaction(data: TransactionRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("transactions").insert({
            "user_id": user_id,
            "category_id": data.category_id,
            "title": data.title,
            "amount": data.amount,
            "type": data.type,
            "date": str(data.date),
            "notes": data.notes
        }).execute()
        return res.data[0]
    except APIError as e:
        handle_supabase_error(e)

@router.put("/{transaction_id}")
async def update_transaction(transaction_id: str, data: TransactionRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("transactions").update({
            "category_id": data.category_id,
            "title": data.title,
            "amount": data.amount,
            "type": data.type,
            "date": str(data.date),
            "notes": data.notes
        }).eq("id", transaction_id).eq("user_id", user_id).execute()
        return res.data[0]
    except APIError as e:
        handle_supabase_error(e)

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        supabase.postgrest.auth(token).from_("transactions")\
            .delete()\
            .eq("id", transaction_id)\
            .eq("user_id", user_id)\
            .execute()
        return {"message": "Transaction deleted"}
    except APIError as e:
        handle_supabase_error(e)
