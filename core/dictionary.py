"""Loader kamus password."""
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_common() -> set:
    f = DATA_DIR / "common_passwords.txt"
    if not f.exists():
        return set()
    return {ln.strip().lower() for ln in f.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()}


def load_router_defaults() -> dict:
    f = DATA_DIR / "default_router.txt"
    if not f.exists():
        return {}
    result = {}
    for ln in f.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "|" not in ln:
            continue
        merek, pw = ln.split("|", 1)
        result[merek.strip().lower()] = [p.strip() for p in pw.split(",") if p.strip()]
    return result


def guess_brand(ssid: str):
    s = (ssid or "").lower()
    peta = {
        "indihome": "indihome",
        "first media": "firstmedia",
        "biznet": "biznet",
        "myrepublic": "myrepublic",
        "tp-link": "tplink",
        "tplink": "tplink",
        "zte": "zte",
        "huawei": "huawei",
        "mikrotik": "mikrotik",
        "asus": "asus",
        "xiaomi": "xiaomi",
    }
    for kata, merek in peta.items():
        if kata in s:
            return merek
    return None
