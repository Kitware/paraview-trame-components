import paraview.web.venv  # noqa: F401
from paraview import simple
import ptc


class Sphere(ptc.Viewer):
    def __init__(self):
        self.sphere = simple.Sphere()
        self.rep = simple.Show(self.sphere)
        self.view = simple.Render()

        simple.ColorBy(self.rep, ("POINTS", "vtkProcessId"))
        self.rep.RescaleTransferFunctionToDataRange(True, False)
        self.rep.SetScalarBarVisibility(self.view, True)

        super().__init__(from_state=True)


def main():
    app = Sphere()
    app.start()


if __name__ == "__main__":
    main()
