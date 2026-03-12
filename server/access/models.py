import re
from typing import Literal, Optional

from pydantic import Field, field_validator

from helpers import CustomBaseModel, strip_whitespace


def slugify_group_id(value: str) -> str:
    value = strip_whitespace(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "group"


class GroupSummary(CustomBaseModel):
    id: str
    name: str


class GroupRecord(GroupSummary):
    slug: str
    created_at: float
    is_active: bool = True


class UserRecord(CustomBaseModel):
    id: str
    username: str
    password_hash: str
    display_name: Optional[str] = None
    group_ids: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: float


class GroupsState(CustomBaseModel):
    version: int = 1
    groups: dict[str, GroupRecord] = Field(default_factory=dict)


class UsersState(CustomBaseModel):
    version: int = 1
    users: dict[str, UserRecord] = Field(default_factory=dict)


class GroupCreate(CustomBaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = strip_whitespace(value)
        if len(value) == 0:
            raise ValueError("Group name cannot be empty.")
        if len(value) > 48:
            raise ValueError("Group name must be 48 characters or fewer.")
        return value


class GroupUpdate(CustomBaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = strip_whitespace(value)
        if len(value) == 0:
            raise ValueError("Group name cannot be empty.")
        if len(value) > 48:
            raise ValueError("Group name must be 48 characters or fewer.")
        return value


class UserCreate(CustomBaseModel):
    username: str
    password: str
    display_name: Optional[str] = None
    group_ids: list[str] = Field(default_factory=list)
    is_active: bool = True

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = strip_whitespace(value)
        if len(value) == 0:
            raise ValueError("Username cannot be empty.")
        if len(value) > 32:
            raise ValueError("Username must be 32 characters or fewer.")
        if not re.fullmatch(r"[a-zA-Z0-9._-]+", value):
            raise ValueError(
                "Username can only contain letters, numbers, '.', '_' or '-'."
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return value

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = strip_whitespace(value)
        if len(value) > 64:
            raise ValueError("Display name must be 64 characters or fewer.")
        return value or None


class UserUpdate(CustomBaseModel):
    password: Optional[str] = None
    display_name: Optional[str] = None
    group_ids: Optional[list[str]] = None
    is_active: Optional[bool] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        return value

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = strip_whitespace(value)
        if len(value) > 64:
            raise ValueError("Display name must be 64 characters or fewer.")
        return value or None


class AdminGroup(GroupSummary):
    slug: str
    created_at: float
    is_active: bool = True
    note_count: int = 0
    user_count: int = 0


class AdminUser(CustomBaseModel):
    id: str
    username: str
    display_name: Optional[str] = None
    group_ids: list[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: float


class LibraryScope(CustomBaseModel):
    kind: Literal["legacy", "group"]
    query_value: str
    display_name: str
    notes_path: str
    attachments_path: str
    metadata_path: str
    index_path: str
    group_id: str | None = None
    group_slug: str | None = None
