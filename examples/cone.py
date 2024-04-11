from paraview.simple import Cone, Show, Render

cone = Cone()
Show()
Render()

# ---------------------------------------------------------
# Add-on to turn ParaView Python script to a web app
# ---------------------------------------------------------

import paraview.web.venv
from ptc import Viewer

web_app = Viewer()
web_app.start()
