from dataclasses import dataclass, field

from paraview import simple

from trame.widgets import vuetify3 as v3
from trame_server.utils.typed_state import TypedState


@dataclass
class Transform:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    ui_visibility: bool = True


@dataclass
class TransformEditorState:
    translation: Transform = field(default_factory=Transform)
    scale: Transform = field(default_factory=Transform)
    orientation: Transform = field(default_factory=Transform)
    origin: Transform = field(default_factory=Transform)


class TransformEditorRow(v3.VRow):
    def __init__(self, label: str, inner_state: TypedState[Transform]):
        super().__init__(
            max_width="100%",
            align_content="center",
            v_if=(inner_state.name.ui_visibility,),
        )
        with self:
            v3.VCol(label, classes="pa-0")
            with v3.VCol(classes="pa-0"):
                v3.VNumberInput(
                    label="x",
                    v_model=(inner_state.name.x,),
                    control_variant="hidden",
                    precision=(5,),
                )
            with v3.VCol(classes="pa-0"):
                v3.VNumberInput(
                    label="y",
                    v_model=(inner_state.name.y,),
                    control_variant="hidden",
                    precision=(5,),
                )
            with v3.VCol(classes="pa-0"):
                v3.VNumberInput(
                    label="z",
                    v_model=(inner_state.name.z,),
                    control_variant="hidden",
                    precision=(5,),
                )


def _convert_transform_to_list(transform: Transform) -> list[float]:
    return [transform.x, transform.y, transform.z] if transform else []


class TransformEditor(v3.VCard):
    def __init__(
        self,
        show_translation: bool = True,
        show_scale: bool = True,
        show_orientation: bool = True,
        show_origin: bool = True,
        **kwargs,
    ):
        super().__init__(width="100%", **kwargs)

        # Initialize component state
        self.typed_state = TypedState(self.state, TransformEditorState)
        self.typed_state.data.translation.ui_visibility = show_translation

        self.typed_state.data.scale.ui_visibility = show_scale
        self.typed_state.data.scale.x = 1.0
        self.typed_state.data.scale.y = 1.0
        self.typed_state.data.scale.z = 1.0

        self.typed_state.data.orientation.ui_visibility = show_orientation
        self.typed_state.data.origin.ui_visibility = show_origin

        self._build_ui()

    def _build_ui(self):
        with self:
            with (
                v3.VCardText(classes="pb-0"),
                v3.VContainer(classes="pa-0"),
            ):
                TransformEditorRow(
                    label="Translation",
                    inner_state=self.typed_state.get_sub_state(
                        self.typed_state.name.translation
                    ),
                )
                TransformEditorRow(
                    label="Scale",
                    inner_state=self.typed_state.get_sub_state(
                        self.typed_state.name.scale
                    ),
                )
                TransformEditorRow(
                    label="Origin",
                    inner_state=self.typed_state.get_sub_state(
                        self.typed_state.name.origin
                    ),
                )
                TransformEditorRow(
                    label="Orientation",
                    inner_state=self.typed_state.get_sub_state(
                        self.typed_state.name.orientation
                    ),
                )

            with v3.VCardActions():
                v3.VSpacer()
                v3.VBtn("Apply", click=self.apply_changes)

    @property
    def source_proxy(self):
        return simple.GetActiveSource()

    @property
    def view_proxy(self):
        return simple.GetActiveView()

    def _get_display_properties(self):
        if self.source_proxy is None or self.view_proxy is None:
            print("Cannot compute display properties")
            return None
        return simple.GetDisplayProperties(self.source_proxy, view=self.view_proxy)

    def apply_changes(self):
        self.apply_translation(
            _convert_transform_to_list(self.typed_state.data.translation)
        )
        self.apply_origin(_convert_transform_to_list(self.typed_state.data.origin))
        self.apply_orientation(
            _convert_transform_to_list(self.typed_state.data.orientation)
        )
        self.apply_scale(_convert_transform_to_list(self.typed_state.data.scale))

        simple.ResetCamera()
        self.ctrl.view_update()

    def apply_translation(self, translation):
        display_properties = self._get_display_properties()
        if display_properties is None:
            return

        display_properties.Translation = translation
        display_properties.PolarAxes.Translation = translation

    def apply_orientation(self, orientation):
        display_properties = self._get_display_properties()
        if display_properties is None:
            return

        display_properties.Orientation = orientation
        display_properties.PolarAxes.Orientation = orientation

    def apply_origin(self, origin):
        display_properties = self._get_display_properties()
        if display_properties is None:
            return

        display_properties.Origin = origin

    def apply_scale(self, scale):
        display_properties = self._get_display_properties()
        if display_properties is None:
            return

        display_properties.Scale = scale
        display_properties.DataAxesGrid.Scale = scale
        display_properties.PolarAxes.Scale = scale
