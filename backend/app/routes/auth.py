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
            raise HTTPException(status_code=400, detail="Error creating user")

        return {"message": "Cadastro realizado! Verifique seu email para confirmar a conta.", "user": res.user}
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
    
class ResetPasswordRequest(BaseModel):
    email: EmailStr

class UpdatePasswordRequest(BaseModel):
    new_password: str
    access_token: str

@router.post("/forgot-password")
async def forgot_password(data: ResetPasswordRequest):
    try:
        supabase.auth.reset_password_email(data.email)
        return {"message": "Reset email sent!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/update-password")
async def update_password(data: UpdatePasswordRequest):
    try:
        supabase.auth.set_session(data.access_token, "")
        supabase.auth.update_user({"password": data.new_password})
        return {"message": "Password updated successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))