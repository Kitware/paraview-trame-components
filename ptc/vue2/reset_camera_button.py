from trame.widgets import vuetify2 as v2
from paraview import simple
from typing import Literal


class ResetCameraButtons(v2.VBtnToggle):
    """
    A widget composed of 4 buttons to reset the camera of a view :
    - The first is used to reset the camera to see the entire object.
    - The second places the camera at -x from the object and look in the x direction.
    - The third places the camera at -y from the object and look in the y direction.
    - The fourth places the camera at -z from the object and look in the z direction.
    """

    def __init__(
        self,
        style: str | None = None,
        classes: str | None = None,
        show_reset_camera: bool = True,
        show_reset_camera_x: bool = True,
        show_reset_camera_y: bool = True,
        show_reset_camera_z: bool = True,
        show_interaction_mode: bool = True,
        **kwargs,
    ) -> None:
        if style is None:
            style = "top: 0.5rem; left: 0.5rem; background-color: white;"
        if classes is None:
            classes = "position-absolute"
        super().__init__(
            style=style,
            classes=classes,
            **kwargs,
        )

        self.state.setdefault("interaction_mode", "3D")
        self.state.setdefault("show_interaction_mode", show_interaction_mode)

        def reset_camera_callback() -> None:
            self.ctrl.view_reset_camera()

        def reset_to_positive_x() -> None:
            self.view.ResetActiveCameraToPositiveX()
            self.ctrl.view_reset_camera()

        def reset_to_positive_y() -> None:
            self.view.ResetActiveCameraToPositiveY()
            self.ctrl.view_reset_camera()

        def reset_to_positive_z() -> None:
            self.view.ResetActiveCameraToPositiveZ()
            self.ctrl.view_reset_camera()

        def change_interaction_mode(mode: Literal["2D", "3D"]) -> None:
            self.view.InteractionMode = mode
            self.state.interaction_mode = mode
            self.ctrl.view_update()

        with self:
            with (
                v2.VTooltip("Change interaction mode", location="bottom"),
                v2.Template(v_slot_activator=("{ props }",)),
            ):
                with v2.VBtn(
                    v_bind=("props",),
                    click=(change_interaction_mode, "['3D']"),
                    v_show=("interaction_mode === '2D'"),
                    v_if=("show_interaction_mode", show_interaction_mode),
                ):
                    v2.VIcon("mdi-video-2d")

            with (
                v2.VTooltip("Change interaction mode", location="bottom"),
                v2.Template(v_slot_activator=("{ props }",)),
            ):
                with v2.VBtn(
                    v_bind=("props",),
                    click=(change_interaction_mode, "['2D']"),
                    v_show=("interaction_mode === '3D'"),
                    v_if=("show_interaction_mode",),
                ):
                    v2.VIcon("mdi-video-3d")

            with (
                v2.VTooltip(
                    "Reset Camera",
                    location="bottom",
                ),
                v2.Template(v_slot_activator=("{ props }",)),
            ):
                with v2.VBtn(
                    v_bind=("props",),
                    click=reset_camera_callback,
                    v_if=("show_reset_camera", show_reset_camera),
                ):
                    v2.VIcon("mdi-crop-free")

            with (
                v2.VTooltip(
                    "Set view direction to +X",
                    location="bottom",
                ),
                v2.Template(v_slot_activator=("{ props }",)),
            ):
                with v2.VBtn(
                    v_bind=("props",),
                    click=reset_to_positive_x,
                    v_if=("show_reset_camera_x", show_reset_camera_x),
                ):
                    v2.VIcon("mdi-axis-x-arrow")

            with (
                v2.VTooltip(
                    "Set view direction to +Y",
                    location="bottom",
                ),
                v2.Template(v_slot_activator=("{ props }",)),
            ):
                with v2.VBtn(
                    v_bind=("props",),
                    click=reset_to_positive_y,
                    v_if=("show_reset_camera_y", show_reset_camera_y),
                ):
                    v2.VIcon("mdi-axis-y-arrow")

            with (
                v2.VTooltip(
                    "Set view direction to +Z",
                    location="bottom",
                ),
                v2.Template(v_slot_activator=("{ props }",)),
            ):
                with v2.VBtn(
                    v_bind=("props",),
                    click=reset_to_positive_z,
                    v_if=("show_reset_camera_z", show_reset_camera_z),
                ):
                    v2.VIcon("mdi-axis-z-arrow")

    @property
    def view(self):
        return simple.GetActiveView()
