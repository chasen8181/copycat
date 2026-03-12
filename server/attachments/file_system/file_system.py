import os
import urllib.parse
from datetime import datetime

from fastapi import UploadFile
from fastapi.responses import FileResponse

from helpers import get_env, is_valid_filename

from ..base import BaseAttachments
from ..models import AttachmentCreateResponse


class AttachmentTooLargeError(ValueError):
    pass


class AttachmentTypeBlockedError(ValueError):
    pass


class FileSystemAttachments(BaseAttachments):
    def __init__(
        self,
        storage_path: str | None = None,
        url_prefix: str = "attachments",
        query_params: dict[str, str] | None = None,
    ):
        self.base_path = (
            get_env("COPYCAT_PATH", mandatory=True)
            if storage_path is None
            else os.path.dirname(storage_path)
        )
        if storage_path is None and not os.path.exists(self.base_path):
            raise NotADirectoryError(
                f"'{self.base_path}' is not a valid directory."
        )
        self.storage_path = storage_path or os.path.join(
            self.base_path, "attachments"
        )
        self.url_prefix = url_prefix.strip("/") or "attachments"
        self.query_params = query_params or {}
        self.max_attachment_bytes = get_env(
            "COPYCAT_MAX_ATTACHMENT_BYTES",
            mandatory=False,
            default=26214400,
            cast_int=True,
        )
        self.block_active_content = get_env(
            "COPYCAT_ATTACHMENT_BLOCK_ACTIVE_CONTENT",
            mandatory=False,
            default=False,
            cast_bool=True,
        )
        self.blocked_extensions = tuple(
            normalized_extension
            for normalized_extension in (
                (
                    extension.strip().lower()
                    if extension.strip().startswith(".")
                    else f".{extension.strip().lower()}"
                )
                for extension in get_env(
                    "COPYCAT_ATTACHMENT_BLOCKED_EXTENSIONS",
                    mandatory=False,
                    default=".html,.htm,.js,.mjs,.svg,.svgz,.xml,.xhtml",
                ).split(",")
            )
            if normalized_extension != "."
        )
        os.makedirs(self.storage_path, exist_ok=True)

    def create(self, file: UploadFile) -> AttachmentCreateResponse:
        """Create a new attachment."""
        file.filename = self._validate_upload_filename(file.filename)
        try:
            self._save_file(file)
        except FileExistsError:
            file.filename = self._datetime_suffix_filename(file.filename)
            self._save_file(file)
        return AttachmentCreateResponse(
            filename=file.filename, url=self._url_for_filename(file.filename)
        )

    def get(self, filename: str) -> FileResponse:
        """Get a specific attachment."""
        filename = self._validate_upload_filename(filename)
        filepath = os.path.join(self.storage_path, filename)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"'{filename}' not found.")
        return FileResponse(
            filepath,
            headers={"X-Content-Type-Options": "nosniff"},
        )

    def _save_file(self, file: UploadFile):
        filepath = os.path.join(self.storage_path, file.filename)
        try:
            with open(filepath, "xb") as f:
                bytes_written = 0
                while True:
                    chunk = file.file.read(1024 * 1024)
                    if not chunk:
                        break
                    bytes_written += len(chunk)
                    if bytes_written > self.max_attachment_bytes:
                        raise AttachmentTooLargeError
                    f.write(chunk)
        except Exception:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise

    def _datetime_suffix_filename(self, filename: str) -> str:
        """Add a timestamp suffix to the filename."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
        name, ext = os.path.splitext(filename)
        return f"{name}_{timestamp}{ext}"

    def _validate_upload_filename(self, filename: str) -> str:
        if not filename:
            raise ValueError("Filename cannot be empty.")
        normalized_name = os.path.basename(filename.strip())
        is_valid_filename(normalized_name)
        if normalized_name in {".", ".."}:
            raise ValueError("Filename cannot be empty.")
        if normalized_name.startswith(".") or normalized_name.endswith("."):
            raise ValueError("Filename cannot start or end with a period.")
        if normalized_name.strip() != normalized_name:
            raise ValueError("Filename cannot start or end with whitespace.")
        if self.block_active_content:
            _, extension = os.path.splitext(normalized_name.lower())
            if extension in self.blocked_extensions:
                raise AttachmentTypeBlockedError
        return normalized_name

    def _url_for_filename(self, filename: str) -> str:
        """Return the URL for the given filename."""
        url = f"{self.url_prefix}/{urllib.parse.quote(filename)}"
        if self.query_params:
            url += "?" + urllib.parse.urlencode(self.query_params)
        return url
