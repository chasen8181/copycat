from typing import Literal

from pydantic import BaseModel, Field

from helpers import CustomBaseModel


class Login(CustomBaseModel):
    username: str
    password: str


class Token(BaseModel):
    # Note: OAuth requires keys to be snake_case so we use the standard
    # BaseModel here
    access_token: str
    token_type: str = Field("bearer")


class AuthPrincipal(CustomBaseModel):
    authenticated: bool = True
    username: str
    role: Literal["admin", "user"]
    group_ids: list[str] = Field(default_factory=list)
    is_admin: bool = False
