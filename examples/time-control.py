import paraview.web.venv
from pathlib import Path
from paraview import simple
from ptc import Viewer, PipelineBrowser, TimeControl, PARAVIEW_EXAMPLES

IMAGE_STATE = str(Path(__file__).with_name("can-state.png").resolve())

simple.LoadState(
    IMAGE_STATE,
    data_directory=str(PARAVIEW_EXAMPLES),
    restrict_to_data_directory=True,
)
web_app = Viewer(from_state=True)

with web_app.col_left:
    PipelineBrowser()

with web_app.col_center:
    TimeControl(time_expression="custom_time_expression")


@web_app.state.change("time_index")
def on_time_index_changed(time_index, **kwargs):
    web_app.state.custom_time_expression = f"Custom message {time_index}"


web_app.start()
