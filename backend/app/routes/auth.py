from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from app.database import supabase
from app.logger import (
    log_auth_success, log_auth_failure,
    log_register, log_password_reset,
    security_logger
)
from slowapi import Limiter
from slowapi.util import get_remote_address
import time

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

def get_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"

MIN_RESPONSE_TIME = 0.3

def constant_time_response(start: float):
    elapsed = time.monotonic() - start
    if elapsed < MIN_RESPONSE_TIME:
        time.sleep(MIN_RESPONSE_TIME - elapsed)

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)

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
    start = time.monotonic()
    try:
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {"data": {"full_name": data.full_name}}
        })

        if not res.user:
            log_register(email=data.email, ip=ip, success=False)
            constant_time_response(start)
            return {"message": "Registration complete! Please check your email to confirm your account."}

        log_register(email=data.email, ip=ip, success=True)

        if res.session:
            try:
                create_default_categories(res.user.id, res.session.access_token)
            except Exception:
                pass

        constant_time_response(start)
        return {"message": "Registration complete! Please check your email to confirm your account."}
    except HTTPException:
        raise
    except Exception:
        log_register(email=data.email, ip=ip, success=False)
        constant_time_response(start)
        return {"message": "Registration complete! Please check your email to confirm your account."}

@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest):
    ip = get_ip(request)
    start = time.monotonic()
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

        constant_time_response(start)
        return {
            "access_token": res.session.access_token,
            # Returns the refresh token so the frontend can renew the session.
            "refresh_token": res.session.refresh_token,
            "user": res.user
        }
    except HTTPException:
        raise
    except Exception:
        log_auth_failure(email=data.email, ip=ip, reason="invalid_credentials")
        constant_time_response(start)
        raise HTTPException(status_code=401, detail="Invalid email or password.")

@router.post("/refresh")
@limiter.limit("30/minute")
async def refresh_token(request: Request, data: RefreshTokenRequest):
    """
    Recebe o refresh_token, invalida o token atual no Supabase
    e emite um novo par access_token + refresh_token.
    Isso previne replay attacks: cada refresh_token só pode ser usado uma vez.
    """
    ip = get_ip(request)
    try:
        res = supabase.auth.refresh_session(data.refresh_token)

        if not res.session:
            security_logger.warning(f'REFRESH_FAILURE | ip={ip} | reason=no_session')
            raise HTTPException(status_code=401, detail="Invalid or expired session. Please log in again.")

        security_logger.info(f'TOKEN_REFRESHED | user_id={res.user.id} | ip={ip}')

        return {
            "access_token": res.session.access_token,
            "refresh_token": res.session.refresh_token,
            "user": res.user
        }
    except HTTPException:
        raise
    except Exception:
        security_logger.warning(f'REFRESH_FAILURE | ip={ip} | reason=exception')
        raise HTTPException(status_code=401, detail="Invalid or expired session. Please log in again.")

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class UpdatePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)
    access_token: str

@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ResetPasswordRequest):
    ip = get_ip(request)
    start = time.monotonic()
    try:
        supabase.auth.reset_password_email(data.email)
    except Exception:
        pass
    log_password_reset(email=data.email, ip=ip)
    constant_time_response(start)
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
