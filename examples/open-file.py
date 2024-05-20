import paraview.web.venv

from ptc import Viewer, PipelineBrowser, ColorBy, OpenFileDialog, TimeControl

web_app = Viewer()

with web_app.ui:
    with web_app.col_left:
        PipelineBrowser()

    with web_app.col_center:
        ColorBy()
        TimeControl()

    OpenFileDialog()

web_app.start()
