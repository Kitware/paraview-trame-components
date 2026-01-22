from paraview import simple
from typing import Any, Literal

from trame.decorators import change
from trame.widgets import color_opacity_editor, html
from trame.widgets import vuetify3 as vuetify

ColorOpacityEditorColors = list[list[float, list[float, float, float]]]
PVColors = list[float]

ColorOpacityEditorOpacities = list[list[float, float]]
PVOpacities = list[float]


class ColorOpacityEditorConvertor:
    """
    Data conversion handler for the ColorEditor component.

    In ParaView:
      - points of the ColorTransferFunction (ctf) are defined like:
    [scalar_value_0, r_0, g_0, b_0, ..., scalar_value_N, r_N, g_N, b_N]
      - point of the OpacityTransferFunction (otf) are defined like:
    [scalar_value_0, opacity_0, 0.5, 0, ..., scalar_value_N, opacity_N, 0.5, 0]

    trame-color-editor defines its colors and opacity like:
      - colors:
    [[scalar_0, [r_0, g_0, b_0]], ..., [scalar_N, [r_N, g_N, b_N]]]
      - opacities:
    [[scalar_0, opacity_0], ..., [scalar_N, opacity_N]]
    """

    @staticmethod
    def convert_pv_ctf_to_colors(pv_ctf_points: PVColors) -> ColorOpacityEditorColors:
        colors = []
        for i in range(0, len(pv_ctf_points), 4):
            colors.append(
                [
                    pv_ctf_points[i],
                    [pv_ctf_points[i + 1], pv_ctf_points[i + 2], pv_ctf_points[i + 3]],
                ]
            )

        return colors

    @staticmethod
    def convert_colors_to_pv_ctf_points(colors: ColorOpacityEditorColors) -> PVColors:
        points = []
        for color in colors:
            points.append(color[0])
            points.append(color[1][0])
            points.append(color[1][1])
            points.append(color[1][2])

        return points

    @staticmethod
    def convert_pv_otf_to_opacities(
        pv_otf_points: PVOpacities,
    ) -> ColorOpacityEditorOpacities:
        opacities = []
        for i in range(0, len(pv_otf_points), 4):
            opacities.append(
                [
                    pv_otf_points[i],
                    pv_otf_points[i + 1],
                ]
            )
        return opacities

    @staticmethod
    def convert_opacities_to_pv_otf_points(
        opacities: ColorOpacityEditorOpacities,
    ) -> PVOpacities:
        points = []
        for opacity in opacities:
            points.append(opacity[0])
            points.append(opacity[1])
            points.append(0.5)
            points.append(0)
        return points

    @staticmethod
    def convert_hex_to_rgb(hex_value: str) -> tuple:
        return tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def convert_rgb_to_hex(r: int, g: int, b: int) -> str:
        return "#{:02X}{:02X}{:02X}".format(r, g, b)


class ColorPicker(vuetify.VMenu):
    def __init__(self, state_var_name, **kwargs) -> None:
        super().__init__(close_on_content_click=False, **kwargs)

        with self:
            with vuetify.Template(v_slot_activator="{ props }"):
                with vuetify.VBtn(
                    "Nan Color",
                    v_bind="props",
                    elevation=0,
                    classes="justify-start",
                    block=True,
                ):
                    with vuetify.Template(v_slot_prepend=True):
                        vuetify.VIcon(
                            "mdi-circle",
                            color=(f"{state_var_name}",),
                        )
            vuetify.VColorPicker(
                v_model=(f"{state_var_name}",),
                modes=("['rgb']",),
                classes="w-100",
                divided=True,
                landscape=True,
                max_width=250,
            )


class ColorOpacityEditor(html.Div):
    def __init__(self):
        super().__init__()

        self.state.table_colors = []
        self.state.table_opacities = []

        self.state.setdefault("preset_name", "Fast")
        self.state.setdefault(
            "presets_names", sorted(simple.ListColorPresetNames(), key=str.casefold)
        )
        self.state.setdefault("nan_color", "#FF0000")
        self.update_scalar_range()

        self.build_content()

    @property
    def source_proxy(self) -> Any:
        return simple.GetActiveSource()

    @property
    def view_proxy(self) -> Any:
        return simple.GetActiveView()

    def update_scalar_range(self) -> None:
        if self.source_proxy is None:
            self.state.scalar_range = [0, 0]
            return

        # Update scalar_range, opacities, and colors
        [field_type, array_name] = self.get_representation_color_array_name()

        if not field_type or not array_name:
            self.state.scalar_range = [0, 0]
            return

        source_information = self.source_proxy.GetDataInformation().DataInformation
        if source_information is None:
            self.state.scalar_range = [0, 0]
            return

        data_information = None
        if field_type == "POINTS":
            data_information = source_information.GetPointDataInformation()
        if field_type == "CELLS":
            data_information = source_information.GetCellDataInformation()

        if data_information is None:
            self.state.scalar_range = [0, 0]
            return

        array_info = data_information.GetArrayInformation(array_name)
        lut = simple.GetColorTransferFunction(array_name)
        array_range = array_info.GetComponentRange(lut.VectorComponent)

        self.state.scalar_range = [array_range[0], array_range[1]]

    def make_linear_nodes(
        self, values: list[float, float], values_range: list[float, float]
    ) -> ColorOpacityEditorOpacities:
        span = values_range[1] - values_range[0]
        dx = span / max(len(values) - 1, 1)
        nodes = []

        for i, value in enumerate(values):
            nodes.append([values_range[0] + i * dx, value])
        return nodes

    def build_color_editor_table(self) -> None:
        with vuetify.VTable(
            density="compact",
            height="300px",
            classes="overflow-auto",
            style="width:100%",
        ):
            with html.Tbody(v_for="(color, index) in table_colors"):
                with html.Td(classes="pa-1"):
                    vuetify.VNumberInput(
                        model_value=("color[0]",),
                        update_modelValue="color[0] = $event; flushState('table_colors');",
                        update_focused=(
                            self.on_table_values_focus_changed,
                            "[$event, 'colors', index, 0]",
                        ),
                        label="Scalar",
                        variant="outlined",
                        control_variant="hidden",
                        min=("scalar_range[0]",),
                        max=("scalar_range[1]",),
                        precision=(16,),
                    )
                with html.Td(
                    classes="pa-1", v_for="(component, channelId) in ['R', 'G', 'B']"
                ):
                    vuetify.VNumberInput(
                        model_value=("color[1][channelId]",),
                        update_modelValue="color[1][channelId] = $event; flushState('table_colors');",
                        update_focused=(
                            self.on_table_values_focus_changed,
                            "[$event, 'colors', index, 1, channelId]",
                        ),
                        variant="outlined",
                        label=("component",),
                        control_variant="hidden",
                        precision=(5,),
                    )

    def build_opacity_editor_table(self) -> None:
        with vuetify.VTable(
            density="compact",
            height="300px",
            classes="overflow-auto",
            style="width:100%",
        ):
            with html.Tr(v_for="(opacity, index) in table_opacities"):
                with html.Td(classes="pa-1"):
                    vuetify.VNumberInput(
                        model_value=("opacity[0]",),
                        update_modelValue="opacity[0] = $event; flushState('table_opacities');",
                        update_focused=(
                            self.on_table_values_focus_changed,
                            "[$event, 'opacities', index, 0]",
                        ),
                        label="Scalar",
                        variant="outlined",
                        control_variant="hidden",
                        precision=(16,),
                        min=("scalar_range[0]",),
                        max=("scalar_range[1]",),
                    )
                with html.Td(classes="pa-1"):
                    vuetify.VNumberInput(
                        label="Opacity",
                        variant="outlined",
                        control_variant="hidden",
                        model_value=("opacity[1]",),
                        precision=(5,),
                        update_modelValue="opacity[1] = $event; flushState('table_opacities');",
                        update_focused=(
                            self.on_table_values_focus_changed,
                            "[$event,'opacities',  index, 1]",
                        ),
                        min=0,
                        max=1,
                    )

    def build_content(self) -> None:
        with self:
            vuetify.VSelect(
                label="Select preset",
                v_model=("preset_name",),
                items=("presets_names",),
            )

            color_opacity_editor.ColorOpacityEditor(
                style="width: 100%; height: 15rem; padding: 0.5rem;",
                v_model_colorNodes=("colors", []),
                v_model_opacityNodes=(
                    "opacities",
                    self.make_linear_nodes([0, 1], [0, 1]),
                ),
                scalar_range=("scalar_range", [0, 0]),
                background_shape=("background_shape", "opacity"),
                background_opacity=("background_opacity", True),
                handle_radius=7,
                line_width=2,
                viewport_padding=("viewport_padding", [8, 8]),
                handle_color=("handle_color", [0.125, 0.125, 0.125, 1]),
                handle_border_color=("handle_border_color", [0.75, 0.75, 0.75, 1]),
                histograms=("histograms", []),
                histograms_range=("histograms_range", []),
                show_histograms=("show_histograms", False),
                histograms_color=("histograms_color", [0, 0, 0, 0.25]),
            )

            ColorPicker(
                state_var_name="nan_color",
            )

            with vuetify.VExpansionPanels(
                v_model=("opened_panels", [0, 1]),
                multiple=True,
                elevation=0,
            ):
                with vuetify.VExpansionPanel():
                    vuetify.VExpansionPanelTitle("Color transfer function")
                    vuetify.VDivider()
                    with vuetify.VExpansionPanelText():
                        self.build_color_editor_table()
                with vuetify.VExpansionPanel():
                    vuetify.VExpansionPanelTitle("Opacity transfer function")
                    vuetify.VDivider()
                    with vuetify.VExpansionPanelText():
                        self.build_opacity_editor_table()

    def update_colors(self, pv_ctf_points: PVColors) -> None:
        colors = ColorOpacityEditorConvertor.convert_pv_ctf_to_colors(pv_ctf_points)
        self.state.colors = colors

    def update_opacities(self, pv_otf_points: PVOpacities) -> None:
        self.state.opacities = ColorOpacityEditorConvertor.convert_pv_otf_to_opacities(
            pv_otf_points
        )

    @change("nan_color")
    def on_nan_color_changed(self, *args, **kwargs) -> None:
        if not self.state.nan_color:
            return
        [_, array_name] = self.get_representation_color_array_name()

        if not array_name:
            return

        lut = simple.GetColorTransferFunction(array_name)
        if not lut:
            return

        rgb_nan_color = ColorOpacityEditorConvertor.convert_hex_to_rgb(
            self.state.nan_color[1:]
        )
        lut.NanColor = [
            rgb_nan_color[0] / 255,
            rgb_nan_color[1] / 255,
            rgb_nan_color[2] / 255,
        ]

    @change("preset_name")
    def on_preset_name_changed(self, *args, **kwargs) -> None:
        [_, array_name] = self.get_representation_color_array_name()

        if not array_name:
            return

        lut = simple.GetColorTransferFunction(array_name)
        lut.ApplyPreset(self.state.preset_name, True)

        representation = simple.GetRepresentation(self.source_proxy, self.view_proxy)
        representation.RescaleTransferFunctionToDataRange(False, True)

        self.update_colors(lut.RGBPoints)

        otf = simple.GetOpacityTransferFunction(array_name)
        if otf is None:
            self.update_opacities(
                self.make_linear_nodes([0, 1], self.state.scalar_range)
            )
        else:
            self.update_opacities(otf.Points)

        # Update Nan color
        pv_nan_color = lut.NanColor
        self.state.nan_color = ColorOpacityEditorConvertor.convert_rgb_to_hex(
            max(0, min(int(pv_nan_color[0] * 255), 255)),
            max(0, min(int(pv_nan_color[1] * 255), 255)),
            max(0, min(int(pv_nan_color[2] * 255), 255)),
        )

    @change("colors")
    def on_colors_changed(self, *args, **kwargs) -> None:
        self.update_color_transfer_function()
        self.state.table_colors = self.state.colors

    @change("opacities")
    def on_opacities_changed(self, *args, **kwargs) -> None:
        self.update_opacity_transfer_function()
        self.state.table_opacities = self.state.opacities

    def get_representation_color_array_name(self) -> list[str, str]:
        representation = simple.GetRepresentation(self.source_proxy, self.view_proxy)
        if representation is None:
            return ["", ""]

        return representation.ColorArrayName

    def update_opacity_transfer_function(self) -> None:
        [_, array_name] = self.get_representation_color_array_name()

        if not array_name:
            return

        otf = simple.GetOpacityTransferFunction(array_name)
        if otf is None:
            return

        otf.Points = ColorOpacityEditorConvertor.convert_opacities_to_pv_otf_points(
            self.state.opacities
        )

        simple.Render()
        self.ctrl.view_update()

    def update_color_transfer_function(self) -> None:
        [_, array_name] = self.get_representation_color_array_name()

        if not array_name:
            return

        lut = simple.GetColorTransferFunction(array_name)
        if lut is None:
            return

        lut.RGBPoints = ColorOpacityEditorConvertor.convert_colors_to_pv_ctf_points(
            self.state.colors
        )

        simple.Render()
        self.ctrl.view_update()

    def on_table_values_focus_changed(
        self,
        focus: bool,
        array_name: Literal["colors", "opacities"],
        node_index: int,
        node_component_id: int,
        channel_index: int | None = None,
    ) -> None:
        if focus:
            return

        table_array_name = f"table_{array_name}"

        # Update values when focus is left
        def get_value(state_variable_name: str) -> Any:
            return (
                self.state[state_variable_name][node_index][node_component_id][
                    channel_index
                ]
                if channel_index is not None
                else self.state[state_variable_name][node_index][node_component_id]
            )

        old_value = get_value(array_name)
        new_value = get_value(table_array_name)

        if old_value != new_value:
            table_data = [*self.state[table_array_name]]
            # Sort table_data only if scalar value changed
            if node_component_id == 0:
                table_data.sort(key=lambda x: x[0])
            self.state[array_name] = table_data
