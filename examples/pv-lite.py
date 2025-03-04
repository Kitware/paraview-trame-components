import paraview.web.venv
from pathlib import Path
from paraview import simple

import ptc
import ptc.proxy_editor

# -----------------------------------------------------------------------------
IMAGE_STATE = str(Path(__file__).with_name("can-state.png").resolve())

simple.LoadState(
    IMAGE_STATE,
    data_directory=str(ptc.PARAVIEW_EXAMPLES),
    restrict_to_data_directory=True,
)
# -----------------------------------------------------------------------------

web_app = ptc.Viewer(from_state=True)

with web_app.ui_layout:
    with ptc.VerticalToolbar().bar:
        ptc.VListItem(
            prepend_icon=(
                "ptc_show_color_by ? 'mdi-eye-outline' : 'mdi-eye-off-outline'",
            ),
            click="ptc_show_color_by = !ptc_show_color_by",
        )
        ptc.VListItem(
            prepend_icon=("ptc_show_vcr ? 'mdi-play' : 'mdi-play-outline'",),
            click="ptc_show_vcr = !ptc_show_vcr",
        )

with web_app.ui_view_container:
    with ptc.Div(
        v_show=("ptc_show_vcr", False),
        style="position: absolute; bottom: 0.5rem; left: 5rem; right: 5rem;",
    ):
        ptc.TimeControl()

with web_app.col_center:
    with ptc.ColorBy() as color:
        color.v_show = ("ptc_show_color_by", False)
        with color.prepend:
            ptc.RepresentBy(classes="mr-2")

web_app.start()
