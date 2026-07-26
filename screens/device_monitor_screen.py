"""Device Monitor screen - shows live hardware / OS stats."""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules import device_monitor
from modules.report_generator import save_all_formats

KV = """
<DeviceMonitorScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Device Monitor"
            left_action_items: [["arrow-left", lambda x: app.go_to("dashboard")]]
            right_action_items: [["refresh", lambda x: root.refresh()]]

        ScrollView:
            MDBoxLayout:
                id: content
                orientation: "vertical"
                adaptive_height: True
                padding: dp(16)
                spacing: dp(10)

                MDLabel:
                    id: info_label
                    text: "Loading device information..."
                    markup: True
                    adaptive_height: True

        MDRaisedButton:
            text: "SAVE REPORT"
            pos_hint: {"center_x": 0.5}
            on_release: root.save_report()
"""

Builder.load_string(KV)


class DeviceMonitorScreen(MDScreen):
    last_report = None

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        report = device_monitor.get_full_report()
        self.last_report = report
        self.ids.info_label.text = self._format(report)

    def _format(self, r):
        lines = [
            f"[b]Device:[/b] {r['device_model']}",
            f"[b]Android:[/b] {r['android_version']}    [b]Kernel:[/b] {r['kernel']}",
            "",
            f"[b]CPU usage:[/b] {r['cpu_usage_percent']}%    [b]Cores:[/b] {r['cpu_count']}",
        ]
        if r["ram"]:
            lines.append(
                f"[b]RAM:[/b] {r['ram']['used_mb']} / {r['ram']['total_mb']} MB ({r['ram']['percent']}%)"
            )
        if r["storage"]:
            lines.append(
                f"[b]Storage:[/b] {r['storage']['used_gb']} / {r['storage']['total_gb']} GB "
                f"({r['storage']['percent']}%)"
            )
        if r["battery"]:
            lines.append(
                f"[b]Battery:[/b] {r['battery'].get('percent')}%  charging: {r['battery'].get('charging')}"
            )
        if r["temperature_c"] is not None:
            lines.append(f"[b]Temperature:[/b] {r['temperature_c']}°C")

        root_info = r["root"]
        lines.append("")
        lines.append(f"[b]Root:[/b] {'Yes' if root_info['rooted'] else 'No'}")
        if root_info["rooted"]:
            lines.append(f"[b]CPU governor:[/b] {root_info.get('cpu_governor')}")
            lines.append(f"[b]SELinux:[/b] {root_info.get('selinux')}")
        return "\n".join(lines)

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="device_monitor")
