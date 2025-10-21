"""
This example is taken from the classroom tutorial of https://docs.paraview.org/en/latest/Tutorials/ClassroomTutorials/targetedTrame.html
with the inclusion of the buttons
"""

import paraview.web.venv  # noqa: F401, isort: skip


from trame.app import TrameApp
from trame.decorators import change
from trame.widgets import vuetify2 as v2, paraview as pv_widgets
from trame.ui.vuetify2 import SinglePageLayout

from paraview import simple
from ptc.vue2 import ResetCameraButtons, PalettePicker
# -----------------------------------------------------------------------------


class ConeApp(TrameApp):
    def __init__(self, server=None):
        super().__init__(server, client_type="vue2")

        self.cone = simple.Cone()
        self.representation = simple.Show(self.cone)
        self.view = simple.Render()

        self.state.trame__title = "ParaView - Cone"
        self.ui = self._build_ui()

    @change("resolution")
    def on_resolution_change(self, resolution, **_):
        self.cone.Resolution = resolution
        self.ctrl.view_update()

    def reset_resolution(self):
        self.state.resolution = 6

    def _build_ui(self):
        with SinglePageLayout(self.server, full_height=True) as layout:
            layout.icon.click = self.ctrl.view_reset_camera
            layout.title.set_text("ParaView - Cone")

            with layout.toolbar:
                v2.VSpacer()
                v2.VSlider(
                    v_model=("resolution", 6),
                    min=3,
                    max=60,
                    step=1,
                    hide_details=True,
                    dense=True,
                    style="max-width: 300px",
                )
                v2.VDivider(vertical=True, classes="mx-2")
                with v2.VBtn(icon=True, click=self.reset_resolution):
                    v2.VIcon("mdi-undo-variant")

            with (
                layout.content,
                v2.VContainer(fluid=True, classes="pa-0 fill-height"),
                pv_widgets.VtkRemoteView(self.view, interactive_ratio=1) as html_view,
            ):
                PalettePicker("WhiteBackground")
                ResetCameraButtons(rounded="xl")

                # Choose which buttons to show
                # ResetCameraButtons(
                #     show_reset_camera=True,
                #     show_reset_camera_x=False,
                #     show_reset_camera_y=False,
                #     show_reset_camera_z=True,
                #     show_interaction_mode=True, # Toggle between 2D and 3D
                # )
                # ResetCameraButtons(classes="position-absolute", style="top: 1rem; right: 1rem;")
                self.ctrl.view_reset_camera = html_view.reset_camera
                self.ctrl.view_update = html_view.update

                self.ctrl.on_data_change.add(self.ctrl.view_update)

            return layout


# -----------------------------------------------------------------------------


app = ConeApp()
app.server.start()
