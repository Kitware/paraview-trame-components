import paraview.web.venv  # noqa: F401
from paraview import simple

from ptc import Viewer, SliceEditor

from trame.widgets import vuetify3 as vuetify


class SliceEditorPTCViewer(Viewer):
    def __init__(self):
        super().__init__()
        self._source_proxy = None
        self.setup_visu()
        self._add_slice_editor()

    def setup_visu(self):
        self._source_proxy = simple.Wavelet()
        wavelet_display = simple.Show(self._source_proxy)
        simple.ColorBy(wavelet_display, ("POINTS", "RTData"))
        wavelet_display.Representation = "Volume"

        simple.Render()
        self.ctrl.view_update()

    def _add_slice_editor(self):
        with self.ui, self.col_left, vuetify.VCard(style="width: 100%;"):
            slice_editor = SliceEditor()
            slice_editor.set_source(self._source_proxy)


if __name__ == "__main__":
    app = SliceEditorPTCViewer()
    app.server.start()
