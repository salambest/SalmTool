"""AI Error Helper screen."""

from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

from modules.ai_helper import explain_error
from modules.report_generator import save_all_formats

KV = """
<AiHelperScreen>:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "AI Error Helper"
            left_action_items: [["arrow-left", lambda x: app.go_to("dashboard")]]

        MDTextField:
            id: error_field
            hint_text: "Paste an error message or stack trace"
            multiline: True
            size_hint_x: 0.9
            pos_hint: {"center_x": 0.5}

        MDRaisedButton:
            text: "EXPLAIN & SUGGEST FIX"
            pos_hint: {"center_x": 0.5}
            on_release: root.ask_ai()

        ScrollView:
            MDBoxLayout:
                id: content
                orientation: "vertical"
                adaptive_height: True
                padding: dp(16)
                spacing: dp(8)

                MDLabel:
                    id: info_label
                    text: "Result will appear here."
                    markup: True
                    adaptive_height: True

        MDRaisedButton:
            text: "SAVE REPORT"
            pos_hint: {"center_x": 0.5}
            on_release: root.save_report()
"""

Builder.load_string(KV)


class AiHelperScreen(MDScreen):
    last_report = None

    def ask_ai(self):
        error_text = self.ids.error_field.text.strip()
        if not error_text:
            self.ids.info_label.text = "Please paste an error message first."
            return
        self.ids.info_label.text = "Asking AI Helper..."
        result = explain_error(error_text)
        self.last_report = {"error_input": error_text, "ai_response": result["text"], "ok": result["ok"]}
        self.ids.info_label.text = result["text"]

    def save_report(self):
        if not self.last_report:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        save_all_formats(self.last_report, app.reports_dir, name="ai_helper")
