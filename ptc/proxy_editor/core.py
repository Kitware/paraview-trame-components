from paraview import simple, servermanager
from trame.widgets import vuetify3 as v3, client, html
from trame.decorators import controller

PXM = servermanager.ProxyManager()


def template_name(idx):
    return f"ptc_editor_{idx}"


def template_state_name(idx):
    return f"trame__template_{template_name(idx)}"


class ProxyEditor(v3.VCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.panels = []
        self.active_widget = None
        self.state.setdefault("proxy_editor_change", 0)
        self._init = True
        self._can_delete = None

        with self:
            self.flat = True

            if self.style is None:
                self.style = "width: 20rem;"
            else:
                self.style += ";width: 20rem;"
            with html.Div(
                classes="d-flex pa-2 justify-space-between align-center",
                v_show="proxy_editor_active_panel",
            ):
                v3.VBtn(
                    prepend_icon="mdi-gesture-tap",
                    text="Apply",
                    click=self._apply,
                    density="compact",
                    hide_details=True,
                    variant="tonal",
                    color="primary",
                    stacked=True,
                    disabled=("proxy_editor_auto_apply || !proxy_editor_change",),
                    size="small",
                )
                v3.VBtn(
                    prepend_icon="mdi-arrow-u-left-top",
                    text="Reset",
                    click=self._reset,
                    density="compact",
                    hide_details=True,
                    variant="tonal",
                    color="secondary",
                    stacked=True,
                    size="small",
                )
                v3.VBtn(
                    prepend_icon="mdi-delete-forever-outline",
                    text="Delete",
                    click=self._delete,
                    density="compact",
                    hide_details=True,
                    variant="tonal",
                    color="ternary",
                    stacked=True,
                    size="small",
                    disabled=("proxy_editor_delete_available", True),
                )
                v3.VCheckbox(
                    v_model=("proxy_editor_auto_apply", False),
                    true_icon="mdi-lock-check-outline",
                    false_icon="mdi-lock-open-outline",
                    density="compact",
                    hide_details=True,
                )
            client.ServerTemplate(name=("proxy_editor_active_panel", ""))

        self._init = False

    @controller.add("on_data_change")
    @controller.add("on_data_loaded")
    def _update_can_delete(self):
        self._can_delete = {}
        proxies = PXM.GetProxiesInGroup("sources")
        for key in proxies:
            proxy = proxies[key]
            proxy_id = key[1]
            self._can_delete.setdefault(proxy_id, True)

            if hasattr(proxy, "Input") and proxy.Input:
                input_prop = proxy.Input
                if hasattr(input_prop, "GetNumberOfProxies"):
                    num_proxies = input_prop.GetNumberOfProxies()
                    if num_proxies > 1:
                        for input_idx in range(num_proxies):
                            proxy_id = input_prop.GetProxy(
                                input_idx
                            ).GetGlobalIDAsString()
                            if input_idx != 0:
                                self._can_delete[proxy_id] = False
                    elif num_proxies == 1:
                        self._can_delete[
                            input_prop.GetProxy(0).GetGlobalIDAsString()
                        ] = False
                else:
                    self._can_delete[input_prop.GetGlobalIDAsString()] = False

    @controller.add("on_active_proxy_change")
    def _on_active_proxy(self):
        active_proxy = simple.GetActiveSource()
        active_proxy_id = (
            active_proxy.GetGlobalIDAsString() if active_proxy is not None else 0
        )

        if self._can_delete is None:
            self._update_can_delete()

        self.state.proxy_editor_delete_available = not self._can_delete.get(
            active_proxy_id, False
        )

        self.state.proxy_editor_active_panel = ""
        self.active_widget = None
        for idx, widget in enumerate(self.panels):
            if widget.can_handle(active_proxy):
                widget.update_ui(active_proxy)
                self.active_widget = widget
                self.state.proxy_editor_active_panel = template_name(idx + 1)

    @controller.add("on_active_proxy_modified")
    def _on_proxy_change(self):
        self.state.proxy_editor_change += 1
        if self.state.proxy_editor_auto_apply:
            self._apply()

    def _apply(self):
        if self.active_widget is None:
            return

        self.state.proxy_editor_change = 0
        active_proxy = simple.GetActiveSource()
        self.active_widget.update_proxy(active_proxy)
        self.server.controller.on_data_change()

    def _reset(self):
        if self.active_widget is None:
            return

        self.state.proxy_editor_change = 0
        active_proxy = simple.GetActiveSource()
        self.active_widget.update_ui(active_proxy)

    def _delete(self):
        active_proxy = simple.GetActiveSource()
        if active_proxy is not None:
            simple.SetActiveSource(None)
            simple.Delete(active_proxy)

            self.ctrl.on_data_change()
            self.ctrl.on_active_proxy_change()

    def add_child(self, panel_to_register):
        # Allow widget add-on in constructor
        if self._init:
            super().add_child(panel_to_register)
            return

        # register panel outside of constructor
        self.panels.append(panel_to_register)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # Delay panel html computation
        for idx, panel in enumerate(self.panels):
            self.state[template_state_name(idx + 1)] = panel.html

        return super().__exit__(exc_type, exc_value, exc_traceback)

    def clear_panels(self):
        """Remove any previously registered panel"""
        self.panels.clear()
