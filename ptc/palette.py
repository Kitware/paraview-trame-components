from paraview import simple
from trame.widgets import vuetify3

PALETTES = [
    {"title": "Blue Gray Background (Default)", "value": "BlueGrayBackground"},
    {"title": "White Background", "value": "WhiteBackground"},
    {"title": "Warm Gray Background", "value": "WarmGrayBackground"},
    {"title": "Dark Gray Background", "value": "DarkGrayBackground"},
    {"title": "Neutral Gray Background", "value": "NeutralGrayBackground"},
    {"title": "Light Gray Background", "value": "LightGrayBackground"},
    {"title": "Black Background", "value": "BlackBackground"},
    {"title": "Gradient Background", "value": "GradientBackground"},
]


class PalettePicker(vuetify3.VMenu):
    def __init__(self, palette_name=None, **kwargs):
        super().__init__(**kwargs)

        if palette_name is not None:
            self.load_palette(palette_name)

        with self:
            with vuetify3.Template(v_slot_activator="{ props }"):
                vuetify3.VBtn(
                    icon="mdi-palette-outline",
                    v_bind="props",
                    size="small",
                    style="pointer-events: auto; user-select: none;",
                    **kwargs,
                )
            vuetify3.VList(
                density="compact",
                items=("palette_list", PALETTES),
                click_select=(self.load_palette, "[$event.id]"),
            )

    def load_palette(self, name):
        simple.LoadPalette(paletteName=name)
        self.server.controller.on_data_change()
