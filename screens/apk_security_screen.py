"""APK Security Scanner screen - static risk analysis of a selected APK."""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules.apk_security import scan_apk
from modules.report_generator import save_all_formats

KV = """
<ApkSecurityScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "APK Security Scanner"
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
                    text: "No APK scanned yet."
                    markup: True
                    adaptive_height: True

        MDRaisedButton:
            text: "SAVE REPORT"
            pos_hint: {"center_x": 0.5}
            on_release: root.save_report()
"""

Builder.load_string(KV)


class ApkSecurityScreen(MDScreen):
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
        self.ids.info_label.text = "Scanning, please wait..."
        report = scan_apk(selection[0])
        self.last_report = report
        self.ids.info_label.text = self._format(report)

    def _format(self, r):
        info = r["apk_info"]
        findings = r["findings"]
        lines = [
            f"[b]Package:[/b] {info.get('package')}",
            f"[b]Risk level:[/b] {r['risk_emoji']} {r['risk_level']}  (score {r['risk_score']})",
            f"[b]Obfuscation heuristic:[/b] {r['obfuscation_score_percent']}%",
            "",
            f"[b]Dangerous permissions ({len(r['dangerous_permissions'])}):[/b]",
            "\n".join(r["dangerous_permissions"]) or "-",
            "",
            f"[b]URLs found ({len(findings['urls'])}):[/b]",
            "\n".join(findings["urls"][:20]) or "-",
            "",
            f"[b]IP addresses found ({len(findings['ips'])}):[/b]",
            "\n".join(findings["ips"][:20]) or "-",
            "",
            f"[b]Suspicious base64-like blobs:[/b] {len(findings['base64_like_blobs'])}",
            f"[b]Native .so libraries:[/b] {len(findings['native_libraries'])}",
            "\n".join(findings["native_libraries"][:15]) or "-",
        ]
        return "\n".join(lines)

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="apk_security")
