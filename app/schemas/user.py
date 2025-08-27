from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    mobile: str
    gender: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    mobile: str
    gender: str
    role: str