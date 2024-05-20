import paraview.web.venv

from ptc import Viewer, PipelineBrowser, ColorBy, OpenFileToggle, TimeControl

web_app = Viewer()

with web_app.ui:
    with web_app.col_left:
        OpenFileToggle(classes="mb-2")
        PipelineBrowser()

    with web_app.col_center:
        ColorBy()
        TimeControl()

web_app.start()
