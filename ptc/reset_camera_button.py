from typing import Literal
from paraview import simple
from trame.widgets import vuetify3 as v3


class ResetCameraButtons(v3.VBtnGroup):
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
                v3.VTooltip("Change interaction mode", location="bottom"),
                v3.Template(v_slot_activator=("{ props }",)),
            ):
                v3.VBtn(
                    icon="mdi-video-2d",
                    v_bind=("props",),
                    click=(change_interaction_mode, "['3D']"),
                    v_show=("interaction_mode === '2D'"),
                    v_if=("show_interaction_mode", show_interaction_mode),
                )

            with (
                v3.VTooltip("Change interaction mode", location="bottom"),
                v3.Template(v_slot_activator=("{ props }",)),
            ):
                v3.VBtn(
                    icon="mdi-video-3d",
                    v_bind=("props",),
                    click=(change_interaction_mode, "['2D']"),
                    v_show=("interaction_mode === '3D'"),
                    v_if=("show_interaction_mode",),
                )

            with (
                v3.VTooltip(
                    "Reset Camera",
                    location="bottom",
                ),
                v3.Template(v_slot_activator=("{ props }",)),
            ):
                (
                    v3.VBtn(
                        icon="mdi-crop-free",
                        v_bind=("props",),
                        click=reset_camera_callback,
                        v_if=("show_reset_camera", show_reset_camera),
                    ),
                )

            with (
                v3.VTooltip(
                    "Set view direction to +X",
                    location="bottom",
                ),
                v3.Template(v_slot_activator=("{ props }",)),
            ):
                (
                    v3.VBtn(
                        icon="mdi-axis-x-arrow",
                        v_bind=("props",),
                        click=reset_to_positive_x,
                        v_if=("show_reset_camera_x", show_reset_camera_x),
                    ),
                )

            with (
                v3.VTooltip(
                    "Set view direction to +Y",
                    location="bottom",
                ),
                v3.Template(v_slot_activator=("{ props }",)),
            ):
                (
                    v3.VBtn(
                        icon="mdi-axis-y-arrow",
                        v_bind=("props",),
                        click=reset_to_positive_y,
                        v_if=("show_reset_camera_y", show_reset_camera_y),
                    ),
                )

            with (
                v3.VTooltip(
                    "Set view direction to +Z",
                    location="bottom",
                ),
                v3.Template(v_slot_activator=("{ props }",)),
            ):
                (
                    v3.VBtn(
                        icon="mdi-axis-z-arrow",
                        v_bind=("props",),
                        click=reset_to_positive_z,
                        v_if=("show_reset_camera_z", show_reset_camera_z),
                    ),
                )

    @property
    def view(self):
        return simple.GetActiveView()
