from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.database import supabase
from app.dependencies import get_current_user, get_token

router = APIRouter()

class CategoryRequest(BaseModel):
    name: str
    type: str
    color: Optional[str] = '#6366f1'
    icon: Optional[str] = '💰'

@router.get("/")
async def get_categories(token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("categories")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("name")\
        .execute()
    return res.data

@router.post("/")
async def create_category(data: CategoryRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("categories").insert({
        "user_id": user_id,
        "name": data.name,
        "type": data.type,
        "color": data.color,
        "icon": data.icon
    }).execute()
    return res.data[0]

@router.put("/{category_id}")
async def update_category(category_id: str, data: CategoryRequest, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    res = supabase.postgrest.auth(token).from_("categories").update({
        "name": data.name,
        "type": data.type,
        "color": data.color,
        "icon": data.icon
    }).eq("id", category_id).eq("user_id", user_id).execute()
    return res.data[0]

@router.delete("/{category_id}")
async def delete_category(category_id: str, token: str = Depends(get_token), user_id: str = Depends(get_current_user)):
    supabase.postgrest.auth(token).from_("categories")\
        .delete()\
        .eq("id", category_id)\
        .eq("user_id", user_id)\
        .execute()
    return {"message": "Categoria deletada"}