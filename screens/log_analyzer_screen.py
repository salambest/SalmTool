"""Log Analyzer screen."""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules.log_analyzer import analyze_logs
from modules.report_generator import save_all_formats

KV = """
<LogAnalyzerScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Log Analyzer"
            left_action_items: [["arrow-left", lambda x: app.go_to("dashboard")]]

        MDRaisedButton:
            text: "SCAN LOGS"
            pos_hint: {"center_x": 0.5}
            on_release: root.scan()

        ScrollView:
            MDBoxLayout:
                id: content
                orientation: "vertical"
                adaptive_height: True
                padding: dp(16)
                spacing: dp(8)

                MDLabel:
                    id: info_label
                    text: "Tap 'Scan logs' to begin."
                    markup: True
                    adaptive_height: True

        MDRaisedButton:
            text: "SAVE REPORT"
            pos_hint: {"center_x": 0.5}
            on_release: root.save_report()
"""

Builder.load_string(KV)


class LogAnalyzerScreen(MDScreen):
    last_report = None

    def scan(self):
        self.ids.info_label.text = "Scanning logs..."
        report = analyze_logs()
        self.last_report = report
        self.ids.info_label.text = self._format(report)

    def _format(self, r):
        lines = [
            f"[b]Lines scanned:[/b] {r['total_lines_scanned']}",
            f"[b]Sources available:[/b] logcat={r['source_available']['logcat']}, "
            f"termux={r['source_available']['termux']}",
            "",
            f"[b]Crashes ({len(r['crashes'])}):[/b]",
            "\n".join(r["crashes"][:15]) or "-",
            "",
            f"[b]Errors ({len(r['errors'])}):[/b]",
            "\n".join(r["errors"][:20]) or "-",
            "",
            f"[b]Warnings ({len(r['warnings'])}):[/b]",
            "\n".join(r["warnings"][:20]) or "-",
        ]
        return "\n".join(lines)

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="log_analyzer")
