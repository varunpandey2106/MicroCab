from pydantic import BaseModel, EmailStr, Field
from fastapi_jwt_auth import AuthJWT
import os
from typing import List  # Import List type from typing module

SECRET_KEY=os.getenv('SECRET_KEY', 'secret')

class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
    # authjwt_token_location:str = 'headers'
    authjwt_token_location: List[str] = ['headers']  # Define as a List[str] instead of a dict
    authjwt_cookie_csrf_protect: bool = True
    # authjwt_cookie_samesite:str ='lax'

@AuthJWT.load_config
def get_config():
    return Settings()

class Signup(BaseModel):
    email:EmailStr
    password:str
    fullname:str

class UserDetails(BaseModel):
    id:str
    email:EmailStr
    fullname:str

    class Config:
        orm_mode=True

class Login(BaseModel):
    email:EmailStr
    password:str=Field(default=None)

class LoginDetails(BaseModel):
    user:UserDetails
    access_token:str
    refresh_token:str

    class Config:
        orm_mode=True


