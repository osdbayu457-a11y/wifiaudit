"""Parser output 'cmd wifi list-scan-results' Android 14 (versi tangguh)."""
import re

BSSID_RE = re.compile(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}')
ANGKA_RE = re.compile(r'(-?\d[\d,]*)')


def _baris_bssid(line: str):
    line = line.strip()
    if not BSSID_RE.match(line):
        return None
    bssid = line[:17]
    sisa = line[17:]
    angka = ANGKA_RE.findall(sisa)
    if len(angka) < 2:
        return None
    try:
        freq = int(angka[0].replace(',', ''))
        rssi = int(angka[1].replace(',', ''))
    except ValueError:
        return None
    return bssid, freq, rssi


def parse_scan(raw: str) -> list:
    lines = raw.splitlines()
    hasil = []
    i = 0
    while i < len(lines):
        info = _baris_bssid(lines[i])
        if info is None:
            i += 1
            continue
        bssid, freq, rssi = info
        ssid = ""
        flags = ""
        j = i + 1
        if j < len(lines):
            baris_ssid = lines[j].rstrip()
            idx = baris_ssid.find('[')
            if idx == -1:
                ssid = baris_ssid.strip()
            else:
                ssid = baris_ssid[:idx].strip()
                flags = baris_ssid[idx:].strip()
            j += 1
        while j < len(lines):
            lanjut = lines[j].rstrip()
            if not lanjut:
                j += 1
                continue
            if _baris_bssid(lanjut) is not None:
                break
            if '[' in lanjut:
                flags += lanjut.strip()
                j += 1
            else:
                break
        hasil.append({
            "ssid": ssid, "bssid": bssid,
            "freq": freq, "rssi": rssi, "flags": flags,
        })
        i = j
    return hasil


def klasifikasi_keamanan(flags: str) -> str:
    f = (flags or "").upper()
    if 'SAE' in f or 'WPA3' in f:
        return "WPA3"
    if 'RSN-PSK' in f or 'WPA2' in f:
        return "WPA2"
    if 'WPA-PSK' in f:
        return "WPA"
    if 'WEP' in f:
        return "WEP"
    if 'ESS' in f and 'WPA' not in f and 'RSN' not in f:
        return "Terbuka"
    return "Tidak diketahui"
