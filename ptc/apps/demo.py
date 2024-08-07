import paraview.web.venv  # noqa: F401

from paraview import simple
from ptc import Viewer
from trame.widgets.vuetify3 import VSlider

# PV pipeline
wavelet = simple.Wavelet(registrationName="Wavelet1")
contour = simple.Contour(registrationName="Contour", Input=wavelet)
contour.ContourBy = ["POINTS", "RTData"]
contour.Isosurfaces = [157.0909652709961]
contour.PointMergeMethod = "Uniform Binning"
rep = simple.Show(contour)
view = simple.Render()

web_app = Viewer()

# add-on UI
with web_app.side_top:
    VSlider(
        v_model=("value", contour.Isosurfaces[0]),
        min=37,
        max=276,
        step=0.5,
        color="primary",
        style="margin: 0 100px;",
    )


@web_app.state.change("value")
def on_contour_value_change(value, **kwargs):
    contour.Isosurfaces = [value]
    web_app.update()


web_app.start()
