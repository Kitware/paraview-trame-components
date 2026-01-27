import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable

from paraview import simple

from trame.widgets import vuetify3 as v3
from trame_server.controller import FunctionNotImplementedError
from trame_server.utils.typed_state import TypedState

logger = logging.getLogger(__name__)


@dataclass
class AxisComponent:
    value: float = 0.0
    precision: int = 0
    visibility: bool = True
    control_variant: str = "hidden"
    on_focus_lost_callback_name: str = ""


@dataclass
class Transform:
    x: AxisComponent = field(default_factory=AxisComponent)
    y: AxisComponent = field(default_factory=AxisComponent)
    z: AxisComponent = field(default_factory=AxisComponent)

    ui_visibility: bool = True


@dataclass
class TransformEditorState:
    translation: Transform = field(default_factory=Transform)
    scale: Transform = field(default_factory=Transform)
    orientation: Transform = field(default_factory=Transform)
    origin: Transform = field(default_factory=Transform)

    apply_button_visibility: bool = True


class AxisComponentCol(v3.VCol):
    def __init__(self, inner_state: TypedState[AxisComponent], **kwargs) -> None:
        super().__init__(classes="pa-0", v_if=(inner_state.name.visibility,), **kwargs)

        with self:
            v3.VNumberInput(
                classes="pa-1",
                v_model=(inner_state.name.value,),
                control_variant=(inner_state.name.control_variant,),
                precision=(inner_state.name.precision,),
                update_focused=(
                    self.on_focus,
                    f"[$event, {inner_state.name.on_focus_lost_callback_name}]",
                ),
            )

    def on_focus(self, focus: bool, on_focus_lost_callback_name: str) -> None:
        if focus or not on_focus_lost_callback_name:
            return
        try:
            self.server.controller[on_focus_lost_callback_name]()
        except FunctionNotImplementedError:
            logger.warning(f"{on_focus_lost_callback_name} is not implemented")


class TransformEditorRow(v3.VRow):
    def __init__(self, label: str, inner_state: TypedState[Transform]) -> None:
        super().__init__(
            max_width="100%",
            align_content="center",
            v_if=(inner_state.name.ui_visibility,),
        )
        with self:
            v3.VCol(label, classes="pa-0", cols=3)

            AxisComponentCol(inner_state=inner_state.get_sub_state(inner_state.name.x))
            AxisComponentCol(inner_state=inner_state.get_sub_state(inner_state.name.y))
            AxisComponentCol(inner_state=inner_state.get_sub_state(inner_state.name.z))


def _convert_transform_to_list(transform: Transform) -> list[float]:
    return (
        [transform.x.value, transform.y.value, transform.z.value] if transform else []
    )


class TransformEditor(v3.VCard):
    def __init__(
        self,
        show_translation: bool = True,
        show_scale: bool = True,
        show_orientation: bool = True,
        show_origin: bool = True,
        show_apply_button: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(width="100%", **kwargs)

        # Initialize component state
        self.typed_state = TypedState(self.state, TransformEditorState)

        self.typed_state.data.scale.x.value = 1.0
        self.typed_state.data.scale.y.value = 1.0
        self.typed_state.data.scale.z.value = 1.0

        self.typed_state.data.translation.ui_visibility = show_translation
        self.typed_state.data.scale.ui_visibility = show_scale
        self.typed_state.data.orientation.ui_visibility = show_orientation
        self.typed_state.data.origin.ui_visibility = show_origin

        self.typed_state.data.apply_button_visibility = show_apply_button

        self._build_ui()

    def _build_ui(self) -> None:
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
            with v3.VCardActions(v_if=(self.typed_state.name.apply_button_visibility,)):
                v3.VSpacer()
                v3.VBtn("Apply", click=self.apply_changes)

    @property
    def source_proxy(self) -> Any:
        return simple.GetActiveSource()

    @property
    def view_proxy(self) -> Any:
        return simple.GetActiveView()

    @property
    def scale_name(self) -> Transform:
        return self.typed_state.name.scale

    @property
    def translation_name(self) -> Transform:
        return self.typed_state.name.translation

    @property
    def orientation_name(self) -> Transform:
        return self.typed_state.name.orientation

    @property
    def origin_name(self) -> Transform:
        return self.typed_state.name.origin

    def _get_display_properties(self) -> Any:
        """
        Get ParaView display properties.
        :return: paraview.servermanager.GeometryRepresentation object
        """
        if self.source_proxy is None or self.view_proxy is None:
            logger.warning(
                "Cannot compute display properties. Missing source proxy or view proxy."
            )
            return None
        return simple.GetDisplayProperties(self.source_proxy, view=self.view_proxy)

    def apply_changes(self) -> None:
        self.apply_translation()
        self.apply_origin()
        self.apply_orientation()
        self.apply_scale()

        simple.ResetCamera()
        self.ctrl.view_update()

        try:
            self.server.controller.on_apply_clicked()
        except FunctionNotImplementedError:
            logger.warning("on_apply_clicked is not implemented")

    def apply_translation(self) -> None:
        translation = _convert_transform_to_list(self.typed_state.data.translation)
        display_properties = self._get_display_properties()
        if display_properties is None:
            return

        display_properties.Translation = translation
        display_properties.PolarAxes.Translation = translation

    def apply_orientation(self) -> None:
        orientation = _convert_transform_to_list(self.typed_state.data.orientation)
        display_properties = self._get_display_properties()
        if display_properties is None:
            return

        display_properties.Orientation = orientation
        display_properties.PolarAxes.Orientation = orientation

    def apply_origin(self) -> None:
        origin = _convert_transform_to_list(self.typed_state.data.origin)
        display_properties = self._get_display_properties()
        if display_properties is None:
            return

        display_properties.Origin = origin

    def apply_scale(self) -> None:
        scale = _convert_transform_to_list(self.typed_state.data.scale)
        display_properties = self._get_display_properties()
        if display_properties is None:
            return

        display_properties.Scale = scale
        display_properties.DataAxesGrid.Scale = scale
        display_properties.PolarAxes.Scale = scale

    def set_components_visibilities(
        self, visibilities: dict[AxisComponent, bool]
    ) -> None:
        for component, visibility in visibilities.items():
            self.state[component.visibility] = visibility

    def set_components_controls_variants(
        self, controls_variants: dict[AxisComponent, str]
    ) -> None:
        for component, control_variant in controls_variants.items():
            self.state[component.control_variant] = control_variant

    def _bind_ctrl_method(self, ctrl_key_name: str, ctrl_method: Callable) -> None:
        self.ctrl[ctrl_key_name] = ctrl_method

    def bind_components_on_focus_lost(
        self, on_focus_lost_callbacks: dict[AxisComponent, Callable]
    ) -> None:
        for component, callable_method in on_focus_lost_callbacks.items():
            state_var_name = component.on_focus_lost_callback_name
            callable_id = (
                self.state[state_var_name] if self.state[state_var_name] else None
            )
            if callable_id is None:
                callable_id = uuid.uuid4().hex.upper()[0:9]
            self.state[state_var_name] = callable_id
            self._bind_ctrl_method(callable_id, callable_method)

    def bind_on_apply_button_clicked(self, on_apply_clicked: Callable) -> None:
        self._bind_ctrl_method("on_apply_clicked", on_apply_clicked)
