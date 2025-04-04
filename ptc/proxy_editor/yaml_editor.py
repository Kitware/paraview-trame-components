from trame.widgets import vuetify3 as v3, html
from trame.decorators import change
from yaml import load, Loader
from paraview import simple


class YamlEditorPanel(v3.VCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.disable_next_change = False

        with self:
            with html.Div(classes="pa-2"):
                v3.VTextarea(
                    auto_grow=True,
                    v_model=("ptc_yaml_props", ""),
                    density="compact",
                    hide_details=True,
                    variant="outlined",
                )

    def can_handle(self, proxy):
        if proxy is None:
            return False

        return True

    def update_ui(self, proxy):
        """Read proxy property and update UI"""
        if not self.can_handle(proxy):
            return

        lines = []
        for prop_name in proxy.ListProperties():
            if prop_name.endswith("Info"):
                continue

            if not hasattr(proxy, prop_name):
                continue

            entry = f"{prop_name}: {getattr(proxy, prop_name)}"
            if ": <" in entry:
                continue

            lines.append(entry)

        self.state.ptc_yaml_props = "\n".join(lines)

    def update_proxy(self, proxy):
        """Read UI and update proxy property"""
        if not self.can_handle(proxy):
            return

        props = load(self.state.ptc_yaml_props, Loader=Loader)
        simple.SetProperties(proxy, **props)

    @change("ptc_yaml_props")
    def on_change(self, **_):
        if self.disable_next_change:
            self.disable_next_change = False
            return

        if self.ctrl.on_active_proxy_modified.exists():
            self.ctrl.on_active_proxy_modified()
