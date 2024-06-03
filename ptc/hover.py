from paraview import simple
from trame.decorators import TrameApp, change
from trame.widgets import html, vuetify3


@TrameApp()
class HoverPoint(vuetify3.VCard):
    def __init__(self):
        super().__init__(
            v_show=("enable_point_hover", False),
            classes="position-absolute",
            style=(
                "`left: calc(${html_view_space?.left + remote_view_mouse?.x || 0}px + 1rem); top: calc(${html_view_space?.top + html_view_space?.height - remote_view_mouse?.y||0}px + 1rem);`",
            ),
        )

        self._extract_selection = simple.ExtractSelection()

        with self:
            html.Div("Some content")
            # self.load_data_from_proxy = ViewTable(
            #     self._extract_selection
            # ).load_data_from_proxy

    @change("enable_point_hover")
    def on_activation_change(self, enable_point_hover, enable_picking, **_):
        if enable_point_hover:
            self.state.enable_picking = True
            self.ctrl.enable_selection(True)
        elif enable_picking:
            simple.ClearSelection()
            self.state.enable_picking = False
            self.ctrl.enable_selection(False)
            self.ctrl.view_update()

    @change("remote_view_mouse")
    def on_hover(self, enable_point_hover, remote_view_mouse, **_):
        if not enable_point_hover:
            return

        x = remote_view_mouse.get("x")
        x_max = int(x + 0.5)
        y = remote_view_mouse.get("y")
        y_max = int(y + 0.5)
        simple.SelectSurfacePoints(
            Rectangle=[int(x), int(y), x_max, y_max], Modifier=None
        )
        self.ctrl.view_update()

        self._extract_selection.UpdatePipeline()
        ds = simple.FetchData(self._extract_selection)[0]

        print(ds.GetNumberOfPoints())  # noqa: T201
