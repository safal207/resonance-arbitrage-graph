from __future__ import annotations

import json
from typing import Any
from urllib.request import Request, urlopen


def get_json(url: str, *, timeout: float = 5.0) -> dict[str, Any]:
    request = Request(
        url,
        method="GET",
        headers={"Accept": "application/json", "User-Agent": "resonance-arbitrage-graph/0.2"},
    )
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed public HTTPS URLs
        return json.loads(response.read().decode("utf-8"))
