import paraview.web.venv  # noqa: F401
from paraview import simple

from ptc import Viewer, ColorOpacityEditor

from trame.widgets import vuetify3 as vuetify


class ColorOpacityEditorPTCViewer(Viewer):
    def __init__(self):
        super().__init__()
        self._source_proxy = None
        self.setup_visu()
        self.state.preset_name = "Fast"
        self._add_color_editor()

    def setup_visu(self):
        self._source_proxy = simple.Wavelet()
        wavelet_display = simple.Show(self._source_proxy)
        simple.ColorBy(wavelet_display, ("POINTS", "RTData"))
        wavelet_display.Representation = "Volume"

        # get color transfer function/color map for 'RTData'
        lut = simple.GetColorTransferFunction("RTData")
        color_bar = simple.GetScalarBar(lut, simple.GetActiveView())
        color_bar.Visibility = 1

        simple.Render()
        self.ctrl.view_update()

    def _add_color_editor(self):
        with self.ui, self.col_left:
            with vuetify.VCard(style="width: 100%;"):
                ColorOpacityEditor()


if __name__ == "__main__":
    app = ColorOpacityEditorPTCViewer()
    app.server.start()
