"""Analisis kekuatan password."""
import re
import math
from collections import Counter


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def has_sequence(pw: str) -> bool:
    pola = [
        r'(012|123|234|345|456|567|678|789|890)',
        r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',
        r'(qwe|wer|ert|rty|tyu|yui|uio|iop|asd|sdf|dfg|fgh|ghj|hjk|jkl|zxc|xcv|cvb|vbn|bnm)',
    ]
    low = pw.lower()
    return any(re.search(p, low) for p in pola)


def has_repeat(pw: str) -> bool:
    return bool(re.search(r'(.)\1{2,}', pw))


def analyze(password: str, kamus: set) -> dict:
    issues = []
    score = 100

    if len(password) < 8:
        issues.append("Panjang kurang dari 8 karakter")
        score -= 45
    elif len(password) < 12:
        issues.append("Panjang di bawah 12 karakter")
        score -= 20

    if password.lower() in kamus:
        issues.append("Ada di daftar password umum")
        score -= 60

    if has_sequence(password):
        issues.append("Mengandung pola berurutan (123, abc, qwerty)")
        score -= 25

    if has_repeat(password):
        issues.append("Mengandung karakter berulang (aaa, 111)")
        score -= 15

    if not re.search(r'[A-Z]', password):
        score -= 5
    if not re.search(r'[0-9]', password):
        score -= 5
    if not re.search(r'[^A-Za-z0-9]', password):
        score -= 10

    entropy = shannon_entropy(password) * len(password)
    score = max(0, min(100, score))

    if score >= 80:
        label = "Sangat Kuat"
    elif score >= 60:
        label = "Kuat"
    elif score >= 40:
        label = "Sedang"
    else:
        label = "Lemah"

    return {
        "score": score,
        "label": label,
        "entropy": round(entropy, 1),
        "issues": issues,
        "length": len(password),
    }
