from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import supabase

security = HTTPBearer()

async def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return credentials.credentials

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the JWT by calling Supabase Auth directly.
    This verifies the signature server-side — unlike manual base64 decoding,
    which only reads the payload without verifying authenticity.
    A forged token with a valid structure but wrong signature will be rejected here.
    """
    token = credentials.credentials
    try:
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token.")
        return user.user.id
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
