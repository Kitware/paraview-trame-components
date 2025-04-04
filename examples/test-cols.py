from paraview.simple import Cone, Show, Render

cone = Cone()
Show()
Render()

# ---------------------------------------------------------
# Add-on to turn ParaView Python script to a web app
# ---------------------------------------------------------

import paraview.web.venv
from ptc import Viewer
from trame.widgets import vuetify3

web_app = Viewer()


def create_elem(name):
    with vuetify3.VCard(classes="ma-2"):
        vuetify3.VCardTitle(name)


def customize(elem, class_name):
    elem.classes += class_name
    elem.style += "opacity: 0.5;"


with web_app.col_left as left:
    customize(left, "bg-blue")
    for i in range(4):
        create_elem(f"Item {i + 1}")

with web_app.col_center as center:
    customize(center, "bg-white")
    for i in range(2):
        create_elem(f"Item {i + 1}")


with web_app.col_right as right:
    customize(right, "bg-red")
    for i in range(4):
        create_elem(f"Item {i + 1}")

web_app.start()
