from paraview import simple

simple.Wavelet()
r = simple.Show()
r.Representation = "Surface"
simple.ColorBy(r, ("POINTS", "RTData"))

simple.Cone(Height=25, Radius=12)
simple.Show()

simple.Render()

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
        ptc.VBtn(
            "Hover {{ enable_point_hover ? 'On' : 'Off' }}",
            click="enable_point_hover = !enable_point_hover",
        )


web_app.start()
