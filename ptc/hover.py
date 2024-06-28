from paraview import selection, simple
from paraview.vtk import vtkCollection
from trame.decorators import TrameApp, change, controller
from trame.widgets import html
from trame.widgets import vuetify3 as v3


@TrameApp()
class HoverPoint(v3.VCard):
    def __init__(self):
        super().__init__(
            v_show=("enable_point_hover", False),
            classes="position-absolute",
            style=(
                "`left: calc(${html_view_space?.left + remote_view_mouse?.x || 0}px + 1rem); top: calc(${html_view_space?.top + html_view_space?.height - remote_view_mouse?.y||0}px + 1rem);`",
            ),
        )

        self.state.hover_data = {}
        self._extract_selection = None

        with self:
            with v3.VTable(density="compact"):
                with html.Tbody():
                    with html.Tr(v_for="v, k in hover_data", key="k"):
                        html.Td("{{ k }}")
                        html.Td("{{ v }}")

    @change("enable_point_hover")
    def on_activation_change(self, enable_point_hover, enable_picking, **_):
        if enable_point_hover:
            if self._extract_selection is None:
                self._extract_selection = simple.ExtractSelection()
                if self.server.controller.register_internal_proxy.exists():
                    self.server.controller.register_internal_proxy(
                        self._extract_selection
                    )
            self.state.enable_picking = True
            self.ctrl.enable_selection(True)
        elif enable_picking:
            simple.ClearSelection()
            if self._extract_selection and self._extract_selection.Input:
                simple.ClearSelection(self._extract_selection.Input)

            self.state.enable_picking = False
            self.ctrl.enable_selection(False)
            self.ctrl.view_update()

    @controller.add("on_active_proxy_change")
    def create_extract(self, *_):
        if self._extract_selection is None:
            self._extract_selection = simple.ExtractSelection()
            if self.server.controller.register_internal_proxy.exists():
                self.server.controller.register_internal_proxy(self._extract_selection)

    @change("remote_view_mouse")
    def on_hover(self, enable_point_hover, remote_view_mouse, **_):
        if not enable_point_hover:
            return

        if self._extract_selection is None:
            self._extract_selection = simple.ExtractSelection()
            if self.server.controller.register_internal_proxy.exists():
                self.server.controller.register_internal_proxy(self._extract_selection)

        x = remote_view_mouse.get("x")
        x_max = int(x + 0.5)
        y = remote_view_mouse.get("y")
        y_max = int(y + 0.5)

        view = simple.GetActiveView()
        simple.Render(view)

        selected_reps = vtkCollection()
        selection_sources = vtkCollection()
        view.SelectSurfacePoints(
            [int(x), int(y), x_max, y_max],
            selected_reps,
            selection_sources,
            0,
        )
        selection._collectSelectionPorts(
            selected_reps, selection_sources, False, Modifier=None
        )
        simple.Render(view)

        nb_sources = selection_sources.GetNumberOfItems()
        selection_extract = {}
        for i in range(nb_sources):
            rep = selected_reps.GetItemAsObject(i)
            source = simple.servermanager._getPyProxy(
                rep.GetProperty("Input").GetProxy(0)
            )
            self._extract_selection.Selection = simple.servermanager._getPyProxy(
                source.GetSelectionInput(0)
            )

            # Crash ParaView sometime
            # if source != self._extract_selection.Input:
            #     print("clear selection")
            #     # simple.ClearSelection(self._extract_selection.Input)
            #     self._extract_selection.Input = source

            self._extract_selection.UpdatePipeline()
            ds = simple.FetchData(self._extract_selection)[0]

            if ds.GetNumberOfPoints() == 1:
                x, y, z = ds.GetPoint(0)
                selection_extract["(x, y, z)"] = [x, y, z]
                pd = ds.GetPointData()
                n = pd.GetNumberOfArrays()
                for j in range(n):
                    array = pd.GetAbstractArray(j)
                    selection_extract[array.GetName()] = array.GetTuple(0)

        if nb_sources:
            self.state.hover_data = selection_extract

        self.ctrl.view_update()
