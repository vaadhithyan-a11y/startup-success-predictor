from pydantic import BaseModel


class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "founder"
    full_name: str = ""


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    status: str
    message: str
    user_id: int
