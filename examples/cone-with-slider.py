from paraview.simple import Cone, Show, Render

cone = Cone()
Show()
Render()

# ---------------------------------------------------------
# Add-on to turn ParaView Python script to a web app
# ---------------------------------------------------------
import paraview.web.venv
import ptc
from trame.widgets import html

web_app = ptc.Viewer()
# add-on UI
with web_app.ui:
    ptc.HoverPoint()

    with web_app.side_top:
        ptc.VSlider(
            v_model=("resolution", 6),
            min=3,
            max=60,
            step=1,
        )
        ptc.VBtn(
            "Hover {{ enable_point_hover ? 'On' : 'Off' }}",
            click="enable_point_hover = !enable_point_hover",
        )

        html.Div("{{ last_tracked_hover_data }}")


@web_app.state.change("resolution")
def on_resolution_change(resolution, **kwargs):
    cone.Resolution = resolution
    web_app.update()


web_app.state.last_tracked_hover_data = None


@web_app.state.change("hover_data")
def print_hover_data(hover_data, **kwargs):
    if hover_data:
        web_app.state.last_tracked_hover_data = hover_data


@web_app.state.change("enable_point_hover")
def clear_last_tracked_hover_data(enable_point_hover, **kwargs):
    if not enable_point_hover:
        web_app.state.last_tracked_hover_data = None


web_app.start()
