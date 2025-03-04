import paraview.web.venv
from pathlib import Path
from paraview import simple

import ptc
import ptc.proxy_editor

IMAGE_STATE = str(Path(__file__).with_name("diskout-state.png").resolve())

simple.LoadState(
    IMAGE_STATE,
    data_directory=str(ptc.PARAVIEW_EXAMPLES),
    restrict_to_data_directory=True,
)
web_app = ptc.Viewer(from_state=True)

with web_app.col_left:
    ptc.PipelineBrowser()
    with ptc.ProxyEditor():
        # register UI we want to have available
        ptc.proxy_editor.InfoPanel()
        ptc.proxy_editor.PlaneEditorPanel()


with web_app.col_center:
    with ptc.ColorBy() as color:
        with color.prepend:
            ptc.RepresentBy(classes="mr-2")

    ptc.VSpacer()

web_app.start()
