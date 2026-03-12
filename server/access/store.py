import json
import os
import tempfile
import threading
import time

from file_lock import FileLock
from helpers import get_env

from .models import (
    GroupCreate,
    GroupRecord,
    GroupUpdate,
    GroupsState,
    UserCreate,
    UserRecord,
    UsersState,
    UserUpdate,
    slugify_group_id,
)


class AccessRegistryStore:
    VERSION = 1

    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = base_path or get_env("COPYCAT_PATH", mandatory=True)
        if not os.path.isdir(self.base_path):
            raise NotADirectoryError(
                f"'{self.base_path}' is not a valid directory."
            )
        self.auth_dir = os.path.join(self.base_path, ".copycat", "auth")
        self.users_path = os.path.join(self.auth_dir, "users.json")
        self.groups_path = os.path.join(self.auth_dir, "groups.json")
        self.lock_path = os.path.join(self.auth_dir, "registry.lock")
        self._lock = threading.Lock()

    def list_groups(self) -> list[GroupRecord]:
        state = self._load_groups()
        return sorted(state.groups.values(), key=lambda item: item.name.lower())

    def get_group(self, group_id: str) -> GroupRecord | None:
        state = self._load_groups()
        return state.groups.get(group_id.lower())

    def create_group(self, data: GroupCreate) -> GroupRecord:
        with self._lock, self._file_lock():
            state = self._load_groups()
            self._ensure_unique_group_name(state, data.name)
            group_id = self._generate_unique_group_id(state, data.name)
            record = GroupRecord(
                id=group_id,
                slug=group_id,
                name=data.name,
                created_at=time.time(),
                is_active=True,
            )
            state.groups[group_id] = record
            self._write_groups(state)
            return record

    def update_group(self, group_id: str, data: GroupUpdate) -> GroupRecord:
        normalized_group_id = group_id.lower()
        with self._lock, self._file_lock():
            state = self._load_groups()
            record = state.groups.get(normalized_group_id)
            if record is None:
                raise FileNotFoundError(f"Group '{group_id}' not found.")
            if record.name.lower() != data.name.lower():
                self._ensure_unique_group_name(
                    state, data.name, excluding_id=normalized_group_id
                )
            updated = GroupRecord(
                id=record.id,
                slug=record.slug,
                name=data.name,
                created_at=record.created_at,
                is_active=record.is_active,
            )
            state.groups[normalized_group_id] = updated
            self._write_groups(state)
            return updated

    def delete_group(self, group_id: str) -> None:
        normalized_group_id = group_id.lower()
        with self._lock, self._file_lock():
            groups_state = self._load_groups()
            if normalized_group_id not in groups_state.groups:
                raise FileNotFoundError(f"Group '{group_id}' not found.")
            groups_state.groups.pop(normalized_group_id)
            users_state = self._load_users()
            for username, user in list(users_state.users.items()):
                users_state.users[username] = UserRecord(
                    id=user.id,
                    username=user.username,
                    password_hash=user.password_hash,
                    display_name=user.display_name,
                    group_ids=[
                        current_group_id
                        for current_group_id in user.group_ids
                        if current_group_id != normalized_group_id
                    ],
                    is_active=user.is_active,
                    created_at=user.created_at,
                )
            self._write_groups(groups_state)
            self._write_users(users_state)

    def list_users(self) -> list[UserRecord]:
        state = self._load_users()
        return sorted(
            state.users.values(), key=lambda item: item.username.lower()
        )

    def get_user(self, username: str) -> UserRecord | None:
        state = self._load_users()
        return state.users.get(username.lower())

    def create_user(
        self, data: UserCreate, password_hash: str, *, group_ids: list[str]
    ) -> UserRecord:
        normalized_username = data.username.lower()
        with self._lock, self._file_lock():
            state = self._load_users()
            if normalized_username in state.users:
                raise FileExistsError(
                    f"A user named '{data.username}' already exists."
                )
            record = UserRecord(
                id=normalized_username,
                username=data.username,
                password_hash=password_hash,
                display_name=data.display_name,
                group_ids=list(dict.fromkeys(group_ids)),
                is_active=data.is_active,
                created_at=time.time(),
            )
            state.users[normalized_username] = record
            self._write_users(state)
            return record

    def update_user(
        self,
        username: str,
        data: UserUpdate,
        *,
        password_hash: str | None = None,
        group_ids: list[str] | None = None,
    ) -> UserRecord:
        normalized_username = username.lower()
        with self._lock, self._file_lock():
            state = self._load_users()
            record = state.users.get(normalized_username)
            if record is None:
                raise FileNotFoundError(f"User '{username}' not found.")
            updated = UserRecord(
                id=record.id,
                username=record.username,
                password_hash=password_hash or record.password_hash,
                display_name=(
                    record.display_name
                    if data.display_name is None
                    else data.display_name
                ),
                group_ids=(
                    record.group_ids
                    if group_ids is None
                    else list(dict.fromkeys(group_ids))
                ),
                is_active=(
                    record.is_active if data.is_active is None else data.is_active
                ),
                created_at=record.created_at,
            )
            state.users[normalized_username] = updated
            self._write_users(state)
            return updated

    def delete_user(self, username: str) -> None:
        normalized_username = username.lower()
        with self._lock, self._file_lock():
            state = self._load_users()
            if state.users.pop(normalized_username, None) is None:
                raise FileNotFoundError(f"User '{username}' not found.")
            self._write_users(state)

    def _load_groups(self) -> GroupsState:
        if not os.path.isfile(self.groups_path):
            return GroupsState(version=self.VERSION)
        with open(self.groups_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return GroupsState.model_validate(data)

    def _load_users(self) -> UsersState:
        if not os.path.isfile(self.users_path):
            return UsersState(version=self.VERSION)
        with open(self.users_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return UsersState.model_validate(data)

    def _ensure_auth_dir(self) -> None:
        os.makedirs(self.auth_dir, exist_ok=True)

    def _file_lock(self) -> FileLock:
        self._ensure_auth_dir()
        return FileLock(self.lock_path)

    def _write_groups(self, state: GroupsState) -> None:
        self._ensure_auth_dir()
        state.version = self.VERSION
        self._atomic_write(self.groups_path, state.model_dump(by_alias=True))

    def _write_users(self, state: UsersState) -> None:
        self._ensure_auth_dir()
        state.version = self.VERSION
        self._atomic_write(self.users_path, state.model_dump(by_alias=True))

    @staticmethod
    def _atomic_write(path: str, data: dict) -> None:
        directory = os.path.dirname(path)
        fd, tmp_path = tempfile.mkstemp(
            dir=directory, prefix="copycat-", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    @staticmethod
    def _ensure_unique_group_name(
        state: GroupsState, name: str, excluding_id: str | None = None
    ) -> None:
        normalized_name = name.lower()
        for group in state.groups.values():
            if group.id == excluding_id:
                continue
            if group.name.lower() == normalized_name:
                raise FileExistsError(
                    f"A group named '{name}' already exists."
                )

    @staticmethod
    def _generate_unique_group_id(state: GroupsState, name: str) -> str:
        candidate = slugify_group_id(name)
        if candidate not in state.groups:
            return candidate
        suffix = 2
        while f"{candidate}-{suffix}" in state.groups:
            suffix += 1
        return f"{candidate}-{suffix}"
