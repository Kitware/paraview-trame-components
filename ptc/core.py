from paraview import simple
from trame.app import get_server
from trame.decorators import TrameApp, controller
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import paraview as pv_widgets

from .layouts import create_layout_manager


class InvalidContainerNameError(Exception):
    def __init__(self, name):
        super().__init__(f"Container {name} not available")


@TrameApp()
class Viewer:
    def __init__(self, view=None, from_state=False, server=None, template_name="main"):
        self.layout_factory = create_layout_manager(self)
        self.template_name = template_name
        self.server = get_server(server)
        self.view = view
        self.ui = None
        if self.view is None:
            self.view = simple.GetActiveView()

        if from_state:
            self.view.MakeRenderWindowInteractor(True)

        self._build_ui()

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    def start(self, *args, **kwargs):
        self.ui.flush_content()
        self.server.start(*args, **kwargs)

    def _build_ui(self):
        with VAppLayout(
            self.server, template_name=self.template_name, full_height=True
        ) as layout:
            self.ui = layout
            view = pv_widgets.VtkRemoteView(self.view, interactive_ratio=1)
            self.ctrl.view_update = view.update
            self.ctrl.view_reset_camera = view.reset_camera

    @controller.add("on_data_change")
    def update(self):
        self.ctrl.view_update()

    def reset_camera(self):
        self.ctrl.view_reset_camera()

    def __getattr__(self, key):
        """Lookup a layout specific container."""
        manager = self.layout_factory.get_manager(key)

        if manager is None:
            raise InvalidContainerNameError(key)

        with self.ui:
            return manager.create_container(key)
