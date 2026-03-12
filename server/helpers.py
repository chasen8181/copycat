import os
import re
import shutil
import sys

from pydantic import BaseModel

from logger import logger

ROOT_APP_DIR = ".copycat"
ROOT_METADATA_FILE = "metadata.json"
ROOT_INDEX_DIR = "index"
ROOT_METADATA_LOCK = "metadata.lock"


def camel_case(snake_case_str: str) -> str:
    """Return the declared snake_case string in camelCase."""
    parts = [part for part in snake_case_str.split("_") if part != ""]
    return parts[0] + "".join(part.title() for part in parts[1:])


def is_valid_filename(value):
    """Raise ValueError if the declared string contains any of the following
    characters: <>:"/\\|?*"""
    invalid_chars = r'<>:"/\|?*'
    if any(invalid_char in value for invalid_char in invalid_chars):
        raise ValueError(
            "title cannot include any of the following characters: "
            + invalid_chars
        )
    return value


def strip_whitespace(value):
    """Return the declared string with leading and trailing whitespace
    removed."""
    return value.strip()


def get_env(
    key, mandatory=False, default=None, cast_int=False, cast_bool=False
):
    """Get an environment variable. If `mandatory` is True and environment
    variable isn't set, exit the program"""
    value = os.environ.get(key)
    if mandatory and not value:
        logger.error(f"Environment variable {key} must be set.")
        sys.exit(1)
    if not mandatory and not value:
        return default
    if cast_int:
        try:
            value = int(value)
        except (TypeError, ValueError):
            logger.error(f"Invalid value '{value}' for {key}.")
            sys.exit(1)
    if cast_bool:
        value = value.lower()
        if value == "true":
            value = True
        elif value == "false":
            value = False
        else:
            logger.error(f"Invalid value '{value}' for {key}.")
            sys.exit(1)
    return value


def replace_base_href(html_file, path_prefix):
    """Replace the href value for the base element in an HTML file."""
    base_path = path_prefix + "/"
    logger.info(
        f"Replacing href value for base element in '{html_file}' "
        + f"with '{base_path}'."
    )
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    pattern = r'(<base\s+href=")[^"]*(")'
    replacement = r"\1" + base_path + r"\2"
    updated_html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(updated_html)


def resolve_root_app_dir(base_path: str) -> str:
    preferred_path = os.path.join(base_path, ROOT_APP_DIR)
    os.makedirs(preferred_path, exist_ok=True)
    legacy_path = _find_legacy_root_metadata_dir(base_path, preferred_path)
    if legacy_path is not None:
        _migrate_root_metadata_dir(legacy_path, preferred_path)
    return preferred_path


def _find_legacy_root_metadata_dir(
    base_path: str, preferred_path: str
) -> str | None:
    candidates = []
    with os.scandir(base_path) as entries:
        for entry in entries:
            if not entry.is_dir():
                continue
            if os.path.normcase(entry.path) == os.path.normcase(preferred_path):
                continue
            if not entry.name.startswith("."):
                continue
            metadata_path = os.path.join(entry.path, ROOT_METADATA_FILE)
            if os.path.isfile(metadata_path):
                candidates.append(entry.path)
    if len(candidates) == 1:
        return candidates[0]
    if len(candidates) > 1:
        logger.warning(
            "Found multiple legacy metadata directories in '%s'. "
            + "Skipping automatic migration.",
            base_path,
        )
    return None


def _migrate_root_metadata_dir(legacy_path: str, preferred_path: str) -> None:
    index_path = os.path.join(preferred_path, ROOT_INDEX_DIR)
    os.makedirs(index_path, exist_ok=True)

    metadata_source = os.path.join(legacy_path, ROOT_METADATA_FILE)
    metadata_target = os.path.join(preferred_path, ROOT_METADATA_FILE)
    if os.path.isfile(metadata_source) and not os.path.exists(metadata_target):
        logger.info(
            "Migrating root metadata from '%s' to '%s'.",
            metadata_source,
            metadata_target,
        )
        os.replace(metadata_source, metadata_target)

    for entry_name in os.listdir(legacy_path):
        source_path = os.path.join(legacy_path, entry_name)
        if entry_name == ROOT_METADATA_LOCK:
            _remove_path(source_path)
            continue
        target_path = os.path.join(index_path, entry_name)
        if os.path.exists(target_path):
            logger.warning(
                "Skipping migrated cache item '%s' because '%s' already exists.",
                source_path,
                target_path,
            )
            continue
        logger.info(
            "Migrating cache item from '%s' to '%s'.",
            source_path,
            target_path,
        )
        os.replace(source_path, target_path)

    try:
        os.rmdir(legacy_path)
        logger.info("Removed empty legacy metadata directory '%s'.", legacy_path)
    except OSError:
        logger.warning(
            "Legacy metadata directory '%s' was not removed automatically.",
            legacy_path,
        )


def _remove_path(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


class CustomBaseModel(BaseModel):
    class Config:
        alias_generator = camel_case
        populate_by_name = True
        from_attributes = True
