from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.database import supabase

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(data: RegisterRequest):
    try:
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {"data": {"full_name": data.full_name}}
        })

        if not res.user:
            raise HTTPException(status_code=400, detail="Erro ao criar usuário")

        # Confirma email automaticamente via SQL
        supabase.postgrest.schema("auth").from_("users").update({
            "email_confirmed_at": "now()"
        }).eq("id", res.user.id).execute()

        return {"message": "Cadastro realizado! Já pode fazer login.", "user": res.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(data: LoginRequest):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return {
            "access_token": res.session.access_token,
            "user": res.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))