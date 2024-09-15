from pydantic import BaseModel, Field, EmailStr


class SUserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class SUserLogin(BaseModel):
    email_username: str
    password: str


class UserAgentInfo(BaseModel):
    user_agent: str = Field(..., alias="User-Agent")
    accept_language: str = Field(..., alias="Accept-Language")
    accept: str = Field(..., alias="Accept")
    dnt: str = Field(None, alias="DNT")
    connection: str = Field(None, alias="Connection")
