"""Dashboard screen: the main entry grid with a card per feature."""

from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard

KV = """
<FeatureCard>:
    orientation: "vertical"
    size_hint: None, None
    size: dp(150), dp(120)
    padding: dp(8)
    spacing: dp(4)
    radius: [18, 18, 18, 18]
    elevation: 2

    MDLabel:
        text: root.icon_text
        halign: "center"
        font_style: "H5"

    MDLabel:
        text: root.title_text
        halign: "center"
        font_style: "Caption"
        theme_text_color: "Secondary"


<DashboardScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "SalmTool Ultimate"
            elevation: 4
            right_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]

        ScrollView:
            MDGridLayout:
                id: grid
                cols: 2
                adaptive_height: True
                padding: dp(16)
                spacing: dp(16)
"""

Builder.load_string(KV)

# (icon, title, target screen name) — add a new tuple here to register a
# new feature card on the dashboard.
FEATURES = [
    ("📱", "Device Monitor", "device_monitor"),
    ("📦", "APK Analyzer", "apk_analyzer"),
    ("🛡", "APK Security", "apk_security"),
    ("🌐", "Network Analyzer", "network_analyzer"),
    ("📡", "WiFi Analyzer", "wifi_analyzer"),
    ("🖼", "EXIF Analyzer", "exif_analyzer"),
    ("🔐", "Hash Checker", "hash_checker"),
    ("📋", "Log Analyzer", "log_analyzer"),
    ("📂", "File Manager", "file_manager"),
    ("🔓", "Root Manager", "root_manager"),
    ("🤖", "AI Helper", "ai_helper"),
    ("📊", "Reports", "reports"),
]


class FeatureCard(ButtonBehavior, MDCard):
    def __init__(self, icon_text, title_text, target_screen, **kwargs):
        self.icon_text = icon_text
        self.title_text = title_text
        self.target_screen = target_screen
        super().__init__(**kwargs)

    def on_release(self):
        from kivymd.app import MDApp
        MDApp.get_running_app().go_to(self.target_screen)


class DashboardScreen(MDScreen):
    def on_pre_enter(self, *args):
        grid = self.ids.grid
        if not grid.children:
            for icon, title, screen in FEATURES:
                grid.add_widget(FeatureCard(icon, title, screen))
