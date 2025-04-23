import paraview.web.venv  # noqa: F401

from paraview import simple
from ptc import Viewer, VSlider


class Demo(Viewer):
    def __init__(
        self,
        views=None,
        from_state=False,
        server=None,
        reset_camera_button=True,
        template_name="main",
    ):
        # pipeline
        wavelet = simple.Wavelet(registrationName="Wavelet1")
        self.contour = simple.Contour(registrationName="Contour", Input=wavelet)
        self.contour.ContourBy = ["POINTS", "RTData"]
        self.contour.Isosurfaces = [157.0909652709961]
        self.contour.PointMergeMethod = "Uniform Binning"
        self.rep = simple.Show(self.contour)
        self.view = simple.Render()

        super().__init__(
            [self.view], from_state, server, reset_camera_button, template_name
        )
        self.server.state.change("value")(self._on_contour_change)

        with self.side_top:
            VSlider(
                v_model=("value", self.contour.Isosurfaces[0]),
                min=37,
                max=276,
                step=0.5,
                color="primary",
                style="margin: 0 100px;",
            )

    def _on_contour_change(self, value, **_):
        self.contour.Isosurfaces = [value]
        self.update()


def main():
    app = Demo()
    app.start()


if __name__ == "__main__":
    main()
