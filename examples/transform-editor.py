import paraview.web.venv
from paraview import simple

from ptc import Viewer, TransformEditor

render_view = simple.GetActiveViewOrCreate("RenderView")

# Will not be updated
sphere = simple.Sphere()
sphere.Radius = 1.0
simple.Show(sphere)

box_source = simple.Box()
simple.Show(box_source)
simple.SetActiveSource(box_source)

web_app = Viewer()

with web_app.ui:
    with web_app.col_left:
        TransformEditor(
            show_translation=True,
            show_scale=True,
            show_origin=True,
            show_orientation=True,
        )

web_app.start()
