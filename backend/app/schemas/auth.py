from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str


class UserPublic(BaseModel):
    email: str
    name: str
    role: str
    department: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1)
    role: str = Field(default="employee", pattern="^(admin|analyst|employee|viewer)$")
    department: str = Field(default="General", min_length=1)
    password: str = Field(min_length=8)
