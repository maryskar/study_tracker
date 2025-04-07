from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    userId: int
    token: str

class RecoverPasswordRequest(BaseModel):
    email: EmailStr

class RecoverPasswordResponse(BaseModel):
    message: str
