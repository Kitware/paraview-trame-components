from paraview import simple
from trame.decorators import TrameApp, change, controller
from trame.widgets import vuetify3 as v3


@TrameApp()
class RepresentBy(v3.VSelect):
    def __init__(self, **kwargs):
        super().__init__(
            v_if=("representation_show", False),
            v_model=("representation_active", "Surface"),
            items=("representation_available", []),
            density="compact",
            hide_details=True,
            style="min-width: 10rem;",
            variant="outlined",
            **kwargs,
        )

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
    def active_representation(self):
        active_rep = self.representation
        if active_rep:
            return str(self.representation.Representation)[1:-1]

        return ""

    @property
    def available_representations(self):
        active_rep = self.representation
        if not active_rep:
            return []

        return [str(v) for v in self.representation.Representation.Available]

    @change("representation_active")
    def _representation_change(self, representation_active, **_):
        if (
            self.active_representation == representation_active
            or self.representation is None
        ):
            return

        self.representation.Representation = representation_active
        self.server.controller.on_data_change()

    @controller.add("on_active_proxy_change")
    def _update_available(self):
        if self.source is None:
            self.state.representation_show = False
            return

        self.state.representation_show = True

        self.state.representation_active = self.active_representation
        self.state.representation_available = self.available_representations
