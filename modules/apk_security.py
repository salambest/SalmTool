"""
APK Security Scanner module.

Performs static analysis on an APK file to surface common risk indicators:
dangerous permissions, embedded URLs / IP addresses, base64-looking blobs,
native (.so) libraries, and a rough obfuscation heuristic. This module
never executes or unpacks the APK's code — it only reads bytes from the
zip entries for pattern matching, so it is safe to run against untrusted
files.

This is a personal-use static triage tool (in the spirit of open-source
projects like MobSF), not an antivirus engine — its output is informational
and should be read as "worth a closer look", not a definitive verdict.
"""

import re
import zipfile
from math import log2

from modules.apk_analyzer import analyze_apk, _extract_strings

DANGEROUS_PERMISSIONS = {
    "android.permission.READ_SMS", "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS", "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS", "android.permission.READ_CALL_LOG",
    "android.permission.CALL_PHONE", "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA", "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.READ_PHONE_STATE", "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.WRITE_SECURE_SETTINGS", "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.REQUEST_INSTALL_PACKAGES", "android.permission.PACKAGE_USAGE_STATS",
}

URL_RE = re.compile(r"https?://[^\s\"'<>]{4,}")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
BASE64_RE = re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b")

LEVEL_EMOJI = {"SAFE": "🟢", "LOW": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}


def _shannon_entropy(s):
    if not s:
        return 0.0
    freq = {c: s.count(c) for c in set(s)}
    length = len(s)
    return -sum((n / length) * log2(n / length) for n in freq.values())


def _scan_zip_strings(apk_path, max_entries=400):
    urls, ips, b64_blobs = set(), set(), set()
    high_entropy_hits = 0

    with zipfile.ZipFile(apk_path) as z:
        names = z.namelist()
        native_libs = [n for n in names if n.startswith("lib/") and n.endswith(".so")]

        scan_targets = [n for n in names if n.endswith((".xml", ".dex", ".json", ".txt", ".properties"))]
        for name in scan_targets[:max_entries]:
            try:
                data = z.read(name)
            except Exception:
                continue

            strings = _extract_strings(data, min_len=8)
            for s in strings:
                urls.update(URL_RE.findall(s))
                ips.update(IP_RE.findall(s))
                for m in BASE64_RE.findall(s):
                    if _shannon_entropy(m) > 4.3:
                        b64_blobs.add(m[:60] + ("..." if len(m) > 60 else ""))

            joined = " ".join(strings)
            if joined and _shannon_entropy(joined) > 4.6:
                high_entropy_hits += 1

    return {
        "urls": sorted(urls)[:100],
        "ips": sorted(ips)[:100],
        "base64_like_blobs": sorted(b64_blobs)[:50],
        "native_libraries": native_libs,
        "high_entropy_file_hits": high_entropy_hits,
    }


def _obfuscation_score(apk_info):
    """Rough heuristic: a high proportion of very short (1-2 letter) class
    names hints at a ProGuard/R8-style renamed codebase. Informational
    only — legitimate apps can also be minified this way."""
    components = apk_info.get("activities", [])
    if not components:
        return 0.0
    short_names = [c for c in components if re.search(r"\.[a-zA-Z]{1,2}$", c)]
    return round(len(short_names) / max(len(components), 1) * 100, 1)


def compute_risk_level(findings, apk_info):
    score = 0
    dangerous_found = [p for p in apk_info.get("permissions", []) if p in DANGEROUS_PERMISSIONS]

    score += len(dangerous_found) * 8
    score += min(len(findings["urls"]), 10) * 2
    score += min(len(findings["ips"]), 10) * 3
    score += min(len(findings["base64_like_blobs"]), 10) * 4
    score += min(findings["high_entropy_file_hits"], 10) * 3

    permissions = apk_info.get("permissions", [])
    if "android.permission.BIND_ACCESSIBILITY_SERVICE" in permissions:
        score += 15
    if "android.permission.REQUEST_INSTALL_PACKAGES" in permissions:
        score += 10

    if score >= 60:
        level = "CRITICAL"
    elif score >= 35:
        level = "HIGH"
    elif score >= 15:
        level = "LOW"
    else:
        level = "SAFE"

    return level, score, dangerous_found


def scan_apk(apk_path):
    apk_info = analyze_apk(apk_path)
    findings = _scan_zip_strings(apk_path)
    level, score, dangerous_perms = compute_risk_level(findings, apk_info)
    obf_score = _obfuscation_score(apk_info)

    return {
        "apk_info": apk_info,
        "findings": findings,
        "dangerous_permissions": dangerous_perms,
        "obfuscation_score_percent": obf_score,
        "risk_score": score,
        "risk_level": level,
        "risk_emoji": LEVEL_EMOJI[level],
    }
