from abc import ABC, abstractmethod

from .models import AuthPrincipal, Login, Token


class BaseAuth(ABC):
    @abstractmethod
    def login(self, data: Login) -> Token:
        """Login a user."""
        pass

    @abstractmethod
    def authenticate(self, request, token: str | None = None) -> AuthPrincipal:
        """Authenticate a user."""
        pass
