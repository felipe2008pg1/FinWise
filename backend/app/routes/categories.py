from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.database import supabase
from app.dependencies import get_current_user, get_token
from postgrest.exceptions import APIError

router = APIRouter()

class CategoryRequest(BaseModel):
    name: str
    type: str
    color: Optional[str] = '#6366f1'
    icon: Optional[str] = '💰'

def handle_supabase_error(e: Exception):
    msg = str(e)
    if "JWT expired" in msg or "PGRST303" in msg:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    raise HTTPException(status_code=500, detail=msg)

@router.get("/")
async def get_categories(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("categories")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("name")\
            .execute()
        return res.data
    except APIError as e:
        handle_supabase_error(e)

@router.post("/")
async def create_category(data: CategoryRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("categories").insert({
            "user_id": user_id,
            "name": data.name,
            "type": data.type,
            "color": data.color,
            "icon": data.icon
        }).execute()
        return res.data[0]
    except APIError as e:
        handle_supabase_error(e)

@router.put("/{category_id}")
async def update_category(category_id: str, data: CategoryRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        res = supabase.postgrest.auth(token).from_("categories").update({
            "name": data.name,
            "type": data.type,
            "color": data.color,
            "icon": data.icon
        }).eq("id", category_id).eq("user_id", user_id).execute()
        return res.data[0]
    except APIError as e:
        handle_supabase_error(e)

@router.delete("/{category_id}")
async def delete_category(category_id: str, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    try:
        supabase.postgrest.auth(token).from_("categories")\
            .delete()\
            .eq("id", category_id)\
            .eq("user_id", user_id)\
            .execute()
        return {"message": "Category deleted"}
    except APIError as e:
        handle_supabase_error(e)
