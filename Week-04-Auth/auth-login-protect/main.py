from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security_scheme = HTTPBearer()
import os
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional
from fastapi import FastAPI, HTTPException, Header

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Auth API",
    description="A secure API with Supabase authentication.",
    version="1.0"
)

print("Server running and connected to Supabase")

@app.get("/")
def read_root():
    return {"message": "Server running and connected to Supabase"}

    from pydantic import BaseModel
from fastapi import HTTPException

class AuthCredentials(BaseModel):
    email: str = None
    password: str = None

@app.post("/auth/signup", status_code=201)
def signup(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        return {"user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
def login(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid login credentials")


from typing import Optional

@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}



def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Access token required")

    try:
        user_response = supabase.auth.get_user(token)
        return {"user": user_response.user, "token": token}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/protected/profile")
def protected_profile(auth_data: dict = Depends(verify_token)):
    user = auth_data["user"]
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

@app.get("/protected/dashboard")
def protected_dashboard(auth_data: dict = Depends(verify_token)):
    user = auth_data["user"]
    return {"message": f"Welcome to your dashboard, {user.email}!"}

@app.post("/auth/logout", status_code=204)
def logout(auth_data: dict = Depends(verify_token)):
    try:
        supabase.auth.sign_out()
        return
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))