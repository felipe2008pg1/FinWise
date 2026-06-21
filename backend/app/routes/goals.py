from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.database import supabase
from app.dependencies import get_current_user, get_token

router = APIRouter()

class GoalRequest(BaseModel):
    title: str
    target_amount: float
    current_amount: Optional[float] = 0
    deadline: Optional[date] = None

@router.get("/")
async def get_goals(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("goals")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .execute()
    return res.data

@router.post("/")
async def create_goal(data: GoalRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("goals").insert({
        "user_id": user_id,
        "title": data.title,
        "target_amount": data.target_amount,
        "current_amount": data.current_amount,
        "deadline": str(data.deadline) if data.deadline else None
    }).execute()
    return res.data[0]

@router.put("/{goal_id}")
async def update_goal(goal_id: str, data: GoalRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("goals").update({
        "title": data.title,
        "target_amount": data.target_amount,
        "current_amount": data.current_amount,
        "deadline": str(data.deadline) if data.deadline else None
    }).eq("id", goal_id).eq("user_id", user_id).execute()
    return res.data[0]

@router.patch("/{goal_id}/complete")
async def complete_goal(goal_id: str, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("goals").update({
        "status": "completed"
    }).eq("id", goal_id).eq("user_id", user_id).execute()
    return res.data[0]

@router.delete("/{goal_id}")
async def delete_goal(goal_id: str, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    supabase.postgrest.auth(token).from_("goals")\
        .delete()\
        .eq("id", goal_id)\
        .eq("user_id", user_id)\
        .execute()
    return {"message": "Goal deleted"}
