import paraview.web.venv
from paraview import simple
import ptc

source = simple.OpenDataFile(str(ptc.PARAVIEW_EXAMPLES / "disk_out_ref.ex2"))
simple.Show()
simple.Render()
simple.ResetCamera()

web_app = ptc.Viewer()

with web_app.col_right:
    ptc.ViewTable(source, style="max-width: 30vw;")

web_app.start()
