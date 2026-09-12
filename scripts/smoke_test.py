from __future__ import annotations

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch(base_url: str, path: str) -> tuple[int, str]:
    url = base_url.rstrip("/") + path
    request = Request(url, headers={"User-Agent": "joylab-release-gate/0.6.5"})
    with urlopen(request, timeout=20) as response:
        return response.status, response.read().decode("utf-8")


def require_json(base_url: str, path: str) -> dict:
    status, body = fetch(base_url, path)
    if status != 200:
        raise RuntimeError(f"{path}: expected HTTP 200, got {status}")
    return json.loads(body)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/smoke_test.py <base-url>", file=sys.stderr)
        return 2

    base_url = sys.argv[1].strip()
    if not base_url:
        print("base URL is empty", file=sys.stderr)
        return 2

    try:
        status, dashboard = fetch(base_url, "/")
        if status != 200 or "JoyLab Agent OS" not in dashboard:
            raise RuntimeError("dashboard root failed")

        health = require_json(base_url, "/api/health")
        if health.get("status") != "healthy":
            raise RuntimeError("health endpoint is not healthy")

        version_payload = require_json(base_url, "/api/version")
        if version_payload.get("version") != "0.6.5":
            raise RuntimeError(
                f"unexpected deployed version: {version_payload.get('version')}"
            )

        capabilities = require_json(base_url, "/api/capabilities")
        required = {"evidence-builder", "certification-gate", "crash-reconciliation"}
        actual = set(capabilities.get("capabilities", []))
        missing = sorted(required - actual)
        if missing:
            raise RuntimeError(f"missing capabilities: {missing}")

        print(f"RELEASE_GATE_GREEN {base_url}")
        return 0
    except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as exc:
        print(f"RELEASE_GATE_RED {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
