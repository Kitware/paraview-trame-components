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


class ResetCameraButtons(v3.VBtnGroup):
    """
    A widget composed of 4 buttons to reset the camera of a view :
    - The first is used to reset the camera to see the entire object.
    - The second places the camera at -x from the object and look in the x direction.
    - The third places the camera at -y from the object and look in the y direction.
    - The fourth places the camera at -z from the object and look in the z direction.
    """

    def __init__(
        self, style: str | None = None, classes: str | None = None, **kwargs
    ) -> None:
        if style is None:
            style = "top: 0.5rem; left: 0.5rem"
        if classes is None:
            classes = "position-absolute"
        super().__init__(
            style=style,
            classes=classes,
            **kwargs,
        )

        def reset_camera() -> None:
            self.ctrl.view_reset_camera()
            simple.Render()

        def reset_to_positive_x() -> None:
            self.view.ResetActiveCameraToPositiveX()
            self.ctrl.view_reset_camera()

        def reset_to_positive_y() -> None:
            self.view.ResetActiveCameraToPositiveY()
            self.ctrl.view_reset_camera()

        def reset_to_positive_z() -> None:
            self.view.ResetActiveCameraToPositiveZ()
            self.ctrl.view_reset_camera()

        buttons = [
            Button(
                icon="mdi-crop-free",
                tooltip="Reset Camera",
                click_callback=reset_camera,
            ),
            Button(
                icon="mdi-axis-x-arrow",
                tooltip="Set view direction to +X",
                click_callback=reset_to_positive_x,
            ),
            Button(
                icon="mdi-axis-y-arrow",
                tooltip="Set view direction to +Y",
                click_callback=reset_to_positive_y,
            ),
            Button(
                icon="mdi-axis-z-arrow",
                tooltip="Set view direction to +Z",
                click_callback=reset_to_positive_z,
            ),
        ]

        with self:
            for button in buttons:
                with (
                    v3.VTooltip(button.tooltip, location="bottom"),
                    v3.Template(v_slot_activator=("{ props }",)),
                    v3.VBtn(
                        icon=True,
                        v_bind=("props",),
                        click=button.click_callback,
                        variant="text",
                        size="small",
                        classes="ma-0",
                    ),
                ):
                    v3.VIcon(button.icon)

    @property
    def view(self):
        return simple.GetActiveView()
