"""Hash Checker screen - compute and compare file hashes."""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules.hash_checker import compute_all, compare_hashes
from modules.report_generator import save_all_formats

KV = """
<HashCheckerScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Hash Checker"
            left_action_items: [["arrow-left", lambda x: app.go_to("dashboard")]]

        MDRaisedButton:
            text: "SELECT FILE"
            pos_hint: {"center_x": 0.5}
            on_release: root.pick_file()

        MDTextField:
            id: compare_field
            hint_text: "Paste a hash to compare against"
            size_hint_x: 0.9
            pos_hint: {"center_x": 0.5}

        ScrollView:
            MDBoxLayout:
                id: content
                orientation: "vertical"
                adaptive_height: True
                padding: dp(16)
                spacing: dp(8)

                MDLabel:
                    id: info_label
                    text: "No file selected yet."
                    markup: True
                    adaptive_height: True

        MDBoxLayout:
            size_hint_y: None
            height: dp(48)
            padding: dp(8)
            spacing: dp(8)

            MDRaisedButton:
                text: "COMPARE"
                on_release: root.compare()

            MDRaisedButton:
                text: "SAVE REPORT"
                on_release: root.save_report()
"""

Builder.load_string(KV)


class HashCheckerScreen(MDScreen):
    last_report = None

    def pick_file(self):
        from plyer import filechooser
        filechooser.open_file(on_selection=self._on_file_selected)

    def _on_file_selected(self, selection):
        if not selection:
            return
        self.ids.info_label.text = "Computing hashes..."
        hashes = compute_all(selection[0])
        self.last_report = {"file": selection[0], **hashes}
        self.ids.info_label.text = self._format(self.last_report)

    def _format(self, r):
        return (
            f"[b]File:[/b] {r['file']}\n"
            f"[b]MD5:[/b] {r['md5']}\n"
            f"[b]SHA1:[/b] {r['sha1']}\n"
            f"[b]SHA256:[/b] {r['sha256']}"
        )

    def compare(self):
        if not self.last_report:
            return
        target = self.ids.compare_field.text.strip()
        if not target:
            return
        match = any(compare_hashes(target, self.last_report[algo]) for algo in ("md5", "sha1", "sha256"))
        self.last_report["compared_against"] = target
        self.last_report["match"] = match
        self.ids.info_label.text = self._format(self.last_report) + f"\n\n[b]Match:[/b] {'YES' if match else 'NO'}"

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="hash_checker")
