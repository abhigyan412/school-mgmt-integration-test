import requests
from config import settings
import re

_cookies_dict: dict = {}
_csrf_token: str = ""
_logged_in: bool = False


def _parse_set_cookie_headers(resp) -> dict:
    cookies = {}
    raw_list = []
    
    # Try to get individual Set-Cookie headers
    if hasattr(resp.raw, 'headers') and hasattr(resp.raw.headers, 'getlist'):
        raw_list = resp.raw.headers.getlist("Set-Cookie")
    
    if raw_list:
        for cookie_str in raw_list:
            first = cookie_str.strip().split(";")[0].strip()
            if "=" in first:
                name, value = first.split("=", 1)
                name, value = name.strip(), value.strip()
                if name in ("accessToken", "refreshToken", "csrfToken") and value:
                    cookies[name] = value
    else:
        # Fallback: regex on combined header
        raw_combined = resp.headers.get("set-cookie", "")
        matches = re.finditer(
            r'(accessToken|refreshToken|csrfToken)=([^;,\s]+)',
            raw_combined
        )
        for m in matches:
            name, value = m.group(1), m.group(2)
            if value and not value.startswith("Thu"):
                cookies[name] = value

    return cookies


def _login() -> None:
    global _csrf_token, _logged_in, _cookies_dict

    resp = requests.post(
        f"{settings.backend_url}/api/v1/auth/login",
        json={
            "username": settings.backend_email,
            "password": settings.backend_password,
        },
        timeout=15,
        verify=False,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Login failed: {resp.status_code} - {resp.text}")

    _cookies_dict = _parse_set_cookie_headers(resp)
    _csrf_token = _cookies_dict.get("csrfToken", "")

    print("COOKIES:", {k: v[:30] for k, v in _cookies_dict.items()})
    print("CSRF:", _csrf_token)

    _logged_in = True


def fetch_student_sync(student_id: int) -> dict:
    global _logged_in

    if not _logged_in:
        _login()

    for attempt in range(2):
        # Pass cookies as plain dict — bypasses domain matching
        resp = requests.get(
            f"{settings.backend_url}/api/v1/students/{student_id}",
            cookies=_cookies_dict,
            headers={"x-csrf-token": _csrf_token},
            timeout=15,
            verify=False,
        )

        print(f"STATUS: {resp.status_code} | RESPONSE: {resp.text[:100]}")

        if resp.status_code in (401, 403) and attempt == 0:
            _logged_in = False
            _login()
            continue

        if resp.status_code == 400 and "csrf" in resp.text.lower() and attempt == 0:
            _logged_in = False
            _login()
            continue

        if resp.status_code == 404:
            raise ValueError(f"Student {student_id} not found")

        if resp.status_code != 200:
            raise RuntimeError(f"Backend error {resp.status_code}: {resp.text}")

        payload = resp.json()
        return payload.get("data", payload)

    raise RuntimeError("Failed to fetch student after re-authentication")