import paraview.web.venv  # noqa: F401
from paraview import simple
import ptc

sphere = simple.Sphere()
rep = simple.Show(sphere)
view = simple.Render()

simple.ColorBy(rep, ("POINTS", "vtkProcessId"))

rep.RescaleTransferFunctionToDataRange(True, False)
rep.SetScalarBarVisibility(view, True)

web_app = ptc.Viewer(from_state=True)
web_app.start()
