from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.database import supabase
from app.dependencies import get_current_user, get_token

router = APIRouter()

class TransactionRequest(BaseModel):
    category_id: Optional[str] = None
    title: str
    amount: float
    type: str
    date: date
    notes: Optional[str] = None

@router.get("/")
async def get_transactions(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("transactions")\
        .select("*, categories(name, color, icon)")\
        .eq("user_id", user_id)\
        .order("date", desc=True)\
        .execute()
    return res.data

@router.post("/")
async def create_transaction(data: TransactionRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
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

@router.put("/{transaction_id}")
async def update_transaction(transaction_id: str, data: TransactionRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("transactions").update({
        "category_id": data.category_id,
        "title": data.title,
        "amount": data.amount,
        "type": data.type,
        "date": str(data.date),
        "notes": data.notes
    }).eq("id", transaction_id).eq("user_id", user_id).execute()
    return res.data[0]

@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    supabase.postgrest.auth(token).from_("transactions")\
        .delete()\
        .eq("id", transaction_id)\
        .eq("user_id", user_id)\
        .execute()
    return {"message": "Transação deletada"}