from paraview import simple
from trame.widgets import vuetify3 as v3, html
from trame.decorators import change
import math

PREFIX = "ptc_clip_plane"


def ALL_KEYS():
    yield f"{PREFIX}_name"
    yield f"{PREFIX}_crinkle"
    yield f"{PREFIX}_invert"
    for i in range(3):
        yield f"{PREFIX}_origin_{i}"
        yield f"{PREFIX}_normal_{i}"


class PlaneEditorPanel(v3.VCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.flat = True

        self.state.setdefault(f"{PREFIX}_mode", "txt")
        self.state.setdefault(f"{PREFIX}_name", "Clip")
        self.state.setdefault(f"{PREFIX}_bounds", [0, 1, 0, 1, 0, 1])
        self.disable_next_change = True

        with self:
            with v3.VCardItem():
                v3.VCardTitle(f"{{{{ {PREFIX}_name }}}}")
                with v3.Template(raw_attrs=["#append"]):
                    with html.Div(classes="d-flex ga-2"):
                        v3.VBtn(
                            icon="mdi-text-recognition",
                            click=f"{PREFIX}_mode = 'txt'",
                            density="compact",
                            hide_details=True,
                            flat=True,
                        )
                        v3.VBtn(
                            icon="mdi-tune-variant",
                            click=f"{PREFIX}_mode = 'slider'",
                            density="compact",
                            hide_details=True,
                            flat=True,
                        )
            v3.VDivider()

            with html.Div(classes="pa-4"):
                with v3.VRow(dense=True):
                    with v3.VCol(cols=12):
                        html.Label(
                            "Origin",
                            classes="text-subtitle-1 font-weight-medium d-block",
                        )
                        with v3.VRow(dense=True, v_show=f"{PREFIX}_mode === 'txt'"):
                            with v3.VCol(cols=4):
                                v3.VTextField(
                                    v_model_number=(f"{PREFIX}_origin_0", 0),
                                    density="compact",
                                    variant="outlined",
                                    hide_details=True,
                                    type="number",
                                    step=(
                                        f"({PREFIX}_bounds[1] - {PREFIX}_bounds[0]) / 255",
                                    ),
                                    hide_spin_buttons=True,
                                    __properties=["step"],
                                )
                            with v3.VCol(cols=4):
                                v3.VTextField(
                                    v_model_number=(f"{PREFIX}_origin_1", 0),
                                    density="compact",
                                    variant="outlined",
                                    hide_details=True,
                                    type="number",
                                    step=(
                                        f"({PREFIX}_bounds[3] - {PREFIX}_bounds[2]) / 255",
                                    ),
                                    hide_spin_buttons=True,
                                    __properties=["step"],
                                )
                            with v3.VCol(cols=4):
                                v3.VTextField(
                                    v_model_number=(f"{PREFIX}_origin_2", 0),
                                    density="compact",
                                    variant="outlined",
                                    hide_details=True,
                                    type="number",
                                    step=(
                                        f"({PREFIX}_bounds[5] - {PREFIX}_bounds[4]) / 255",
                                    ),
                                    hide_spin_buttons=True,
                                    __properties=["step"],
                                )

                    with v3.VCol(cols=12, v_show=f"{PREFIX}_mode === 'slider'"):
                        v3.VSlider(
                            v_model=(f"{PREFIX}_origin_0", 0),
                            density="compact",
                            hide_details=True,
                            min=(f"{PREFIX}_bounds[0]",),
                            max=(f"{PREFIX}_bounds[1]",),
                            step=(f"({PREFIX}_bounds[1] - {PREFIX}_bounds[0]) / 255",),
                        )
                        v3.VSlider(
                            v_model=(f"{PREFIX}_origin_1", 0),
                            density="compact",
                            hide_details=True,
                            min=(f"{PREFIX}_bounds[2]",),
                            max=(f"{PREFIX}_bounds[3]",),
                            step=(f"({PREFIX}_bounds[3] - {PREFIX}_bounds[2]) / 255",),
                        )
                        v3.VSlider(
                            v_model=(f"{PREFIX}_origin_2", 0),
                            density="compact",
                            hide_details=True,
                            min=(f"{PREFIX}_bounds[4]",),
                            max=(f"{PREFIX}_bounds[5]",),
                            step=(f"({PREFIX}_bounds[5] - {PREFIX}_bounds[4]) / 255",),
                        )

                with v3.VRow(dense=True):
                    with v3.VCol(cols=12):
                        html.Label(
                            "Normal",
                            classes="text-subtitle-1 font-weight-medium d-block",
                        )
                        with v3.VRow(dense=True, v_show=f"{PREFIX}_mode === 'txt'"):
                            with v3.VCol(cols=4):
                                v3.VTextField(
                                    v_model=(f"{PREFIX}_normal_0", 0),
                                    density="compact",
                                    variant="outlined",
                                    hide_details=True,
                                )
                            with v3.VCol(cols=4):
                                v3.VTextField(
                                    v_model=(f"{PREFIX}_normal_1", 0),
                                    density="compact",
                                    variant="outlined",
                                    hide_details=True,
                                )
                            with v3.VCol(cols=4):
                                v3.VTextField(
                                    v_model=(f"{PREFIX}_normal_2", 0),
                                    density="compact",
                                    variant="outlined",
                                    hide_details=True,
                                )

                    with v3.VCol(
                        cols=12,
                        v_show=f"{PREFIX}_mode === 'slider'",
                    ):
                        v3.VSlider(
                            v_model=(f"{PREFIX}_normal_0", 0),
                            density="compact",
                            hide_details=True,
                            min=-1,
                            max=1,
                            step=0.1,
                        )
                        v3.VSlider(
                            v_model=(f"{PREFIX}_normal_1", 0),
                            density="compact",
                            hide_details=True,
                            min=-1,
                            max=1,
                            step=0.1,
                        )
                        v3.VSlider(
                            v_model=(f"{PREFIX}_normal_2", 0),
                            density="compact",
                            hide_details=True,
                            min=-1,
                            max=1,
                            step=0.1,
                        )

                    with v3.VCol(cols=12):
                        with html.Div(
                            classes="d-flex justify-space-between align-center"
                        ):
                            v3.VBtn(
                                prepend_icon="mdi-axis-x-arrow",
                                text="X",
                                click=f"{PREFIX}_normal_0 = 1;{PREFIX}_normal_1 = 0;{PREFIX}_normal_2 = 0;",
                                density="compact",
                                hide_details=True,
                                variant="tonal",
                                color="primary",
                                stacked=True,
                                size="small",
                            )
                            v3.VBtn(
                                prepend_icon="mdi-axis-y-arrow",
                                text="Y",
                                click=f"{PREFIX}_normal_0 = 0;{PREFIX}_normal_1 = 1;{PREFIX}_normal_2 = 0;",
                                density="compact",
                                hide_details=True,
                                variant="tonal",
                                color="primary",
                                stacked=True,
                                size="small",
                            )
                            v3.VBtn(
                                prepend_icon="mdi-axis-z-arrow",
                                text="Z",
                                click=f"{PREFIX}_normal_0 = 0;{PREFIX}_normal_1 = 0;{PREFIX}_normal_2 = 1;",
                                density="compact",
                                hide_details=True,
                                variant="tonal",
                                color="primary",
                                stacked=True,
                                size="small",
                            )
                            v3.VBtn(
                                prepend_icon="mdi-camera-outline",
                                text="Camera",
                                click=self.normal_to_camera,
                                density="compact",
                                hide_details=True,
                                variant="tonal",
                                color="secondary",
                                stacked=True,
                                size="small",
                            )

                with html.Div(classes="d-flex justify-space-between align-center mt-2"):
                    v3.VSwitch(
                        true_icon="mdi-cookie-outline",
                        false_icon="mdi-gesture",
                        v_model=(f"{PREFIX}_crinkle", False),
                        density="compact",
                        hide_details=True,
                        label="Crinkle",
                        inset=True,
                    )
                    v3.VSwitch(
                        v_show=f"{PREFIX}_name === 'Clip'",
                        true_icon="mdi-arrow-expand-right",
                        false_icon="mdi-arrow-expand-left",
                        v_model=(f"{PREFIX}_invert", False),
                        density="compact",
                        hide_details=True,
                        label="Invert",
                        inset=True,
                    )

    def normal_to_camera(self):
        view = simple.GetActiveView()
        cp = view.CameraPosition
        fp = view.CameraFocalPoint
        normal = [cp[i] - fp[i] for i in range(3)]
        norm = math.sqrt(
            normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2]
        )
        for i in range(3):
            self.state[f"{PREFIX}_normal_{i}"] = normal[i] / norm

    @change(*list(ALL_KEYS()))
    def on_change(self, **_):
        if self.disable_next_change:
            self.disable_next_change = False
            return

        if self.ctrl.on_active_proxy_modified.exists():
            self.ctrl.on_active_proxy_modified()

    def can_handle(self, proxy):
        if proxy is None:
            return False

        if proxy.GetXMLName() not in {"Clip", "Cut"}:
            return False

        return True

    def update_ui(self, proxy):
        """Read proxy property and update UI"""
        if not self.can_handle(proxy):
            return

        name = proxy.GetXMLName()

        if name == "Clip":
            implicit_fn_proxy = proxy.ClipType
            crinkle = proxy.Crinkleclip
            invert = proxy.Invert
        elif name == "Cut":
            implicit_fn_proxy = proxy.SliceType
            crinkle = proxy.Crinkleslice
            invert = False

        bounds = proxy.Input.GetDataInformation().DataInformation.GetBounds()
        origin = implicit_fn_proxy.Origin
        normal = implicit_fn_proxy.Normal

        self.state[f"{PREFIX}_name"] = name
        self.state[f"{PREFIX}_bounds"] = bounds
        self.state[f"{PREFIX}_crinkle"] = bool(crinkle)
        self.state[f"{PREFIX}_invert"] = bool(invert)

        for i in range(3):
            self.state[f"{PREFIX}_origin_{i}"] = origin[i]
            self.state[f"{PREFIX}_normal_{i}"] = normal[i]

        self.disable_next_change = True
        self.state.dirty(f"{PREFIX}_name")

    def update_proxy(self, proxy):
        """Read proxy property and update UI"""
        if not self.can_handle(proxy):
            return

        origin = [self.state[f"{PREFIX}_origin_{i}"] for i in range(3)]
        normal = [self.state[f"{PREFIX}_normal_{i}"] for i in range(3)]
        crinkle = self.state[f"{PREFIX}_crinkle"]
        invert = self.state[f"{PREFIX}_invert"]

        if proxy.GetXMLName() == "Cut":
            proxy.SliceType.Origin = origin
            proxy.SliceType.Normal = normal
            proxy.Crinkleslice = 1 if crinkle else 0

        if proxy.GetXMLName() == "Clip":
            proxy.ClipType.Origin = origin
            proxy.ClipType.Normal = normal
            proxy.Crinkleclip = 1 if crinkle else 0
            proxy.Invert = 1 if invert else 0
