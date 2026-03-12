from collections import deque
from threading import Lock
from typing import Deque


class LoginRateLimiter:
    def __init__(
        self,
        *,
        enabled: bool,
        window_seconds: int,
        ip_max_attempts: int,
        user_ip_max_attempts: int,
    ) -> None:
        self.enabled = enabled
        self.window_seconds = max(int(window_seconds), 1)
        self.ip_max_attempts = max(int(ip_max_attempts), 1)
        self.user_ip_max_attempts = max(int(user_ip_max_attempts), 1)
        self._lock = Lock()
        self._ip_failures: dict[str, Deque[float]] = {}
        self._user_ip_failures: dict[str, Deque[float]] = {}

    def check(self, ip_address: str, username: str) -> tuple[bool, int | None]:
        if not self.enabled:
            return (True, None)
        with self._lock:
            now = self._now()
            ip_key = self._normalize_ip(ip_address)
            user_key = self._user_ip_key(ip_key, username)
            ip_events = self._pruned_events(self._ip_failures.get(ip_key), now)
            user_events = self._pruned_events(
                self._user_ip_failures.get(user_key), now
            )
            retry_after = self._retry_after(
                now,
                ip_events,
                user_events,
            )
            if len(ip_events) >= self.ip_max_attempts or len(user_events) >= self.user_ip_max_attempts:
                return (False, retry_after)
            return (True, None)

    def register_failure(self, ip_address: str, username: str) -> None:
        if not self.enabled:
            return
        with self._lock:
            now = self._now()
            ip_key = self._normalize_ip(ip_address)
            user_key = self._user_ip_key(ip_key, username)
            self._ip_failures[ip_key] = self._pruned_events(
                self._ip_failures.get(ip_key), now
            )
            self._user_ip_failures[user_key] = self._pruned_events(
                self._user_ip_failures.get(user_key), now
            )
            self._ip_failures[ip_key].append(now)
            self._user_ip_failures[user_key].append(now)

    def _retry_after(
        self,
        now: float,
        ip_events: Deque[float],
        user_events: Deque[float],
    ) -> int:
        retry_candidates = []
        if len(ip_events) >= self.ip_max_attempts:
            retry_candidates.append(ip_events[0] + self.window_seconds - now)
        if len(user_events) >= self.user_ip_max_attempts:
            retry_candidates.append(user_events[0] + self.window_seconds - now)
        if not retry_candidates:
            return 1
        return max(int(max(retry_candidates)) + 1, 1)

    def _pruned_events(
        self, events: Deque[float] | None, now: float
    ) -> Deque[float]:
        pruned = deque(events or [])
        cutoff = now - self.window_seconds
        while pruned and pruned[0] <= cutoff:
            pruned.popleft()
        return pruned

    @staticmethod
    def _normalize_ip(ip_address: str) -> str:
        normalized = (ip_address or "").strip()
        return normalized or "unknown"

    @staticmethod
    def _normalize_username(username: str) -> str:
        return (username or "").strip().lower()

    def _user_ip_key(self, ip_address: str, username: str) -> str:
        return f"{ip_address}:{self._normalize_username(username)}"

    @staticmethod
    def _now() -> float:
        import time

        return time.time()


def build_content_security_policy() -> str:
    return "; ".join(
        (
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: blob:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "frame-ancestors 'none'",
            "form-action 'self'",
        )
    )


def get_client_ip(request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        first_hop = forwarded_for.split(",")[0].strip()
        if first_hop:
            return first_hop
    forwarded_proto = request.headers.get("x-real-ip", "").strip()
    if forwarded_proto:
        return forwarded_proto
    if request.client is not None and request.client.host:
        return request.client.host
    return "unknown"


def request_uses_https(request) -> bool:
    forwarded_proto = request.headers.get("x-forwarded-proto", "").lower()
    if forwarded_proto:
        return forwarded_proto.split(",")[0].strip() == "https"
    return request.url.scheme == "https"


def apply_security_headers(
    response,
    *,
    csp_mode: str,
    cache_private: bool = False,
) -> None:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault(
        "Referrer-Policy", "strict-origin-when-cross-origin"
    )
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
    )
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
    if csp_mode != "off":
        header_name = (
            "Content-Security-Policy"
            if csp_mode == "enforce"
            else "Content-Security-Policy-Report-Only"
        )
        response.headers.setdefault(header_name, build_content_security_policy())
    if cache_private:
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"


def is_private_path(path: str, path_prefix: str) -> bool:
    prefix = path_prefix.rstrip("/")
    path = path or ""
    private_roots = [
        f"{prefix}/api/",
        f"{prefix}/attachments/",
    ]
    return any(path.startswith(root) for root in private_roots)
