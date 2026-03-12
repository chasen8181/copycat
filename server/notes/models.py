from typing import List, Optional

from pydantic import Field
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated

from helpers import CustomBaseModel, is_valid_filename, strip_whitespace
from metadata.models import TagRef


class NoteBase(CustomBaseModel):
    title: str


class NoteCreate(CustomBaseModel):
    title: Annotated[
        str,
        AfterValidator(strip_whitespace),
        AfterValidator(is_valid_filename),
    ]
    content: Optional[str] = Field(None)
    favorite: bool = Field(False)
    tag_ids: Optional[list[str]] = Field(None)


class Note(CustomBaseModel):
    title: str
    content: Optional[str] = Field(None)
    last_modified: float
    created_at: float
    favorite: bool = Field(False)
    tags: list[TagRef] = Field(default_factory=list)
    group_id: Optional[str] = Field(None)
    group_name: Optional[str] = Field(None)


class NoteUpdate(CustomBaseModel):
    new_title: Annotated[
        Optional[str],
        AfterValidator(strip_whitespace),
        AfterValidator(is_valid_filename),
    ] = Field(None)
    new_content: Optional[str] = Field(None)
    favorite: Optional[bool] = Field(None)
    tag_ids: Optional[list[str]] = Field(None)


class SearchResult(CustomBaseModel):
    title: str
    last_modified: float
    created_at: float
    favorite: bool = Field(False)
    tags: list[TagRef] = Field(default_factory=list)
    group_id: Optional[str] = Field(None)
    group_name: Optional[str] = Field(None)

    score: Optional[float] = Field(None)
    title_highlights: Optional[str] = Field(None)
    content_highlights: Optional[str] = Field(None)
    tag_matches: Optional[List[str]] = Field(None)
