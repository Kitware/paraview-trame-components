import paraview.web.venv
from pathlib import Path
from paraview import simple
from ptc import Viewer
from trame.widgets.vuetify3 import VSlider

IMAGE_WITH_STATE = str(Path(__file__).with_name("wavelet-state.png").resolve())

simple.LoadState(IMAGE_WITH_STATE)
contour1 = simple.FindSource("Contour1")

web_app = Viewer(from_state=True)

# add-on UI
with web_app.side_top:
    VSlider(
        v_model=("value", contour1.Isosurfaces[0]),
        min=37,
        max=276,
        step=0.5,
        color="primary",
    )


@web_app.state.change("value")
def on_contour_value_change(value, **kwargs):
    contour1.Isosurfaces = [value]
    web_app.update()


web_app.start()
