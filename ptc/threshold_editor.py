from dataclasses import dataclass, field
from paraview import simple

from trame.widgets import html, vuetify3 as vuetify
from trame_server.utils.typed_state import TypedState


@dataclass
class ThresholdState:
    available_arrays: list[str] = field(default_factory=list)
    selected_name: str | None = None
    available_components: list[str] = field(default_factory=list)
    selected_name_has_components: bool = False
    selected_component: str | None = None
    range: tuple[float, float] = field(default_factory=lambda: [0, 0])
    lower: float = 0.0
    upper: float = 0.0


class ThresholdEditor(html.Div):
    def __init__(self):
        super().__init__()

        self._typed_state = TypedState(self.state, ThresholdState)
        self._typed_state.bind_changes(
            {
                self.name.lower: self._on_lower_threshold_change,
                self.name.upper: self._on_upper_threshold_change,
                self.name.selected_name: self._on_selected_scalar_change,
                self.name.selected_component: self._on_selected_component_change,
            }
        )

        self.ranges = {}

        self.source = None
        self.pv_filter = simple.Threshold()

        self._build_ui()

    @property
    def name(self) -> ThresholdState:
        return self._typed_state.name

    @property
    def data(self) -> ThresholdState:
        return self._typed_state.data

    def _build_ui(self) -> None:
        with self, vuetify.VCard(title="Threshold"):
            with vuetify.VRow(style="margin: 5px;"):
                vuetify.VSelect(
                    v_model=self.name.selected_name,
                    items=(self.name.available_arrays,),
                    hide_details=True,
                    label="Array",
                    density="comfortable",
                    style="margin-right: 5px; flex: 1;",
                )
                vuetify.VSelect(
                    v_model=self.name.selected_component,
                    items=(self.name.available_components,),
                    disabled=(f"!{self.name.selected_name_has_components}",),
                    hide_details=True,
                    label="Component",
                    density="comfortable",
                    style="margin-left: 5px; flex: 1;",
                )
            with vuetify.VRow(style="margin: 5px;"):
                vuetify.VNumberInput(
                    v_model=self.name.lower,
                    precision=5,
                    min_fraction_digits=0,
                    hide_details=True,
                    control_variant="hidden",
                    density="compact",
                    label="Lower",
                    style="margin-right: 10px;",
                    min=(f"{self.name.range}[0]",),
                    max=(self.name.upper,),
                )
                vuetify.VRangeSlider(
                    model_value=(f"[{self.name.lower}, {self.name.upper}]",),
                    update_modelValue=f"{self.name.lower} = $event[0]; {self.name.upper} = $event[1];",
                    min=(f"{self.name.range}[0]",),
                    max=(f"{self.name.range}[1]",),
                    hide_details=True,
                    style="flex: 4;",
                )
                vuetify.VNumberInput(
                    v_model=self.name.upper,
                    precision=5,
                    min_fraction_digits=0,
                    hide_details=True,
                    control_variant="hidden",
                    density="compact",
                    label="Upper",
                    style="margin-left: 10px;",
                    min=(self.name.lower,),
                    max=(f"{self.name.range}[1]",),
                )

    def set_source(self, source) -> None:
        self.source = source
        self.pv_filter.Input = source
        simple.Hide(self.source)
        simple.Show(self.pv_filter)

        available_arrays = []
        for array in [*source.PointData, *source.CellData]:
            name = array.Name
            nb_components = array.GetNumberOfComponents()
            available_arrays.append(name)
            self.ranges[name] = {"Magnitude": array.GetComponentRange(-1)}
            if nb_components > 1:
                for i in range(nb_components):
                    self.ranges[name][array.GetComponentName(i)] = (
                        array.GetComponentRange(i)
                    )
        self.data.available_arrays = available_arrays

    def _on_lower_threshold_change(self, lower: float) -> None:
        self.pv_filter.LowerThreshold = lower
        simple.Render()
        self.ctrl.view_update()

    def _on_upper_threshold_change(self, upper: float) -> None:
        self.pv_filter.UpperThreshold = upper
        simple.Render()
        self.ctrl.view_update()

    def _reset_range(self) -> None:
        name = self.data.selected_name
        ranges = self.ranges[name]
        if len(ranges) > 1:
            lower, upper = ranges[self.data.selected_component]
        else:
            lower, upper = ranges["Magnitude"]
        self.data.lower = lower
        self.data.upper = upper
        self.data.range = [lower, upper]

    def _on_selected_scalar_change(self, name: str | None) -> None:
        if name is None:
            return
        ranges = self.ranges[name]
        if len(ranges) > 1:
            self.data.selected_name_has_components = True
            components_names = list(ranges.keys())
            self.data.available_components = components_names
            self.data.selected_component = components_names[0]
        else:
            self.data.selected_name_has_components = False
        self._reset_range()
        self.pv_filter.Scalars = name
        simple.Render()
        self.ctrl.view_update()

    def _on_selected_component_change(self, name: str | None) -> None:
        if name is None:
            return
        self._reset_range()
        self.pv_filter.SelectedComponent = name
        simple.Render()
        self.ctrl.view_update()
