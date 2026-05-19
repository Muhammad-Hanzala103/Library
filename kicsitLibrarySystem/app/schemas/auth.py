from pydantic import BaseModel, EmailStr


class TokenData(BaseModel):
    user_id: int


class LoginForm(BaseModel):
    username_or_email: str
    password: str


class PermissionRead(BaseModel):
    code: str
    name: str
    module: str

    model_config = {"from_attributes": True}


class RoleRead(BaseModel):
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    is_active: bool
    roles: list[RoleRead] = []

    model_config = {"from_attributes": True}

