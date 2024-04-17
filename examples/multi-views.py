import paraview.web.venv
from paraview import simple
from ptc import Viewer, PipelineBrowser

cone = simple.Cone()
sphere = simple.Sphere()
cube = simple.Box(Center=[1, 0, 0])

v1 = simple.GetRenderView()
v2 = simple.CreateRenderView()
v3 = simple.CreateRenderView()

visible = {
    v1: [cone],
    v2: [cone, sphere],
    v3: [sphere, cube],
}


def update_representation(v, s):
    r = simple.Show(s, v)
    r.Visibility = 1 if s in visible[v] else 0


# Create all representations and update visibility
for v in [v1, v2, v3]:
    for s in [cone, sphere, cube]:
        update_representation(v, s)


web_app = Viewer(views=[[v1, v2], v3])

with web_app.col_left:
    PipelineBrowser()

web_app.start()
