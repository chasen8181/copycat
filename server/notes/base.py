from abc import ABC, abstractmethod
from typing import Literal

from metadata.models import Tag

from .models import Note, NoteCreate, NoteUpdate, SearchResult


class BaseNotes(ABC):
    @abstractmethod
    def create(self, data: NoteCreate) -> Note:
        """Create a new note."""
        pass

    @abstractmethod
    def get(self, title: str) -> Note:
        """Get a specific note."""
        pass

    @abstractmethod
    def update(self, title: str, new_data: NoteUpdate) -> Note:
        """Update a specific note."""
        pass

    @abstractmethod
    def duplicate(self, title: str) -> Note:
        """Duplicate a specific note."""
        pass

    @abstractmethod
    def delete(self, title: str) -> None:
        """Delete a specific note.""" ""
        pass

    @abstractmethod
    def search(
        self,
        term: str,
        sort: Literal["score", "title", "last_modified", "created_at"] = "score",
        order: Literal["asc", "desc"] = "desc",
        favorites_first: bool = True,
        tag_ids: list[str] | None = None,
        tag_mode: Literal["and", "or"] = "and",
        favorite_only: bool = False,
        limit: int = None,
    ) -> list[SearchResult]:
        """Search for notes."""
        pass

    @abstractmethod
    def export(self, title: str):
        """Export a specific note."""
        pass

    @abstractmethod
    def get_tags(self) -> list[Tag]:
        """Get a list of all available tags."""
        pass
