import paraview.web.venv  # noqa: F401
from paraview import simple

from ptc import Viewer, ThresholdEditor

from trame.widgets import vuetify3 as vuetify


class ThresholdEditorPTCViewer(Viewer):
    def __init__(self):
        super().__init__()
        self._source_proxy = None
        self.setup_visu()
        self._add_threshold_editor()

    def setup_visu(self):
        w = simple.Wavelet()
        self._source_proxy = simple.Gradient(Input=w)
        self._source_proxy.ScalarArray = ["POINTS", "RTData"]
        wavelet_display = simple.Show(self._source_proxy)
        simple.ColorBy(wavelet_display, ("POINTS", "RTData"))
        wavelet_display.Representation = "Volume"

        simple.Render()
        self.ctrl.view_update()

    def _add_threshold_editor(self):
        with self.ui, self.col_left, vuetify.VCard(style="width: 100%;"):
            slice_editor = ThresholdEditor()
            slice_editor.set_source(self._source_proxy)


if __name__ == "__main__":
    app = ThresholdEditorPTCViewer()
    app.server.start()
