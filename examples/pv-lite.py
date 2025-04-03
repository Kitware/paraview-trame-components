import paraview.web.venv
from pathlib import Path
from paraview import simple

import ptc
from ptc.apps.lite import Lite

# -----------------------------------------------------------------------------
IMAGE_STATE = str(Path(__file__).with_name("can-state.png").resolve())

simple.LoadState(
    IMAGE_STATE,
    data_directory=str(ptc.PARAVIEW_EXAMPLES),
    restrict_to_data_directory=True,
)

app = Lite()
app.start()
