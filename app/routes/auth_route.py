from fastapi import APIRouter, Depends
from sqlmodel import Session
from pydantic import BaseModel

from app.core.database import get_session
from app.services.auth_service import AuthService

router = APIRouter()

# --- SKEMA REQUEST ---
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str


# --- ENDPOINTS ---
@router.post("/register")
def register(req: RegisterRequest, session: Session = Depends(get_session)):
    return AuthService.register_user(
        session=session, 
        username=req.username, 
        email=req.email, 
        password=req.password
    )

@router.post("/login")
def login(req: LoginRequest, session: Session = Depends(get_session)):
    return AuthService.login_user(
        session=session, 
        username=req.username, 
        password=req.password
    )

@router.post("/google")
def google_auth(req: GoogleAuthRequest, session: Session = Depends(get_session)):
    return AuthService.google_login(
        session=session, 
        token=req.token
    )