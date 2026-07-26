"""
APK Analyzer module.

Extracts package metadata (package name, version, permissions, activities,
services, receivers, providers) from an .apk file, plus its SHA256 hash.

Primary strategy: use `pyaxmlparser` when it is installed, for accurate
binary-XML parsing of AndroidManifest.xml. Fallback strategy: a lightweight
heuristic that scans the compiled manifest for readable ASCII / UTF-16
strings. This keeps the app fully functional even on builds that skip the
optional dependency (Android recipe availability can vary by build setup).
"""

import hashlib
import re
import zipfile

try:
    from pyaxmlparser import APK as _PyAxmlAPK
except Exception:
    _PyAxmlAPK = None


def sha256_of_file(path, chunk_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_strings(data, min_len=6):
    """Pulls out printable ASCII and UTF-16LE strings from raw bytes.
    This is the same trick classic `strings` utilities use, and is good
    enough to spot permission names, class names, and URLs embedded in a
    compiled binary-XML or DEX file without a full parser."""
    ascii_strings = re.findall(rb"[\x20-\x7e]{%d,}" % min_len, data)
    utf16_strings = re.findall(rb"(?:[\x20-\x7e]\x00){%d,}" % min_len, data)
    out = [s.decode("ascii", "ignore") for s in ascii_strings]
    out += [s.decode("utf-16-le", "ignore") for s in utf16_strings]
    return out


def _fallback_manifest_scan(apk_path):
    """Heuristic manifest parser used when pyaxmlparser isn't available."""
    result = {
        "package": None, "version_name": None, "version_code": None,
        "permissions": [], "components": [],
    }
    with zipfile.ZipFile(apk_path) as z:
        try:
            manifest_data = z.read("AndroidManifest.xml")
        except KeyError:
            return result

        strings = _extract_strings(manifest_data)

        for s in strings:
            if s.startswith("android.permission.") and s not in result["permissions"]:
                result["permissions"].append(s)

        # Dotted, class-like names (com.example.MainActivity, etc). Without
        # a full binary-XML tag parser we cannot be 100% sure whether each
        # one is an activity, service, receiver, or provider, so they are
        # reported together under a single "components" bucket.
        class_like = [
            s for s in strings
            if re.match(r"^[a-zA-Z][\w]*(\.[a-zA-Z][\w]*)+$", s)
            and not s.startswith("android.permission.")
        ]
        result["components"] = sorted(set(class_like))[:60]
    return result


def analyze_apk(apk_path):
    """Returns a dict describing the APK. Never raises for a valid zip
    file — parsing failures degrade gracefully to partial results."""
    report = {
        "file_path": apk_path,
        "sha256": sha256_of_file(apk_path),
        "app_name": None,
        "package": None,
        "version_name": None,
        "version_code": None,
        "permissions": [],
        "activities": [],
        "services": [],
        "receivers": [],
        "providers": [],
        "parser": None,
    }

    if _PyAxmlAPK is not None:
        try:
            apk = _PyAxmlAPK(apk_path)
            report.update({
                "app_name": apk.get_app_name(),
                "package": apk.get_package(),
                "version_name": apk.version_name,
                "version_code": apk.version_code,
                "permissions": apk.get_permissions(),
                "activities": apk.get_activities(),
                "services": apk.get_services(),
                "receivers": apk.get_receivers(),
                "providers": apk.get_providers(),
                "parser": "pyaxmlparser",
            })
            return report
        except Exception:
            pass  # fall through to the heuristic parser below

    fallback = _fallback_manifest_scan(apk_path)
    report.update({
        "package": fallback.get("package"),
        "version_name": fallback.get("version_name"),
        "version_code": fallback.get("version_code"),
        "permissions": fallback.get("permissions"),
        "activities": fallback.get("components", []),
        "parser": "heuristic-fallback",
    })
    return report
