import logging
from paraview import simple
from trame.widgets import vuetify2
from trame_server.controller import FunctionNotImplementedError
from ..palette import PALETTES

logger = logging.getLogger(__name__)


class PalettePicker(vuetify2.VMenu):
    def __init__(self, palette_name=None, **kwargs):
        super().__init__(**kwargs)

        self.server.state.palette_list = PALETTES

        if palette_name is not None:
            self.load_palette(palette_name)

        with self:
            with vuetify2.Template(v_slot_activator="{ on, attrs }"):
                with vuetify2.VBtn(
                    v_bind="attrs",
                    v_on="on",
                    size="small",
                    style="pointer-events: auto; user-select: none;",
                    **kwargs,
                ):
                    vuetify2.VIcon("mdi-palette-outline")
            with vuetify2.VList():
                vuetify2.VListItem(
                    "{{ palette.title }}",
                    v_for="palette in palette_list",
                    click=(self.load_palette, "[palette.value]"),
                )

    def load_palette(self, name):
        simple.LoadPalette(paletteName=name)

        try:
            self.server.controller.on_data_change()
        except FunctionNotImplementedError:
            logger.warning("on_data_change is not implemented")
