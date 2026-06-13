from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.database import supabase
from app.dependencies import get_current_user

router = APIRouter()

class TransactionRequest(BaseModel):
    category_id: Optional[str] = None
    title: str
    amount: float
    type: str  # 'income' ou 'expense'
    date: date
    notes: Optional[str] = None

@router.get("/")
def get_transactions(user_id: str = Depends(get_current_user)):
    res = supabase.table("transactions")\
        .select("*, categories(name, color, icon)")\
        .eq("user_id", user_id)\
        .order("date", desc=True)\
        .execute()
    return res.data

@router.post("/")
def create_transaction(data: TransactionRequest, user_id: str = Depends(get_current_user)):
    res = supabase.table("transactions").insert({
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
def update_transaction(transaction_id: str, data: TransactionRequest, user_id: str = Depends(get_current_user)):
    res = supabase.table("transactions").update({
        "category_id": data.category_id,
        "title": data.title,
        "amount": data.amount,
        "type": data.type,
        "date": str(data.date),
        "notes": data.notes
    }).eq("id", transaction_id).eq("user_id", user_id).execute()
    return res.data[0]

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: str, user_id: str = Depends(get_current_user)):
    supabase.table("transactions")\
        .delete()\
        .eq("id", transaction_id)\
        .eq("user_id", user_id)\
        .execute()
    return {"message": "Transação deletada"}