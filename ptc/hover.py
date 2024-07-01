from paraview import selection, simple
from paraview.vtk import vtkCollection
from trame.decorators import TrameApp, change, controller
from trame.widgets import html
from trame.widgets import vuetify3 as v3


def select_points_on_surface(area, extract_selection_filter):
    extract_info = {}
    selection_sources, selected_reps = vtkCollection(), vtkCollection()
    view = simple.GetActiveView()
    simple.Render(view)

    view.SelectSurfacePoints(
        area,
        selected_reps,
        selection_sources,
        0,
    )

    selection._collectSelectionPorts(
        selected_reps, selection_sources, False, Modifier=None
    )
    simple.Render(view)

    nb_sources = selection_sources.GetNumberOfItems()
    for i in range(nb_sources):
        rep = selected_reps.GetItemAsObject(i)
        source = simple.servermanager._getPyProxy(rep.GetProperty("Input").GetProxy(0))
        extract_selection_filter.Selection = simple.servermanager._getPyProxy(
            source.GetSelectionInput(0)
        )

        # Crash ParaView sometime
        # if source != self._extract_selection.Input:
        #     print("clear selection")
        #     # simple.ClearSelection(self._extract_selection.Input)
        #     self._extract_selection.Input = source

        extract_selection_filter.UpdatePipeline()
        ds = simple.FetchData(extract_selection_filter)[0]

        if ds.GetNumberOfPoints() == 1:
            x, y, z = ds.GetPoint(0)
            extract_info["(x, y, z)"] = [x, y, z]
            pd = ds.GetPointData()
            n = pd.GetNumberOfArrays()
            for j in range(n):
                array = pd.GetAbstractArray(j)
                extract_info[array.GetName()] = array.GetTuple(0)

    return extract_info


def select_cells_on_surface(area, extract_selection_filter):
    extract_info = {}
    selection_sources, selected_reps = vtkCollection(), vtkCollection()
    view = simple.GetActiveView()
    simple.Render(view)

    view.SelectSurfaceCells(
        area,
        selected_reps,
        selection_sources,
        0,
    )

    selection._collectSelectionPorts(
        selected_reps, selection_sources, False, Modifier=None
    )
    simple.Render(view)

    nb_sources = selection_sources.GetNumberOfItems()
    for i in range(nb_sources):
        rep = selected_reps.GetItemAsObject(i)
        source = simple.servermanager._getPyProxy(rep.GetProperty("Input").GetProxy(0))
        extract_selection_filter.Selection = simple.servermanager._getPyProxy(
            source.GetSelectionInput(0)
        )

        # Crash ParaView sometime
        # if source != self._extract_selection.Input:
        #     print("clear selection")
        #     # simple.ClearSelection(self._extract_selection.Input)
        #     self._extract_selection.Input = source

        extract_selection_filter.UpdatePipeline()
        ds = simple.FetchData(extract_selection_filter)[0]

        if ds.GetNumberOfPoints() > 0:
            pd = ds.GetCellData()
            n = pd.GetNumberOfArrays()
            for j in range(n):
                array = pd.GetAbstractArray(j)
                extract_info[array.GetName()] = array.GetTuple(0)

    return extract_info


@TrameApp()
class HoverPoint(v3.VCard):
    def __init__(self, mode="points"):
        super().__init__(
            v_show=("enable_point_hover", False),
            classes="position-absolute",
            style=(
                "`left: calc(${html_view_space?.left + remote_view_mouse?.x || 0}px + 1rem); top: calc(${html_view_space?.top + html_view_space?.height - remote_view_mouse?.y||0}px + 1rem);`",
            ),
        )

        self.state.hover_data = {}
        self.state.hover_mode = mode
        self._extract_selection = None

        with self:
            with v3.VTable(density="compact"):
                with html.Tbody():
                    with html.Tr(v_for="v, k in hover_data", key="k"):
                        html.Td("{{ k }}")
                        html.Td("{{ v }}")

    def enable_points_selection(self):
        self.state.hover_mode = "points"

    def enable_cells_selection(self):
        self.state.hover_mode = "cells"

    @change("enable_point_hover")
    def on_activation_change(self, enable_point_hover, enable_picking, **_):
        if enable_point_hover:
            active_source = simple.GetActiveSource()
            if active_source is None and self._extract_selection is None:
                self.state.enable_picking = False
                self.state.enable_point_hover = False
            else:
                if self._extract_selection is None:
                    prev_active_source = simple.GetActiveSource()
                    self._extract_selection = simple.ExtractSelection()
                    if self.server.controller.register_internal_proxy.exists():
                        self.server.controller.register_internal_proxy(
                            self._extract_selection
                        )
                    simple.SetActiveSource(prev_active_source)
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
            prev_active_source = simple.GetActiveSource()
            self._extract_selection = simple.ExtractSelection()
            if self.server.controller.register_internal_proxy.exists():
                self.server.controller.register_internal_proxy(self._extract_selection)
            simple.SetActiveSource(prev_active_source)

    @change("remote_view_mouse")
    def on_hover(self, enable_point_hover, remote_view_mouse, **_):
        if not enable_point_hover:
            return

        if simple.GetActiveSource() is None:
            return

        if self._extract_selection is None:
            prev_active_source = simple.GetActiveSource()
            self._extract_selection = simple.ExtractSelection()
            if self.server.controller.register_internal_proxy.exists():
                self.server.controller.register_internal_proxy(self._extract_selection)
            simple.SetActiveSource(prev_active_source)

        x, y = remote_view_mouse.get("x"), remote_view_mouse.get("y")
        x_max, y_max = int(x + 0.5), int(y + 0.5)
        area = [int(x), int(y), x_max, y_max]

        if self.state.hover_mode == "points":
            self.state.hover_data = select_points_on_surface(
                area, self._extract_selection
            )
        else:
            self.state.hover_data = select_cells_on_surface(
                area, self._extract_selection
            )

        self.ctrl.view_update()
