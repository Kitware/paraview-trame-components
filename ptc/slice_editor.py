from dataclasses import dataclass
import numpy as np
from paraview import simple
from typing import Callable
import vtk

from trame.widgets import html
from trame.widgets import vuetify3 as vuetify
from trame_server.utils.typed_state import TypedState


@dataclass
class VectorState:
    x: float
    y: float
    z: float


class VectorEditor(html.Div):
    def __init__(
        self,
        namespace: str,
        initial_value: tuple[float, float, float] = [0.0, 0.0, 0.0],
        normalized: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._typed_state = TypedState(self.state, VectorState, namespace=namespace)
        self.data.x = initial_value[0]
        self.data.y = initial_value[1]
        self.data.z = initial_value[2]

        rules = [
            f"() => ({self.name.x} != null && {self.name.y} != null && {self.name.z} != null) ? true : 'Components must not be null'",
        ]
        if normalized:
            min_norm = 1e-6
            rules.append(
                f"() => (({self.name.x} ** 2 + {self.name.y} ** 2 + {self.name.z} ** 2) ** (1 / 2) < {min_norm}) ? 'Norm must be > {min_norm}' : true"
            )

        with (
            self,
            vuetify.VInput(
                model_value=(f"[{self.name.x}, {self.name.y}, {self.name.z}]",),
                rules=(f"[{','.join(rules)}]",),
                hide_details="auto",
            ),
        ):
            for name in [self.name.x, self.name.y, self.name.z]:
                vuetify.VNumberInput(
                    v_model=name,
                    control_variant="stacked",
                    min_fraction_digits=0,
                    precision=5,
                    density="compact",
                    style="margin-left: 4px; margin-right: 4px;",
                    step=(0.1,),
                    hide_details="true",
                )

    @property
    def name(self) -> VectorState:
        return self._typed_state.name

    @property
    def data(self) -> VectorState:
        return self._typed_state.data

    def on_change(self, f: Callable):
        self._typed_state.bind_changes(
            {
                self.name.x: f,
                self.name.y: f,
                self.name.z: f,
            }
        )

    @property
    def value(self) -> tuple[float, float, float]:
        return [
            self.data.x,
            self.data.y,
            self.data.z,
        ]

    @value.setter
    def value(self, value: tuple[float, float, float]) -> None:
        self.data.x = value[0]
        self.data.y = value[1]
        self.data.z = value[2]


class SliceEditor(html.Div):
    def __init__(self):
        super().__init__()

        self.slice = simple.Slice()
        self.state.show_slice = False
        self.state.change("show_slice")(self._show_slice)
        self.plane_representation = vtk.vtkImplicitPlaneRepresentation()
        self.plane_representation.DrawPlaneOff()

        self._build_ui()
        self.plane_representation.normal = self.normal_editor.value

    def _build_ui(self):
        with self, vuetify.VCard(title="Slice Editor", outlined=True):
            vuetify.VCheckbox(
                v_model="show_slice",
                label="Show slice",
                hide_details=True,
                style="margin-left: 10px; margin-top: -10px; margin-bottom: -10px;",
            )
            html.Span("Origin", style="font-size: 18px; margin-left: 14px;")
            self.origin_editor = VectorEditor(
                "origin", style="margin-top: 10px; margin-left: 14px;"
            )
            self.origin_editor.on_change(self._on_origin_change)
            with vuetify.VRow(
                style="margin: 10px; margin-left: 14px; align-items: center;"
            ):
                html.Span("Normal", style="font-size: 18px;")
                vuetify.VSpacer()
                with (
                    vuetify.VTooltip("Normal to X", location="bottom"),
                    vuetify.Template(v_slot_activator="{ props }"),
                ):
                    vuetify.VBtn(
                        "X",
                        click=self._normal_to_x,
                        style="margin: 4px;",
                        density="comfortable",
                        v_bind="props",
                    )
                with (
                    vuetify.VTooltip("Normal to Y", location="bottom"),
                    vuetify.Template(v_slot_activator="{ props }"),
                ):
                    vuetify.VBtn(
                        "Y",
                        click=self._normal_to_y,
                        style="margin: 4px;",
                        density="comfortable",
                        v_bind="props",
                    )
                with (
                    vuetify.VTooltip("Normal to Z", location="bottom"),
                    vuetify.Template(v_slot_activator="{ props }"),
                ):
                    vuetify.VBtn(
                        "Z",
                        click=self._normal_to_z,
                        style="margin: 4px;",
                        density="comfortable",
                        v_bind="props",
                    )
                with (
                    vuetify.VTooltip("Normal to camera", location="bottom"),
                    vuetify.Template(v_slot_activator="{ props }"),
                    vuetify.VBtn(
                        click=self._normal_to_camera,
                        style="margin: 4px;",
                        density="comfortable",
                        v_bind="props",
                    ),
                ):
                    vuetify.VIcon("mdi-camera")
            self.normal_editor = VectorEditor(
                "normal",
                [1.0, 0.0, 0.0],
                True,
                style="margin-bottom: 10px; margin-left: 14px;",
            )
            self.normal_editor.on_change(self._on_normal_change)

    def set_source(self, source):
        self.slice.Input = source
        self._show_slice(self.state.show_slice)

        view = simple.GetActiveView()
        ren_win = view.GetRenderWindow()
        iren = ren_win.GetInteractor()
        bounds = source.GetDataInformation().GetBounds()
        edge_sizes = [(bounds[i + 1] - bounds[i]) for i in range(0, len(bounds), 2)]
        self.plane_representation.place_factor = (
            np.sqrt(sum(edge_size**2 for edge_size in edge_sizes)) / 20
        )
        self.plane_representation.PlaceWidget(bounds)
        self.plane_widget = vtk.vtkImplicitPlaneWidget2(
            representation=self.plane_representation, interactor=iren
        )
        self.plane_widget.AddObserver(
            vtk.vtkCommand.InteractionEvent, self._on_plane_interaction
        )
        self.plane = self.plane_widget.GetRepresentation()
        simple.Render()
        self.plane_widget.On()

    def _on_plane_interaction(self, _caller, _event):
        self.origin_editor.value = self.plane.GetOrigin()
        self.normal_editor.value = self.plane.GetNormal()
        self.state.flush()

    def _show_slice(self, show_slice: bool, **kwargs):
        if show_slice:
            simple.Show(self.slice)
        else:
            simple.Hide(self.slice)
        self.ctrl.view_update()

    def _on_origin_change(self, *_args, **_kwargs):
        origin = self.origin_editor.value
        if any(not isinstance(v, float) for v in origin):
            return
        self.slice.SliceType.Origin = origin

        self.plane.SetOrigin(origin)
        self.ctrl.view_update()

    def _on_normal_change(self, *_args, **_kwargs):
        normal = self.normal_editor.value
        if (
            any(not isinstance(v, float) for v in normal)
            or np.linalg.norm(normal) < 1e-6
        ):
            return

        self.slice.SliceType.Normal = normal

        self.plane.SetNormal(normal)
        self.ctrl.view_update()

    def _normal_to_x(self):
        self.normal_editor.value = [1.0, 0.0, 0.0]

    def _normal_to_y(self):
        self.normal_editor.value = [0.0, 1.0, 0.0]

    def _normal_to_z(self):
        self.normal_editor.value = [0.0, 0.0, 1.0]

    def _normal_to_camera(self):
        self.normal_editor.value = [
            -val for val in simple.GetActiveCamera().GetViewPlaneNormal()
        ]
