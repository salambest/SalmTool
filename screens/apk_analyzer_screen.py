"""APK Analyzer screen - pick an .apk and inspect its manifest metadata."""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules.apk_analyzer import analyze_apk
from modules.report_generator import save_all_formats

KV = """
<ApkAnalyzerScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "APK Analyzer"
            left_action_items: [["arrow-left", lambda x: app.go_to("dashboard")]]

        MDRaisedButton:
            text: "SELECT APK FILE"
            pos_hint: {"center_x": 0.5}
            on_release: root.pick_file()

        ScrollView:
            MDBoxLayout:
                id: content
                orientation: "vertical"
                adaptive_height: True
                padding: dp(16)
                spacing: dp(8)

                MDLabel:
                    id: info_label
                    text: "No APK selected yet."
                    markup: True
                    adaptive_height: True

        MDRaisedButton:
            text: "SAVE REPORT"
            pos_hint: {"center_x": 0.5}
            on_release: root.save_report()
"""

Builder.load_string(KV)


class ApkAnalyzerScreen(MDScreen):
    last_report = None

    def pick_file(self):
        from plyer import filechooser
        filechooser.open_file(
            on_selection=self._on_file_selected,
            filters=[("APK files", "*.apk")],
        )

    def _on_file_selected(self, selection):
        if not selection:
            return
        self.ids.info_label.text = "Analyzing..."
        report = analyze_apk(selection[0])
        self.last_report = report
        self.ids.info_label.text = self._format(report)

    def _format(self, r):
        lines = [
            f"[b]App name:[/b] {r.get('app_name')}",
            f"[b]Package:[/b] {r.get('package')}",
            f"[b]Version:[/b] {r.get('version_name')} ({r.get('version_code')})",
            f"[b]SHA256:[/b] {r.get('sha256')}",
            f"[b]Parser used:[/b] {r.get('parser')}",
            "",
            f"[b]Permissions ({len(r.get('permissions', []))}):[/b]",
            "\n".join(r.get("permissions", [])[:40]) or "-",
            "",
            f"[b]Activities / components ({len(r.get('activities', []))}):[/b]",
            "\n".join(r.get("activities", [])[:30]) or "-",
        ]
        return "\n".join(lines)

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="apk_analyzer")
