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

DEFAULT_CATEGORIES = [
    {"name": "Salário",      "type": "income",  "color": "#22c55e", "icon": "💰"},
    {"name": "Freelance",    "type": "income",  "color": "#14b8a6", "icon": "💻"},
    {"name": "Investimentos","type": "income",  "color": "#06b6d4", "icon": "📈"},
    {"name": "Outros",       "type": "income",  "color": "#84cc16", "icon": "✨"},
    {"name": "Moradia",      "type": "expense", "color": "#f97316", "icon": "🏠"},
    {"name": "Alimentação",  "type": "expense", "color": "#ef4444", "icon": "🍔"},
    {"name": "Transporte",   "type": "expense", "color": "#3b82f6", "icon": "🚗"},
    {"name": "Saúde",        "type": "expense", "color": "#ec4899", "icon": "💊"},
    {"name": "Lazer",        "type": "expense", "color": "#a855f7", "icon": "🎮"},
    {"name": "Educação",     "type": "expense", "color": "#6366f1", "icon": "📚"},
    {"name": "Compras",      "type": "expense", "color": "#eab308", "icon": "🛍️"},
    {"name": "Outros",       "type": "expense", "color": "#64748b", "icon": "📦"},
]

def create_default_categories(user_id: str, access_token: str):
    rows = [{**cat, "user_id": user_id} for cat in DEFAULT_CATEGORIES]
    supabase.postgrest.auth(access_token).from_("categories").insert(rows).execute()

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

        # If the register alredy with active section (email confirmation off).
        # Use the token to create the default categories in Hour.
        if res.session:
            try:
                create_default_categories(res.user.id, res.session.access_token)
            except Exception:
                # Don't let category creation break the user registration.
                pass

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

        # Ensures default categories are also assigned upon first login
        # (covers the case of registration with mandatory email confirmation,
        # where there was no active session at the time of /register)
        try:
            existing = supabase.postgrest.auth(res.session.access_token)\
                .from_("categories").select("id").eq("user_id", res.user.id).limit(1).execute()
            if not existing.data:
                create_default_categories(res.user.id, res.session.access_token)
        except Exception:
            pass

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
