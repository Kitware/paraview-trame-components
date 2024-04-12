import paraview.web.venv
from pathlib import Path
from paraview import simple
from ptc import Viewer, PipelineBrowser, utils

IMAGE_STATE = str(Path(__file__).with_name("diskout-state.png").resolve())

simple.LoadState(
    IMAGE_STATE,
    data_directory=str(utils.PARAVIEW_EXAMPLES),
    restrict_to_data_directory=True,
)
web_app = Viewer(from_state=True)

with web_app.left:
    PipelineBrowser(
        style="background: rgba(255, 255, 255, 0.5);",
        classes="elevation-5 rounded-lg",
    )

web_app.start()
