from paraview import simple
from trame.ui.html import DivLayout
from trame.widgets import dockview, paraview, vuetify3 as v3


class MultiView(dockview.DockView):
    def __init__(self, theme="Dracula", **kwargs):
        super().__init__(
            active_panel=(self._on_view_activated, "[$event]"),
            remove_panel=(self._on_view_closed, "[$event]"),
            theme=theme,
            components=(
                "{ rightHeaderActionsComponent: 'ptc-multiview-add', watermarkComponent: 'ptc-multiview-watermark' }",
            ),
            **kwargs,
        )

        with DivLayout(self.server, "ptc-multiview-add") as add_panel:
            add_panel.root.style = "height: 100%;"
            add_panel.root.classes = "d-flex align-center px-2"
            v3.VBtn(
                flat=True,
                icon="mdi-plus",
                density="compact",
                click=self.add_view,
            )

        with DivLayout(self.server, "ptc-multiview-watermark") as add_panel:
            add_panel.root.style = "height: 100%; width: 100%;"
            add_panel.root.classes = "d-flex justify-center align-center"
            v3.VBtn(
                "Create RenderView",
                prepend_icon="mdi-plus",
                click=self.add_view,
            )

        paraview.initialize(self.server)

        self._view_count = 0
        self._pv_internal = {}

    def add_view(self):
        self._view_count += 1
        panel_id = f"ptc_view_{self._view_count}"
        panel_title = f"View {self._view_count}"
        template_name = f"ptc_view_{self._view_count}_template"

        # ParaView
        pv_view = simple.CreateRenderView()
        pv_view.MakeRenderWindowInteractor(True)
        self._pv_internal[panel_id] = pv_view

        with DivLayout(self.server, template_name) as ui:
            ui.root.style = "position:relative;height:100%;"
            html_view = paraview.VtkRemoteView(pv_view, interactive_ratio=1)
            v3.VBtn(
                icon="mdi-crop-free",
                click=html_view.reset_camera,
                classes="position-absolute",
                style="top: 1rem;right: 1rem; z-index: 1;",
                flat=True,
                density="compact",
            )

        self.add_panel(panel_id, panel_title, template_name)

        return panel_id

    def _on_view_closed(self, panel_id):
        if panel_id in self._pv_internal:
            pv_view = self._pv_internal.pop(panel_id)
            simple.Delete(pv_view)

    def _on_view_activated(self, panel_id):
        pv_view = self._pv_internal.get(panel_id)
        if pv_view:
            simple.SetActiveView(pv_view)
            if self.ctrl.on_active_view_change.exists():
                self.ctrl.on_active_view_change()
