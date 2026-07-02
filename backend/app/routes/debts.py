from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.database import supabase
from app.dependencies import get_current_user, get_token
from postgrest.exceptions import APIError

router = APIRouter()

class DebtRequest(BaseModel):
    title: str
    total_amount: float
    remaining_amount: float
    interest_rate: Optional[float] = 0
    monthly_payment: Optional[float] = None
    due_day: Optional[int] = None

def handle_supabase_error(e: Exception):
    msg = str(e)
    if "JWT expired" in msg or "PGRST303" in msg:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    raise HTTPException(status_code=500, detail=msg)

@router.get("/")
async def get_debts(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("debts")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        return res.data
    except APIError as e:
        handle_supabase_error(e)

@router.post("/")
async def create_debt(data: DebtRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("debts").insert({
            "user_id": user_id,
            "title": data.title,
            "total_amount": data.total_amount,
            "remaining_amount": data.remaining_amount,
            "interest_rate": data.interest_rate,
            "monthly_payment": data.monthly_payment,
            "due_day": data.due_day
        }).execute()
        return res.data[0]
    except APIError as e:
        handle_supabase_error(e)

@router.put("/{debt_id}")
async def update_debt(debt_id: str, data: DebtRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("debts").update({
            "title": data.title,
            "total_amount": data.total_amount,
            "remaining_amount": data.remaining_amount,
            "interest_rate": data.interest_rate,
            "monthly_payment": data.monthly_payment,
            "due_day": data.due_day
        }).eq("id", debt_id).eq("user_id", user_id).execute()
        return res.data[0]
    except APIError as e:
        handle_supabase_error(e)

@router.patch("/{debt_id}/pay")
async def mark_debt_paid(debt_id: str, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("debts").update({
            "status": "paid",
            "remaining_amount": 0
        }).eq("id", debt_id).eq("user_id", user_id).execute()
        return res.data[0]
    except APIError as e:
        handle_supabase_error(e)

@router.delete("/{debt_id}")
async def delete_debt(debt_id: str, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        supabase.postgrest.auth(token).from_("debts")\
            .delete()\
            .eq("id", debt_id)\
            .eq("user_id", user_id)\
            .execute()
        return {"message": "Debt deleted"}
    except APIError as e:
        handle_supabase_error(e)

@router.get("/{debt_id}/simulate")
async def simulate_debt(debt_id: str, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("debts")\
            .select("*")\
            .eq("id", debt_id)\
            .eq("user_id", user_id)\
            .execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Debt not found")
        debt = res.data[0]
        remaining = debt["remaining_amount"]
        rate = debt["interest_rate"] / 100 / 12
        payment = debt["monthly_payment"]
        if not payment or payment <= 0:
            return {"error": "Monthly payment not defined"}
        months = 0
        total_paid = 0
        while remaining > 0 and months < 600:
            interest = remaining * rate
            remaining = remaining + interest - payment
            total_paid += payment
            months += 1
            if remaining < 0:
                total_paid += remaining
                remaining = 0
        return {
            "months_to_pay": months,
            "total_paid": round(total_paid, 2),
            "total_interest": round(total_paid - debt["remaining_amount"], 2)
        }
    except APIError as e:
        handle_supabase_error(e)
