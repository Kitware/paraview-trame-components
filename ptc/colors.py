from paraview import simple
from trame.decorators import TrameApp, change, controller
from trame.widgets import html, vuetify3

ASSOCIATION_MAP = {
    "0": "POINTS",
    "P": "POINTS",
    "1": "CELLS",
    "C": "CELLS",
    "2": "FIELDS",
    "F": "FIELDS",
}

COLOR_PALETTE = [
    (1, 1, 1),
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (0.5, 0, 0),
    (0, 0.5, 0),
    (0, 0, 0.5),
    (0.5, 0.5, 0),
    (0, 0.5, 0.5),
    (0.5, 0.5, 0.5),
]


def association_to_str(number):
    if number == 0:
        return "POINTS"
    if number == 1:
        return "CELLS"
    if number == 2:
        return "FIELDS"
    return ""


def extract_value(value):
    if not value:
        return "POINTS", ""

    association = value[0]
    title = value[1:]
    return ASSOCIATION_MAP[association], title


@TrameApp()
class ColorBy(html.Div):
    def __init__(self, **kwargs):
        super().__init__(
            **{
                **kwargs,
                "classes": kwargs.get("classes", "elevation-5 rounded-lg"),
                "style": "overflow: hidden;" + kwargs.get("style", ""),
            },
        )

        with (
            self,
            html.Div(
                v_if=("colorby_show", False),
                classes="pa-1 d-flex align-center",
                style="pointer-events: auto; user-select: none; background: rgba(255, 255, 255, 0.5);",
            ),
        ):
            self.server.ui.colorby_prepend()
            vuetify3.VSelect(
                v_model=("colorby_active", ""),
                items=("colorby_available", []),
                density="compact",
                hide_details=True,
                style="min-width: 10rem;",
                variant="outlined",
            )
            with vuetify3.VMenu(location="bottom"):
                with vuetify3.Template(v_slot_activator="{ props }"):
                    vuetify3.VBtn(
                        icon="mdi-palette",
                        v_bind="props",
                        flat=True,
                        density="compact",
                        classes="mx-2",
                        v_show="colorby_active === ''",
                    )
                with html.Div(style="max-width: 20rem;", classes="d-flex flex-wrap"):
                    for r, g, b in COLOR_PALETTE:
                        vuetify3.VBtn(
                            classes="ma-1",
                            style=f"background: rgb({int(255 * r)}, {int(255 * g)}, {int(255 * b)})",
                            click=(self.set_solid_color, f"[{r}, {g}, {b}]"),
                        )

    @property
    def prepend(self):
        return self.server.ui.colorby_prepend

    @property
    def state(self):
        return self.server.state

    @property
    def source(self):
        return simple.GetActiveSource()

    @property
    def representation(self):
        active = self.source
        if active:
            return simple.GetRepresentation(active)
        return None

    @property
    def active_color(self):
        active_rep = self.representation
        if active_rep:
            association, title = self.representation.ColorArrayName
            if title:
                return f"{association[0]}{title}"
        return ""

    @property
    def available_colors(self):
        active_rep = self.representation
        if not active_rep:
            return []

        available_colors = [{"title": "Solid Color", "value": ""}]
        pv_prop = self.representation.ColorArrayName.SMProperty
        domain = pv_prop.FindDomain("vtkSMArrayListDomain")

        for idx in range(domain.GetNumberOfStrings()):
            title = domain.GetString(idx)
            association = association_to_str(domain.GetFieldAssociation(idx))
            add_on = " (partial)" if domain.IsArrayPartial(idx) else ""
            available_colors.append(
                dict(title=title + add_on, value=f"{association[0]}{title}")
            )

        return available_colors

    @change("colorby_active")
    def _color_change(self, colorby_active, **_):
        if self.active_color == colorby_active or self.representation is None:
            return

        association, name = extract_value(colorby_active)
        simple.ColorBy(self.representation, (association, name))
        self.server.controller.on_data_change()

    @controller.add("on_active_proxy_change")
    def _update_available(self):
        if self.source is None:
            self.state.colorby_show = False
            return

        self.state.colorby_show = True
        self.state.colorby_active = self.active_color
        self.state.colorby_available = self.available_colors

    def set_solid_color(self, r, g, b):
        rep = self.representation
        if rep:
            rep.AmbientColor = [r, g, b]
            rep.DiffuseColor = [r, g, b]
            self.server.controller.on_data_change()
