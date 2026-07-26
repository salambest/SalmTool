"""
WiFi Analyzer module.

Reads information about the currently connected WiFi network via
Android's WifiManager (through pyjnius) when running on-device. Falls
back to a "not connected" style response on desktop or when permissions
are missing. Root access unlocks a couple of extra low-level details.
"""

from kivy.utils import platform as kivy_platform

from modules.root_manager import is_rooted, run_as_root
from modules.network_analyzer import get_local_ip, get_gateway


def get_wifi_info():
    info = {
        "connected": False, "ssid": None, "bssid": None,
        "signal_dbm": None, "link_speed_mbps": None,
        "ip": get_local_ip(), "gateway": get_gateway(),
    }

    if kivy_platform == "android":
        try:
            from jnius import autoclass, cast
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Context = autoclass("android.content.Context")
            activity = PythonActivity.mActivity
            wifi_manager = cast(
                "android.net.wifi.WifiManager",
                activity.getSystemService(Context.WIFI_SERVICE)
            )
            wifi_info = wifi_manager.getConnectionInfo()
            ssid = wifi_info.getSSID().replace('"', "")
            info.update({
                "connected": ssid not in ("<unknown ssid>", "", None),
                "ssid": ssid,
                "bssid": wifi_info.getBSSID(),
                "signal_dbm": wifi_info.getRssi(),
                "link_speed_mbps": wifi_info.getLinkSpeed(),
            })
        except Exception:
            pass

    return info


def get_extra_root_info():
    if not is_rooted():
        return None
    return {"proc_net_wireless": run_as_root("cat /proc/net/wireless")}


def get_full_report():
    report = get_wifi_info()
    report["root_extra"] = get_extra_root_info()
    return report
