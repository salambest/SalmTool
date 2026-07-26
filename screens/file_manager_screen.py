"""File Manager screen - search files and build reports about them."""

import os
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules.file_manager import search_files, build_files_report
from modules.report_generator import save_all_formats

KV = """
<FileManagerScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "File Manager"
            left_action_items: [["arrow-left", lambda x: app.go_to("dashboard")]]

        MDTextField:
            id: dir_field
            hint_text: "Directory to search (default: home)"
            size_hint_x: 0.9
            pos_hint: {"center_x": 0.5}

        MDTextField:
            id: pattern_field
            hint_text: "Filename pattern (e.g. *.apk)"
            text: "*"
            size_hint_x: 0.9
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "SEARCH"
            pos_hint: {"center_x": 0.5}
            on_release: root.search()

        ScrollView:
            MDBoxLayout:
                id: content
                orientation: "vertical"
                adaptive_height: True
                padding: dp(16)
                spacing: dp(8)

                MDLabel:
                    id: info_label
                    text: "No search run yet."
                    markup: True
                    adaptive_height: True

        MDRaisedButton:
            text: "SAVE REPORT"
            pos_hint: {"center_x": 0.5}
            on_release: root.save_report()
"""

Builder.load_string(KV)


class FileManagerScreen(MDScreen):
    last_report = None

    def search(self):
        root_dir = self.ids.dir_field.text.strip() or os.path.expanduser("~")
        pattern = self.ids.pattern_field.text.strip() or "*"
        self.ids.info_label.text = "Searching..."
        matches = search_files(root_dir, pattern)
        results = build_files_report(matches)
        self.last_report = {"root_dir": root_dir, "pattern": pattern, "results": results}
        self.ids.info_label.text = self._format(self.last_report)

    def _format(self, r):
        lines = [f"[b]Found {len(r['results'])} file(s) under[/b] {r['root_dir']}", ""]
        for item in r["results"][:40]:
            if "error" in item:
                continue
            lines.append(f"{item['path']} — {item['size_human']} — {item['modified']}")
        return "\n".join(lines)

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="file_manager")
