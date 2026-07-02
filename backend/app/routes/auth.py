from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from app.database import supabase
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

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

# 5 attempts per minute per IP — then blocks with a 429
@router.post("/register")
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest):
    try:
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {"data": {"full_name": data.full_name}}
        })

        if not res.user:
            raise HTTPException(status_code=400, detail="Registration failed. Please try again.")

        if res.session:
            try:
                create_default_categories(res.user.id, res.session.access_token)
            except Exception:
                pass

        # Generic message — does not reveal whether the email already exists (anti-enumeration)
        return {"message": "Registration complete! Please check your email to confirm your account."}
    except HTTPException:
        raise
    except Exception:
        # Never exposes internal details
        raise HTTPException(status_code=400, detail="Registration failed. Please check your data and try again.")

# 10 attempts per minute per IP — brute-force protection
@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest):
    try:
        res = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        # Creates default categories upon first login if they do not exist.
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
        # Generic message — does not reveal whether the email exists (anti-enumeration)
        raise HTTPException(status_code=401, detail="Invalid email or password.")

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class UpdatePasswordRequest(BaseModel):
    new_password: str
    access_token: str

# 3 attempts per minute — prevents email-sending abuse
@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ResetPasswordRequest):
    try:
        supabase.auth.reset_password_email(data.email)
    except Exception:
        pass
    # Always returns success — does not reveal whether the email exists.
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
