"""EXIF Analyzer screen - inspect and optionally strip image metadata."""

import os
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules.exif_analyzer import extract_exif, strip_metadata
from modules.report_generator import save_all_formats

KV = """
<ExifAnalyzerScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "EXIF Analyzer"
            left_action_items: [["arrow-left", lambda x: app.go_to("dashboard")]]

        MDRaisedButton:
            text: "SELECT IMAGE"
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
                    text: "No image selected yet."
                    markup: True
                    adaptive_height: True

        MDBoxLayout:
            size_hint_y: None
            height: dp(48)
            padding: dp(8)
            spacing: dp(8)

            MDRaisedButton:
                text: "STRIP METADATA"
                on_release: root.strip_metadata_action()

            MDRaisedButton:
                text: "SAVE REPORT"
                on_release: root.save_report()
"""

Builder.load_string(KV)


class ExifAnalyzerScreen(MDScreen):
    last_report = None
    current_path = None

    def pick_file(self):
        from plyer import filechooser
        filechooser.open_file(
            on_selection=self._on_file_selected,
            filters=[("Images", "*.jpg", "*.jpeg", "*.png", "*.tiff")],
        )

    def _on_file_selected(self, selection):
        if not selection:
            return
        self.current_path = selection[0]
        report = extract_exif(self.current_path)
        self.last_report = report
        self.ids.info_label.text = self._format(report)

    def _format(self, r):
        lines = [
            f"[b]Camera model:[/b] {r.get('camera_model')}",
            f"[b]Date taken:[/b] {r.get('date_taken')}",
        ]
        if r.get("gps"):
            lines.append(f"[b]GPS:[/b] {r['gps']['latitude']:.6f}, {r['gps']['longitude']:.6f}")
        else:
            lines.append("[b]GPS:[/b] not present")
        lines.append("")
        lines.append(f"[b]Raw tags ({len(r.get('raw', {}))}):[/b]")
        for k, v in list(r.get("raw", {}).items())[:30]:
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    def strip_metadata_action(self):
        if not self.current_path:
            return
        base, ext = os.path.splitext(self.current_path)
        out_path = f"{base}_clean{ext}"
        ok = strip_metadata(self.current_path, out_path)
        suffix = f"\n\n[b]Metadata stripped:[/b] Saved to {out_path}" if ok else "\n\nFailed to strip metadata."
        self.ids.info_label.text += suffix

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="exif_analyzer")
