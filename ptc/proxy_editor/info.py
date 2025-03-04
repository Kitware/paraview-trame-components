from trame.widgets import vuetify3 as v3, html


class InfoPanel(v3.VCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self:
            with html.Div(
                "No GUI for",
                classes="pa-4 text-subtitle-1 font-weight-medium",
            ):
                html.Span(
                    "{{ ptc_panel_info_group }}::{{ ptc_panel_info_name }}",
                    classes="font-weight-bold",
                )

    def can_handle(self, proxy):
        if proxy is None:
            return False

        return True

    def update_ui(self, proxy):
        """Read proxy property and update UI"""
        if not self.can_handle(proxy):
            return

        self.state.ptc_panel_info_name = proxy.GetXMLName()
        self.state.ptc_panel_info_group = proxy.GetXMLGroup()

    def update_proxy(self, proxy):
        """Read proxy property and update UI"""
        ...
