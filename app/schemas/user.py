from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "Employee"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    phone: str | None = None
    position: str | None = None
    profile_image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str    
    
class LogoutRequest(BaseModel):
    refresh_token: str    
class UserProfileUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    position: str | None = None
    profile_image: str | None = None    
    
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str