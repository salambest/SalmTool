"""WiFi Analyzer screen."""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules import wifi_analyzer
from modules.report_generator import save_all_formats

KV = """
<WifiAnalyzerScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "WiFi Analyzer"
            left_action_items: [["arrow-left", lambda x: app.go_to("dashboard")]]
            right_action_items: [["refresh", lambda x: root.refresh()]]

        ScrollView:
            MDBoxLayout:
                id: content
                orientation: "vertical"
                adaptive_height: True
                padding: dp(16)
                spacing: dp(8)

                MDLabel:
                    id: info_label
                    text: "Loading WiFi info..."
                    markup: True
                    adaptive_height: True

        MDRaisedButton:
            text: "SAVE REPORT"
            pos_hint: {"center_x": 0.5}
            on_release: root.save_report()
"""

Builder.load_string(KV)


class WifiAnalyzerScreen(MDScreen):
    last_report = None

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        report = wifi_analyzer.get_full_report()
        self.last_report = report
        self.ids.info_label.text = self._format(report)

    def _format(self, r):
        lines = [
            f"[b]Connected:[/b] {r['connected']}",
            f"[b]SSID:[/b] {r['ssid']}",
            f"[b]BSSID:[/b] {r['bssid']}",
            f"[b]Signal:[/b] {r['signal_dbm']} dBm",
            f"[b]Link speed:[/b] {r['link_speed_mbps']} Mbps",
            f"[b]IP:[/b] {r['ip']}    [b]Gateway:[/b] {r['gateway']}",
        ]
        if r.get("root_extra"):
            lines.append("")
            lines.append("[b]Root extra info:[/b]")
            lines.append(str(r["root_extra"].get("proc_net_wireless")))
        return "\n".join(lines)

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="wifi_analyzer")
