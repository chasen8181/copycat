import re
from typing import Optional

from pydantic import Field, field_validator

from helpers import CustomBaseModel, strip_whitespace

MAX_NOTE_TAGS = 10
TAG_COLOR_PALETTE = (
    "#3B82F6",
    "#10B981",
    "#EAB308",
    "#F97316",
    "#EF4444",
    "#EC4899",
    "#8B5CF6",
    "#6B7280",
)
HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


class NoteMetadata(CustomBaseModel):
    created_at: Optional[float] = Field(None)
    favorite: bool = Field(False)
    tag_ids: list[str] = Field(default_factory=list)


class MetadataTag(CustomBaseModel):
    id: str
    label: str
    color: str
    created_at: float


class MetadataState(CustomBaseModel):
    version: int = Field(1)
    notes: dict[str, NoteMetadata] = Field(default_factory=dict)
    tags: dict[str, MetadataTag] = Field(default_factory=dict)


class TagRef(CustomBaseModel):
    id: str
    label: str
    color: str


class Tag(TagRef):
    created_at: float
    usage_count: int = Field(0)


class TagCreate(CustomBaseModel):
    label: str
    color: str

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str) -> str:
        value = strip_whitespace(value)
        if len(value) == 0:
            raise ValueError("Tag label cannot be empty.")
        if len(value) > 32:
            raise ValueError("Tag label must be 32 characters or fewer.")
        return value

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str) -> str:
        if value not in TAG_COLOR_PALETTE and HEX_COLOR_RE.fullmatch(value) is None:
            raise ValueError("Invalid tag color.")
        return value


class TagUpdate(CustomBaseModel):
    label: Optional[str] = None
    color: Optional[str] = None

    @field_validator("label")
    @classmethod
    def validate_label(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = strip_whitespace(value)
        if len(value) == 0:
            raise ValueError("Tag label cannot be empty.")
        if len(value) > 32:
            raise ValueError("Tag label must be 32 characters or fewer.")
        return value

    @field_validator("color")
    @classmethod
    def validate_color(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in TAG_COLOR_PALETTE and HEX_COLOR_RE.fullmatch(value) is None:
            raise ValueError("Invalid tag color.")
        return value


def slugify_tag_id(label: str) -> str:
    value = label.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "tag"
