from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    user: str
    password: str


class LoginResponse(BaseModel):
    TOKEN: str


@router.post("/auth/login/bypass", response_model=LoginResponse)
async def login_bypass(body: LoginRequest):
    return LoginResponse(TOKEN="sigri-mock-token-2026")
