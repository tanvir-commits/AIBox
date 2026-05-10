from __future__ import annotations

import re
from pathlib import Path


def safe_filename(name: str) -> str:
    base = Path(name or "upload").name
    base = re.sub(r"[^\w.\-]+", "_", base, flags=re.UNICODE).strip("._")
    return (base or "upload")[:255]
