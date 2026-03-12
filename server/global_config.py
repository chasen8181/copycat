import sys
from enum import Enum

from pydantic import Field

from helpers import CustomBaseModel, get_env
from logger import logger


class GlobalConfig:
    def __init__(self) -> None:
        logger.debug("Loading global config...")
        self.auth_type: AuthType = self._load_auth_type()
        self.quick_access_hide: bool = self._quick_access_hide()
        self.quick_access_title: str = self._quick_access_title()
        self.quick_access_term: str = self._quick_access_term()
        self.quick_access_sort: str = self._quick_access_sort()
        self.quick_access_limit: int = self._quick_access_limit()
        self.path_prefix: str = self._load_path_prefix()
        self.login_rate_limit_enabled: bool = self._load_login_rate_limit_enabled()
        self.login_rate_limit_window_seconds: int = (
            self._load_login_rate_limit_window_seconds()
        )
        self.login_rate_limit_ip_max: int = self._load_login_rate_limit_ip_max()
        self.login_rate_limit_user_ip_max: int = (
            self._load_login_rate_limit_user_ip_max()
        )
        self.csp_mode: str = self._load_csp_mode()
        self.max_attachment_bytes: int = self._load_max_attachment_bytes()
        self.attachment_block_active_content: bool = (
            self._load_attachment_block_active_content()
        )
        self.attachment_blocked_extensions: tuple[str, ...] = (
            self._load_attachment_blocked_extensions()
        )
        self.set_httponly_auth_cookie: bool = (
            self._load_set_httponly_auth_cookie()
        )

    def load_auth(self):
        if self.auth_type in (AuthType.NONE, AuthType.READ_ONLY):
            return None
        elif self.auth_type in (AuthType.PASSWORD, AuthType.TOTP):
            from auth.local import LocalAuth

            return LocalAuth()

    def load_metadata_storage(self):
        from metadata.file_system import FileSystemMetadata

        return FileSystemMetadata()

    def load_note_storage(self, metadata_storage=None):
        from notes.file_system import FileSystemNotes

        return FileSystemNotes(metadata_storage=metadata_storage)

    def load_attachment_storage(self):
        from attachments.file_system import FileSystemAttachments

        return FileSystemAttachments()

    def _load_auth_type(self):
        key = "COPYCAT_AUTH_TYPE"
        auth_type = get_env(
            key, mandatory=False, default=AuthType.PASSWORD.value
        )
        try:
            auth_type = AuthType(auth_type.lower())
        except ValueError:
            logger.error(
                f"Invalid value '{auth_type}' for {key}. "
                + "Must be one of: "
                + ", ".join([auth_type.value for auth_type in AuthType])
                + "."
            )
            sys.exit(1)
        return auth_type

    def _quick_access_hide(self):
        key = "COPYCAT_QUICK_ACCESS_HIDE"
        value = get_env(key, mandatory=False, default=False, cast_bool=True)
        if value is False:
            depricated_key = "COPYCAT_HIDE_RECENTLY_MODIFIED"
            value = get_env(
                depricated_key, mandatory=False, default=False, cast_bool=True
            )
            if value is True:
                logger.warning(
                    f"{depricated_key} is depricated. Please use {key} instead."
                )
        return value

    def _quick_access_title(self):
        key = "COPYCAT_QUICK_ACCESS_TITLE"
        return get_env(key, mandatory=False, default="RECENTLY MODIFIED")

    def _quick_access_term(self):
        key = "COPYCAT_QUICK_ACCESS_TERM"
        return get_env(key, mandatory=False, default="*")

    def _quick_access_sort(self):
        key = "COPYCAT_QUICK_ACCESS_SORT"
        value = get_env(key, mandatory=False, default="lastModified")
        valid_values = ["score", "title", "lastModified"]
        if value not in valid_values:
            logger.error(
                f"Invalid value '{value}' for {key}. "
                + "Must be one of: "
                + ", ".join(valid_values)
            )
            sys.exit(1)
        return value

    def _quick_access_limit(self):
        key = "COPYCAT_QUICK_ACCESS_LIMIT"
        return get_env(key, mandatory=False, default=4, cast_int=True)

    def _load_path_prefix(self):
        key = "COPYCAT_PATH_PREFIX"
        value = get_env(key, mandatory=False, default="")
        if value and (not value.startswith("/") or value.endswith("/")):
            logger.error(
                f"Invalid value '{value}' for {key}. "
                + "Must start with '/' and not end with '/'."
            )
            sys.exit(1)
        return value

    def _load_login_rate_limit_enabled(self):
        return get_env(
            "COPYCAT_LOGIN_RATE_LIMIT_ENABLED",
            mandatory=False,
            default=True,
            cast_bool=True,
        )

    def _load_login_rate_limit_window_seconds(self):
        return get_env(
            "COPYCAT_LOGIN_RATE_LIMIT_WINDOW_SECONDS",
            mandatory=False,
            default=60,
            cast_int=True,
        )

    def _load_login_rate_limit_ip_max(self):
        return get_env(
            "COPYCAT_LOGIN_RATE_LIMIT_IP_MAX",
            mandatory=False,
            default=10,
            cast_int=True,
        )

    def _load_login_rate_limit_user_ip_max(self):
        return get_env(
            "COPYCAT_LOGIN_RATE_LIMIT_USER_IP_MAX",
            mandatory=False,
            default=5,
            cast_int=True,
        )

    def _load_csp_mode(self):
        key = "COPYCAT_CSP_MODE"
        value = get_env(key, mandatory=False, default="report-only").lower()
        valid_values = {"off", "report-only", "enforce"}
        if value not in valid_values:
            logger.error(
                f"Invalid value '{value}' for {key}. Must be one of: "
                + ", ".join(sorted(valid_values))
            )
            sys.exit(1)
        return value

    def _load_max_attachment_bytes(self):
        key = "COPYCAT_MAX_ATTACHMENT_BYTES"
        value = get_env(
            key, mandatory=False, default=26214400, cast_int=True
        )
        if value <= 0:
            logger.error(f"Invalid value '{value}' for {key}. Must be > 0.")
            sys.exit(1)
        return value

    def _load_attachment_block_active_content(self):
        return get_env(
            "COPYCAT_ATTACHMENT_BLOCK_ACTIVE_CONTENT",
            mandatory=False,
            default=False,
            cast_bool=True,
        )

    def _load_attachment_blocked_extensions(self):
        raw_value = get_env(
            "COPYCAT_ATTACHMENT_BLOCKED_EXTENSIONS",
            mandatory=False,
            default=".html,.htm,.js,.mjs,.svg,.svgz,.xml,.xhtml",
        )
        extensions = []
        for value in raw_value.split(","):
            normalized = value.strip().lower()
            if not normalized:
                continue
            if not normalized.startswith("."):
                normalized = "." + normalized
            extensions.append(normalized)
        return tuple(dict.fromkeys(extensions))

    def _load_set_httponly_auth_cookie(self):
        return get_env(
            "COPYCAT_SET_HTTPONLY_AUTH_COOKIE",
            mandatory=False,
            default=False,
            cast_bool=True,
        )


class AuthType(str, Enum):
    NONE = "none"
    READ_ONLY = "read_only"
    PASSWORD = "password"
    TOTP = "totp"


class GlobalConfigResponseModel(CustomBaseModel):
    auth_type: AuthType
    quick_access_hide: bool
    quick_access_title: str
    quick_access_term: str
    quick_access_sort: str
    quick_access_limit: int
    role: str = "admin"
    available_groups: list[dict[str, str]] = Field(default_factory=list)
    default_group_id: str | None = None
    show_legacy_library: bool = False
    http_only_auth_cookie: bool = False
