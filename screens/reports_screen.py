"""Reports screen - browse previously generated reports."""

import os
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules.report_generator import list_reports

KV = """
<ReportsScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Reports"
            left_action_items: [["arrow-left", lambda x: app.go_to("dashboard")]]
            right_action_items: [["refresh", lambda x: root.refresh()]]

        ScrollView:
            MDList:
                id: report_list
"""

Builder.load_string(KV)


class ReportsScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        from kivymd.app import MDApp
        from kivymd.uix.list import OneLineListItem

        app = MDApp.get_running_app()
        self.ids.report_list.clear_widgets()
        files = list_reports(app.reports_dir)
        if not files:
            self.ids.report_list.add_widget(OneLineListItem(text="No reports generated yet."))
            return
        for path in files:
            self.ids.report_list.add_widget(OneLineListItem(text=os.path.basename(path)))
