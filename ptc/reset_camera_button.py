from dataclasses import dataclass
from typing import Callable

from paraview import simple
from trame.widgets import vuetify3 as v3


@dataclass
class Button:
    """
    A minimal class to create a button.
    """

    icon: str
    tooltip: str
    click_callback: Callable
    v_show: str = "true"
    v_if: str = "true"


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
        reset_camera: bool = True,
        reset_camera_x: bool = True,
        reset_camera_y: bool = True,
        reset_camera_z: bool = True,
        camera_style_toggle: bool = True,
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

        def toggle_interaction_mode_2D() -> None:
            self.view.InteractionMode = "2D"
            self.state.interaction_mode = "2D"

        def toggle_interaction_mode_3D() -> None:
            self.view.InteractionMode = "3D"
            self.state.interaction_mode = "3D"

        buttons = [
            Button(
                icon="mdi-video-2d",
                tooltip="Change interaction mode",
                click_callback=toggle_interaction_mode_3D,
                v_show=("interaction_mode === '2D'"),
                v_if="true" if camera_style_toggle else "false",
            ),
            Button(
                icon="mdi-video-3d",
                tooltip="Change interaction mode",
                click_callback=toggle_interaction_mode_2D,
                v_show=("interaction_mode === '3D'"),
                v_if="true" if camera_style_toggle else "false",
            ),
            Button(
                icon="mdi-crop-free",
                tooltip="Reset Camera",
                click_callback=reset_camera_callback,
                v_if="true" if reset_camera else "false",
            ),
            Button(
                icon="mdi-axis-x-arrow",
                tooltip="Set view direction to +X",
                click_callback=reset_to_positive_x,
                v_if="true" if reset_camera_x else "false",
            ),
            Button(
                icon="mdi-axis-y-arrow",
                tooltip="Set view direction to +Y",
                click_callback=reset_to_positive_y,
                v_if="true" if reset_camera_y else "false",
            ),
            Button(
                icon="mdi-axis-z-arrow",
                tooltip="Set view direction to +Z",
                click_callback=reset_to_positive_z,
                v_if="true" if reset_camera_z else "false",
            ),
        ]

        with self:
            for button in buttons:
                if button.tooltip is None:
                    v3.VBtn(
                        icon=button.icon,
                        click=button.click_callback,
                        size="small",
                        v_show=button.v_show,
                        v_if=button.v_if,
                    )
                else:
                    with (
                        v3.VTooltip(button.tooltip, location="bottom"),
                        v3.Template(v_slot_activator=("{ props }",)),
                    ):
                        v3.VBtn(
                            icon=button.icon,
                            v_bind=("props",),
                            click=button.click_callback,
                            size="small",
                            v_show=button.v_show,
                            v_if=button.v_if,
                        )

    @property
    def view(self):
        return simple.GetActiveView()
