import paraview.web.venv
from pathlib import Path
from paraview import simple

import ptc

IMAGE_STATE = str(Path(__file__).with_name("diskout-state.png").resolve())

simple.LoadState(
    IMAGE_STATE,
    data_directory=str(ptc.PARAVIEW_EXAMPLES),
    restrict_to_data_directory=True,
)
web_app = ptc.Viewer(from_state=True)

with web_app.col_left:
    ptc.PipelineBrowser()
    ptc.VSpacer()
    ptc.PalettePicker("WhiteBackground")

with web_app.col_center:
    with ptc.ColorBy() as color:
        with color.prepend:
            ptc.RepresenteBy(classes="mr-2")

    ptc.VSpacer()

web_app.start()
