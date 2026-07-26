"""
Root Manager module.

Detects root access (Magisk / KernelSU / generic su binary), executes
privileged commands when available, and exposes extra system info that
requires root (SELinux enforcement mode, detailed CPU info, etc).

Design rule: the app must be fully usable WITHOUT root. Every function
here fails softly and returns None / False instead of raising, so calling
code can simply display "Root not available" instead of crashing.
"""

import subprocess
import os

SU_PATHS = [
    "/system/bin/su",
    "/system/xbin/su",
    "/sbin/su",
    "/system/sd/xbin/su",
    "/data/local/xbin/su",
    "/data/local/bin/su",
    "/data/local/su",
]

MAGISK_PATHS = [
    "/sbin/.magisk",
    "/data/adb/magisk",
    "/data/adb/modules",
]

KERNELSU_PATHS = [
    "/data/adb/ksu",
    "/data/adb/ksud",
]

_root_cache = None


def _binary_exists():
    return any(os.path.exists(p) for p in SU_PATHS)


def _test_su_shell():
    try:
        proc = subprocess.run(
            ["su", "-c", "id"],
            capture_output=True, text=True, timeout=3
        )
        return "uid=0" in proc.stdout
    except Exception:
        return False


def is_rooted(force_recheck=False):
    """Returns True/False. Cached after the first successful check so the
    UI can call this often without repeatedly shelling out."""
    global _root_cache
    if _root_cache is not None and not force_recheck:
        return _root_cache
    result = _binary_exists() or _test_su_shell()
    _root_cache = result
    return result


def detect_magisk():
    return any(os.path.exists(p) for p in MAGISK_PATHS)


def detect_kernelsu():
    return any(os.path.exists(p) for p in KERNELSU_PATHS)


def get_root_provider():
    if detect_magisk():
        return "Magisk"
    if detect_kernelsu():
        return "KernelSU"
    if is_rooted():
        return "Unknown su implementation"
    return None


def run_as_root(command, timeout=5):
    """Runs a shell command with `su -c`. Returns stdout string, or None
    on any failure (no root, su denied, timeout, etc)."""
    if not is_rooted():
        return None
    try:
        proc = subprocess.run(
            ["su", "-c", command],
            capture_output=True, text=True, timeout=timeout
        )
        return proc.stdout
    except Exception:
        return None


def get_selinux_status():
    return run_as_root("getenforce")


def get_extra_system_info():
    """Extra root-only diagnostics used by the Root Manager screen."""
    if not is_rooted():
        return None
    return {
        "selinux": get_selinux_status(),
        "build_tags": run_as_root("getprop ro.build.tags"),
        "cpu_info": run_as_root("cat /proc/cpuinfo"),
    }


def get_root_summary():
    rooted = is_rooted()
    return {
        "rooted": rooted,
        "provider": get_root_provider() if rooted else None,
        "selinux": get_selinux_status() if rooted else None,
    }
