from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from app.database import supabase
from app.logger import (
    log_auth_success, log_auth_failure,
    log_register, log_password_reset
)
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

def get_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

DEFAULT_CATEGORIES = [
    {"name": "Salary",        "type": "income",  "color": "#22c55e", "icon": "💰"},
    {"name": "Freelance",     "type": "income",  "color": "#14b8a6", "icon": "💻"},
    {"name": "Investments",   "type": "income",  "color": "#06b6d4", "icon": "📈"},
    {"name": "Other",         "type": "income",  "color": "#84cc16", "icon": "✨"},
    {"name": "Housing",       "type": "expense", "color": "#f97316", "icon": "🏠"},
    {"name": "Food",          "type": "expense", "color": "#ef4444", "icon": "🍔"},
    {"name": "Transport",     "type": "expense", "color": "#3b82f6", "icon": "🚗"},
    {"name": "Health",        "type": "expense", "color": "#ec4899", "icon": "💊"},
    {"name": "Entertainment", "type": "expense", "color": "#a855f7", "icon": "🎮"},
    {"name": "Education",     "type": "expense", "color": "#6366f1", "icon": "📚"},
    {"name": "Shopping",      "type": "expense", "color": "#eab308", "icon": "🛍️"},
    {"name": "Other",         "type": "expense", "color": "#64748b", "icon": "📦"},
]

def create_default_categories(user_id: str, access_token: str):
    rows = [{**cat, "user_id": user_id} for cat in DEFAULT_CATEGORIES]
    supabase.postgrest.auth(access_token).from_("categories").insert(rows).execute()

@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest):
    ip = get_ip(request)
    try:
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {"data": {"full_name": data.full_name}}
        })

        if not res.user:
            log_register(email=data.email, ip=ip, success=False)
            raise HTTPException(status_code=400, detail="Registration failed. Please try again.")

        log_register(email=data.email, ip=ip, success=True)

        if res.session:
            try:
                create_default_categories(res.user.id, res.session.access_token)
            except Exception:
                pass

        return {"message": "Registration complete! Please check your email to confirm your account."}
    except HTTPException:
        raise
    except Exception:
        log_register(email=data.email, ip=ip, success=False)
        raise HTTPException(status_code=400, detail="Registration failed. Please check your data and try again.")

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest):
    ip = get_ip(request)
    try:
        res = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        log_auth_success(user_id=res.user.id, email=data.email, ip=ip)

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
    except HTTPException:
        raise
    except Exception:
        log_auth_failure(email=data.email, ip=ip, reason="invalid_credentials")
        raise HTTPException(status_code=401, detail="Invalid email or password.")

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class UpdatePasswordRequest(BaseModel):
    new_password: str
    access_token: str

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ResetPasswordRequest):
    ip = get_ip(request)
    try:
        supabase.auth.reset_password_email(data.email)
    except Exception:
        pass
    log_password_reset(email=data.email, ip=ip)
    return {"message": "If this email is registered, you will receive a reset link shortly."}

@router.post("/update-password")
@limiter.limit("5/minute")
async def update_password(request: Request, data: UpdatePasswordRequest):
    try:
        supabase.auth.set_session(data.access_token, "")
        supabase.auth.update_user({"password": data.new_password})
        return {"message": "Password updated successfully."}
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to update password. The link may have expired.")
