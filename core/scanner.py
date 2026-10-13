"""Pindai WiFi lewat Shizuku/rish, tahan rate limit Android."""
import subprocess
import time
import re
from pathlib import Path
from .parser import parse_scan, klasifikasi_keamanan

RISH = Path.home() / "rish" / "rish"

# Cache hasil scan terakhir (untuk fallback kalau rate-limited)
_cache = {"waktu": 0, "hasil": []}


def _rish(cmd: str, timeout: int = 40) -> str:
    result = subprocess.run(
        [str(RISH), "-c", cmd],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout


def scan_wifi(paksa: bool = False) -> list:
    """
    Pindai WiFi. Kalau hasil kosong (rate-limited), pakai cache
    dari scan terakhir yang masih segar (< 5 menit).
    """
    sekarang = time.time()

    # Kalau baru scan < 30 detik lalu dan tidak dipaksa, pakai cache
    if not paksa and (sekarang - _cache["waktu"]) < 30 and _cache["hasil"]:
        return _cache["hasil"]

    gabungan = "cmd wifi start-scan; sleep 3; cmd wifi list-scan-results"
    raw = _rish(gabungan)

    # Deteksi rate limit
    if "Failed to start scan" in raw or "Scan failed" in raw or len(raw) < 50:
        # Kalau ada cache < 5 menit, pakai itu
        if (sekarang - _cache["waktu"]) < 300 and _cache["hasil"]:
            return _cache["hasil"]
        return []

    networks = parse_scan(raw)
    for n in networks:
        n["security"] = klasifikasi_keamanan(n.get("flags", ""))
    networks.sort(key=lambda x: x["rssi"], reverse=True)

    if networks:
        _cache["waktu"] = sekarang
        _cache["hasil"] = networks

    return networks


def status_wifi() -> dict:
    raw = _rish("cmd wifi status")
    info = {}
    for line in raw.splitlines():
        if line.startswith("Wifi is connected to"):
            info["connected_ssid"] = line.split('"')[1] if '"' in line else None
        if "WifiInfo: SSID:" in line:
            m = re.search(r'SSID:\s*"([^"]*)"', line)
            if m:
                info["ssid"] = m.group(1)
            m = re.search(r'BSSID:\s*([0-9a-f:]+)', line, re.IGNORECASE)
            if m:
                info["bssid"] = m.group(1)
            m = re.search(r'IP:\s*/([\d.]+)', line)
            if m:
                info["ip"] = m.group(1)
            m = re.search(r'RSSI:\s*(-?\d+)', line)
            if m:
                info["rssi"] = int(m.group(1))
    return info
