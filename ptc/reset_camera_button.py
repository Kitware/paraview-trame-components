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
    - The second places the camera at -x and look in the x direction.
    - The third places the camera at -y and look in the y direction.
    - The fourth places the camera at -z and look in the z direction.

    By default, they will be placed at the top left of its parent component.
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
            simple.GetActiveView().ResetActiveCameraToPositiveX()
            self.ctrl.view_reset_camera()

        def reset_to_positive_y() -> None:
            simple.GetActiveView().ResetActiveCameraToPositiveY()
            self.ctrl.view_reset_camera()

        def reset_to_positive_z() -> None:
            simple.GetActiveView().ResetActiveCameraToPositiveZ()
            self.ctrl.view_reset_camera()

        buttons = [
            Button(
                icon="mdi-crop-free",
                tooltip="Reset Camera",
                click_callback=reset_camera,
            ),
            Button(
                icon="mdi-axis-x-arrow",
                tooltip="Reset Camera X",
                click_callback=reset_to_positive_x,
            ),
            Button(
                icon="mdi-axis-y-arrow",
                tooltip="Reset Camera Y",
                click_callback=reset_to_positive_y,
            ),
            Button(
                icon="mdi-axis-z-arrow",
                tooltip="Reset Camera Z",
                click_callback=reset_to_positive_z,
            ),
        ]

        with (
            self,
        ):
            for button in buttons:
                with (
                    v3.VTooltip(button.tooltip, location="bottom"),
                    v3.Template(v_slot_activator=("{ props }",)),
                    v3.VBtn(
                        icon=True,
                        v_bind=("props",),
                        click=button.click_callback,
                        variant="text",
                        # variant="outlined",
                        size="small",
                        classes="ma-0",
                        style="background-color: white;",
                    ),
                ):
                    v3.VIcon(button.icon)

    @property
    def view(self):
        return simple.GetActiveView()
