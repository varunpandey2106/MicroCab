from pydantic import BaseModel, Field
from fastapi_jwt_auth import AuthJWT
import os

SECRET_KEY=os.getenv('SECRET_KEY', 'secret')

class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
    authjwt_token_location:set ={'headers'}
    authjwt_cookie_csrf_protect: bool = True
    # authjwt_cookie_samesite:str ='lax'

@AuthJWT.load_config
def get_config():
    return Settings()


class Location(BaseModel):
    lon: float = Field(le=180, ge=-180)
    lat: float=Field(le=90, ge=-90)