"""Root Manager screen."""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules.root_manager import get_root_summary, get_extra_system_info
from modules.report_generator import save_all_formats

KV = """
<RootManagerScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Root Manager"
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
                    text: "Checking root status..."
                    markup: True
                    adaptive_height: True

        MDRaisedButton:
            text: "SAVE REPORT"
            pos_hint: {"center_x": 0.5}
            on_release: root.save_report()
"""

Builder.load_string(KV)


class RootManagerScreen(MDScreen):
    last_report = None

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        summary = get_root_summary()
        extra = get_extra_system_info() if summary["rooted"] else None
        report = {**summary, "extra": extra}
        self.last_report = report
        self.ids.info_label.text = self._format(report)

    def _format(self, r):
        lines = [
            f"[b]Rooted:[/b] {'Yes' if r['rooted'] else 'No'}",
            f"[b]Provider:[/b] {r.get('provider')}",
            f"[b]SELinux:[/b] {r.get('selinux')}",
        ]
        if not r["rooted"]:
            lines.append("")
            lines.append(
                "SalmTool Ultimate works fully without root - root-only features "
                "(deep logs, SELinux, kernel details) simply stay hidden."
            )
        elif r.get("extra"):
            lines.append("")
            lines.append("[b]Extra system info available.[/b] Save the report to view it in full.")
        return "\n".join(lines)

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="root_manager")
