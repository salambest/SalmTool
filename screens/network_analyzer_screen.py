"""Network Analyzer screen."""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules import network_analyzer
from modules.report_generator import save_all_formats

KV = """
<NetworkAnalyzerScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Network Analyzer"
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
                    text: "Loading network info..."
                    markup: True
                    adaptive_height: True

        MDBoxLayout:
            size_hint_y: None
            height: dp(48)
            padding: dp(8)
            spacing: dp(8)

            MDRaisedButton:
                text: "PING TEST"
                on_release: root.run_ping()

            MDRaisedButton:
                text: "SAVE REPORT"
                on_release: root.save_report()
"""

Builder.load_string(KV)


class NetworkAnalyzerScreen(MDScreen):
    last_report = None

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        report = network_analyzer.get_full_report()
        self.last_report = report
        self.ids.info_label.text = self._format(report)

    def _format(self, r):
        lines = [
            f"[b]Hostname:[/b] {r['hostname']}",
            f"[b]Local IP:[/b] {r['local_ip']}",
            f"[b]Gateway:[/b] {r['gateway']}",
            f"[b]DNS servers:[/b] {', '.join(r['dns_servers']) or '-'}",
            "",
            "[b]Interfaces:[/b]",
        ]
        for name, ip in r["interfaces"].items():
            lines.append(f"  {name}: {ip}")
        return "\n".join(lines)

    def run_ping(self):
        self.ids.info_label.text = "Pinging 8.8.8.8 ..."
        result = network_analyzer.ping_host("8.8.8.8", count=4)
        if self.last_report:
            self.last_report["ping_test"] = result
        base = self._format(self.last_report) if self.last_report else ""
        self.ids.info_label.text = base + f"\n\n[b]Ping result:[/b]\n{result['output']}"

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="network_analyzer")
