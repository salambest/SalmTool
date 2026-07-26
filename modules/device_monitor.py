"""
Device Monitor module.

Collects hardware / OS level information about the running device: CPU,
RAM, storage, battery, temperature, Android version, kernel, and device
model. When root is available, also surfaces CPU governor and SELinux
status.
"""

import os
import platform as py_platform

try:
    import psutil
except ImportError:
    psutil = None

from kivy.utils import platform as kivy_platform

from modules.root_manager import is_rooted, run_as_root


def get_cpu_usage():
    if psutil:
        try:
            return round(psutil.cpu_percent(interval=0.5), 1)
        except Exception:
            pass
    return None


def get_cpu_count():
    return os.cpu_count() or (psutil.cpu_count() if psutil else None)


def get_ram_usage():
    if psutil:
        try:
            vm = psutil.virtual_memory()
            return {
                "total_mb": round(vm.total / (1024 * 1024), 1),
                "used_mb": round(vm.used / (1024 * 1024), 1),
                "percent": vm.percent,
            }
        except Exception:
            pass
    return None


def get_storage_usage(path="/"):
    if psutil:
        try:
            du = psutil.disk_usage(path)
            return {
                "total_gb": round(du.total / (1024 ** 3), 2),
                "used_gb": round(du.used / (1024 ** 3), 2),
                "free_gb": round(du.free / (1024 ** 3), 2),
                "percent": du.percent,
            }
        except Exception:
            pass
    return None


def get_battery_info():
    if kivy_platform == "android":
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            IntentFilter = autoclass("android.content.IntentFilter")
            BatteryManager = autoclass("android.os.BatteryManager")

            activity = PythonActivity.mActivity
            filter_ = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
            battery_status = activity.registerReceiver(None, filter_)

            level = battery_status.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            scale = battery_status.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            temp = battery_status.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1)
            status = battery_status.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
            percent = round(level / scale * 100, 1) if scale > 0 else None
            return {
                "percent": percent,
                "temperature_c": temp / 10.0 if temp != -1 else None,
                "charging": status == 2,
            }
        except Exception:
            pass

    if psutil and hasattr(psutil, "sensors_battery"):
        try:
            b = psutil.sensors_battery()
            if b:
                return {"percent": b.percent, "charging": b.power_plugged, "temperature_c": None}
        except Exception:
            pass
    return None


def get_temperature():
    thermal_paths = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/thermal/thermal_zone1/temp",
    ]
    for p in thermal_paths:
        try:
            with open(p, "r") as f:
                raw = int(f.read().strip())
                return round(raw / 1000.0, 1) if raw > 1000 else raw
        except Exception:
            continue
    return None


def get_android_version():
    if kivy_platform == "android":
        try:
            from jnius import autoclass
            version = autoclass("android.os.Build$VERSION")
            return version.RELEASE
        except Exception:
            pass
    return py_platform.platform()


def get_kernel_version():
    try:
        return py_platform.uname().release
    except Exception:
        return "unknown"


def get_device_model():
    if kivy_platform == "android":
        try:
            from jnius import autoclass
            build = autoclass("android.os.Build")
            return f"{build.MANUFACTURER} {build.MODEL}"
        except Exception:
            pass
    return py_platform.node() or "unknown"


def get_cpu_governor():
    if not is_rooted():
        return None
    result = run_as_root("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
    return result.strip() if result else None


def get_selinux_status():
    if not is_rooted():
        return None
    result = run_as_root("getenforce")
    return result.strip() if result else None


def get_full_report():
    """Aggregates every metric above into a single report dict, ready to
    be shown in the UI or handed to the Report Generator."""
    return {
        "cpu_usage_percent": get_cpu_usage(),
        "cpu_count": get_cpu_count(),
        "ram": get_ram_usage(),
        "storage": get_storage_usage(),
        "battery": get_battery_info(),
        "temperature_c": get_temperature(),
        "android_version": get_android_version(),
        "kernel": get_kernel_version(),
        "device_model": get_device_model(),
        "root": {
            "rooted": is_rooted(),
            "cpu_governor": get_cpu_governor(),
            "selinux": get_selinux_status(),
        },
    }
