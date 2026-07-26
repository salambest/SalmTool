"""
SalmTool Ultimate
-----------------
Personal Android system analysis & diagnostics toolbox.

This is the application entry point. It builds the KivyMD MDApp, sets up
the ScreenManager, registers every feature screen defined under
`screens/`, and loads runtime configuration (including the AI Helper API
key) from `config.json` — never from source code.

Author: SalmTool Ultimate Project
License: MIT
"""

import os
import json

from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from screens.dashboard import DashboardScreen
from screens.device_monitor_screen import DeviceMonitorScreen
from screens.apk_analyzer_screen import ApkAnalyzerScreen
from screens.apk_security_screen import ApkSecurityScreen
from screens.network_analyzer_screen import NetworkAnalyzerScreen
from screens.wifi_analyzer_screen import WifiAnalyzerScreen
from screens.exif_analyzer_screen import ExifAnalyzerScreen
from screens.hash_checker_screen import HashCheckerScreen
from screens.log_analyzer_screen import LogAnalyzerScreen
from screens.file_manager_screen import FileManagerScreen
from screens.root_manager_screen import RootManagerScreen
from screens.ai_helper_screen import AiHelperScreen
from screens.reports_screen import ReportsScreen

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_ROOT, "config.json")

DEFAULT_CONFIG = {
    "app_name": "SalmTool Ultimate",
    "version": "1.0.0",
    "ai_helper": {"provider": "anthropic", "api_key": "", "model": "claude-sonnet-4-6"},
    "settings": {"dark_mode": True, "reports_dir": "reports"},
}


def load_config():
    """Loads config.json, falling back to safe defaults if it is missing
    or malformed so the app never crashes on startup because of it."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Make sure nested keys always exist even in a partial config file.
        data.setdefault("ai_helper", DEFAULT_CONFIG["ai_helper"])
        data.setdefault("settings", DEFAULT_CONFIG["settings"])
        return data
    except Exception:
        return DEFAULT_CONFIG


class SalmToolApp(MDApp):
    """Root application object for SalmTool Ultimate."""

    def build(self):
        self.config_data = load_config()
        self.title = self.config_data.get("app_name", "SalmTool Ultimate")

        self.theme_cls.theme_style = (
            "Dark" if self.config_data["settings"].get("dark_mode", True) else "Light"
        )
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Amber"

        if platform != "android":
            # Comfortable phone-shaped window for desktop testing.
            Window.size = (420, 780)

        self.reports_dir = os.path.join(
            self.user_data_dir, self.config_data["settings"].get("reports_dir", "reports")
        )
        os.makedirs(self.reports_dir, exist_ok=True)

        sm = MDScreenManager()
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(DeviceMonitorScreen(name="device_monitor"))
        sm.add_widget(ApkAnalyzerScreen(name="apk_analyzer"))
        sm.add_widget(ApkSecurityScreen(name="apk_security"))
        sm.add_widget(NetworkAnalyzerScreen(name="network_analyzer"))
        sm.add_widget(WifiAnalyzerScreen(name="wifi_analyzer"))
        sm.add_widget(ExifAnalyzerScreen(name="exif_analyzer"))
        sm.add_widget(HashCheckerScreen(name="hash_checker"))
        sm.add_widget(LogAnalyzerScreen(name="log_analyzer"))
        sm.add_widget(FileManagerScreen(name="file_manager"))
        sm.add_widget(RootManagerScreen(name="root_manager"))
        sm.add_widget(AiHelperScreen(name="ai_helper"))
        sm.add_widget(ReportsScreen(name="reports"))
        return sm

    def go_to(self, screen_name):
        """Simple central navigation helper used by every screen's back
        button and by the dashboard's feature cards."""
        self.root.current = screen_name

    def toggle_theme(self):
        self.theme_cls.theme_style = (
            "Light" if self.theme_cls.theme_style == "Dark" else "Dark"
        )


if __name__ == "__main__":
    SalmToolApp().run()
