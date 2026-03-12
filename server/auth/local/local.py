import secrets
from base64 import b32encode
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pyotp import TOTP
from pyotp.utils import build_uri
from qrcode import QRCode

from access.passwords import verify_password
from access.store import AccessRegistryStore
from global_config import AuthType, GlobalConfig
from helpers import get_env

from ..base import BaseAuth
from ..models import AuthPrincipal, Login, Token

global_config = GlobalConfig()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token", auto_error=False)


class LocalAuth(BaseAuth):
    JWT_ALGORITHM = "HS256"

    def __init__(self) -> None:
        self.username = get_env("COPYCAT_USERNAME", mandatory=True)
        self.password = get_env("COPYCAT_PASSWORD", mandatory=True)
        self.secret_key = get_env("COPYCAT_SECRET_KEY", mandatory=True)
        self.session_expiry_days = get_env(
            "COPYCAT_SESSION_EXPIRY_DAYS", default=30, cast_int=True
        )
        self.registry = AccessRegistryStore()

        self.is_totp_enabled = False
        if global_config.auth_type == AuthType.TOTP:
            self.is_totp_enabled = True
            self.totp_key = get_env("COPYCAT_TOTP_KEY", mandatory=True)
            self.totp_key = b32encode(self.totp_key.encode("utf-8"))
            self.totp = TOTP(self.totp_key)
            self.last_used_totp = None
            self._display_totp_enrolment()

    def login(self, data: Login) -> Token:
        if self._is_bootstrap_admin_login(data):
            access_token = self._create_access_token(
                data={
                    "sub": self.username,
                    "role": "admin",
                    "group_ids": [],
                }
            )
            return Token(access_token=access_token)

        user = self.registry.get_user(data.username)
        if (
            user is None
            or user.is_active is False
            or verify_password(data.password, user.password_hash) is False
        ):
            raise ValueError("Incorrect login credentials.")

        access_token = self._create_access_token(
            data={
                "sub": user.username,
                "role": "user",
                "group_ids": user.group_ids,
            }
        )
        return Token(access_token=access_token)

    def authenticate(
        self, request: Request, token: str = Depends(oauth2_scheme)
    ) -> AuthPrincipal:
        if token is None:
            token = request.cookies.get("token")
        try:
            return self._validate_token(token)
        except (JWTError, ValueError):
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _is_bootstrap_admin_login(self, data: Login) -> bool:
        username_correct = secrets.compare_digest(
            self.username.lower(), data.username.lower()
        )

        expected_password = self.password
        current_totp = None
        if self.is_totp_enabled:
            current_totp = self.totp.now()
            expected_password += current_totp
        password_correct = secrets.compare_digest(
            expected_password, data.password
        )

        is_valid = username_correct and password_correct
        if self.is_totp_enabled:
            is_valid = is_valid and current_totp != self.last_used_totp
        if is_valid and self.is_totp_enabled:
            self.last_used_totp = current_totp
        return is_valid

    def _validate_token(self, token: str) -> AuthPrincipal:
        if token is None:
            raise ValueError
        payload = jwt.decode(
            token, self.secret_key, algorithms=[self.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role not in {"admin", "user"}:
            raise ValueError

        if role == "admin":
            if username.lower() != self.username.lower():
                raise ValueError
            return AuthPrincipal(
                username=self.username,
                role="admin",
                group_ids=[],
                is_admin=True,
            )

        user = self.registry.get_user(username)
        if user is None or user.is_active is False:
            raise ValueError
        return AuthPrincipal(
            username=user.username,
            role="user",
            group_ids=user.group_ids,
            is_admin=False,
        )

    def _create_access_token(self, data: dict):
        to_encode = data.copy()
        expiry_datetime = datetime.utcnow() + timedelta(
            days=self.session_expiry_days
        )
        to_encode.update({"exp": expiry_datetime})
        return jwt.encode(
            to_encode, self.secret_key, algorithm=self.JWT_ALGORITHM
        )

    def _display_totp_enrolment(self):
        unpadded_secret = self.totp_key.rstrip(b"=")
        uri = build_uri(unpadded_secret, self.username, issuer="CopyCat")
        qr = QRCode()
        qr.add_data(uri)
        print(
            "\nScan this QR code with your TOTP app of choice",
            "e.g. Authy or Google Authenticator:",
        )
        qr.print_ascii()
        print(
            f"Or manually enter this key: {self.totp.secret.decode('utf-8')}\n"
        )
