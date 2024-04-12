from paraview.simple import Cone, Show, Render

cone = Cone()
Show()
Render()

# ---------------------------------------------------------
# Add-on to turn ParaView Python script to a web app
# ---------------------------------------------------------
import paraview.web.venv
from ptc import Viewer
from trame.widgets.vuetify3 import VSlider

web_app = Viewer()
# add-on UI
with web_app.side_top:
    VSlider(
        v_model=("resolution", 6),
        min=3,
        max=60,
        step=1,
    )


@web_app.state.change("resolution")
def on_resolution_change(resolution, **kwargs):
    cone.Resolution = resolution
    web_app.update()


web_app.start()
