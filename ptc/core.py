from pathlib import Path

from paraview import simple
from trame.app import get_server
from trame.decorators import TrameApp, change, controller
from trame.ui.vuetify3 import VAppLayout
from trame.widgets import html
from trame.widgets import paraview as pv_widgets
from trame.widgets import vuetify3 as v3

from .layouts import create_layout_manager


class InvalidContainerNameError(Exception):
    def __init__(self, name):
        super().__init__(f"Container {name} not available")


@TrameApp()
class Viewer:
    def __init__(
        self,
        views=None,
        from_state=False,
        server=None,
        reset_camera_button=True,
        template_name="main",
    ):
        self.layout_factory = create_layout_manager(self)
        self.template_name = template_name
        self.server = get_server(server)

        # Serve our http directory
        self.server.enable_module(
            {
                "serve": {
                    "ptc": str(Path(__file__).with_name("assets") / "http"),
                },
                "styles": ["ptc/style.css"],
            }
        )

        self.views = views
        self.html_views = []
        self.interactive_modes = None
        self.proxy_views = []
        self.ui = None
        if self.views is None or len(self.views) == 0:
            view = simple.GetActiveView()
            if view is None:
                view = simple.CreateRenderView()
            self.views = [view]

        if from_state:
            for view in self.views:
                view.MakeRenderWindowInteractor(True)

        self._build_ui(reset_camera_button)

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    def start(self, *args, **kwargs):
        self.ui.flush_content()
        self.server.start(*args, **kwargs)

    @change("active_view_id")
    def _active_view(self, active_view_id, **_):
        if active_view_id < len(self.proxy_views):
            simple.SetActiveView(self.proxy_views[active_view_id])
            if self.server.controller.on_active_view_change.exists():
                self.server.controller.on_active_view_change()

    def _build_ui(self, reset_camera_button):
        self.state.active_view_id = 1
        self.state.remote_view_mouse = None
        self.state.html_view_space = None
        self.state.client_only("html_view_space")
        with VAppLayout(
            self.server, template_name=self.template_name, full_height=True
        ) as layout:
            self.ui = layout
            with v3.VLayout() as self.ui_layout:
                with v3.VMain(classes="fill-height position-relative") as self.ui_main:
                    with html.Div(
                        classes="d-flex align-stretch fill-height position-relative"
                    ) as self.ui_view_container:
                        for view in self.views:
                            if isinstance(view, list | tuple):
                                with html.Div(
                                    classes="d-flex align-stretch fill-height flex-column flex-grow-1 flex-shrink-1"
                                ):
                                    for v in view:
                                        view_id = len(self.html_views)
                                        with html.Div(
                                            classes="flex-grow-1 flex-shrink-1 border-thin position-relative",
                                            style=(
                                                f"{{ overflow: 'hidden', zIndex: 0, padding: '1px', margin: '1px', outline: active_view_id === {view_id} ? 'solid 1.5px blue' : 'none' }}",
                                            ),
                                            click=f"active_view_id = {view_id}",
                                        ):
                                            view_html = pv_widgets.VtkRemoteView(
                                                v,
                                                interactive_ratio=1,
                                                enable_picking=(
                                                    "enable_picking",
                                                    False,
                                                ),
                                                style="z-index: -1;",
                                                interactor_events=(
                                                    "remote_view_events",
                                                    ["EndAnimation", "MouseMove"],
                                                ),
                                                MouseMove="remote_view_mouse = $event.position",
                                                mouse_enter="html_view_space = $event.target.getBoundingClientRect()",
                                                __events=[
                                                    ("mouse_enter", "mouseenter")
                                                ],
                                            )
                                            if reset_camera_button:
                                                v3.VBtn(
                                                    icon="mdi-crop-free",
                                                    click=view_html.reset_camera,
                                                    classes="position-absolute",
                                                    style="top: 1rem;right: 1rem; z-index: 1;",
                                                    variant="outlined",
                                                    size="small",
                                                )
                                            self.ctrl.on_data_loaded.add(
                                                view_html.reset_camera
                                            )
                                            self.ctrl.view_update.add(view_html.update)
                                            self.ctrl.view_reset_camera.add(
                                                view_html.reset_camera
                                            )
                                            self.html_views.append(view_html)
                                            self.proxy_views.append(v)
                            else:
                                view_id = len(self.html_views)
                                with html.Div(
                                    classes="flex-grow-1 flex-shrink-1 border-thin position-relative",
                                    style=(
                                        f"{{ overflow: 'hidden', zIndex: 0, padding: '1px', margin: '1px', outline: active_view_id === {view_id} ? 'solid 1.5px blue' : 'none' }}",
                                    ),
                                    click=f"active_view_id = {view_id}",
                                ):
                                    view_html = pv_widgets.VtkRemoteView(
                                        view,
                                        interactive_ratio=1,
                                        enable_picking=("enable_picking", False),
                                        style="z-index: -1;",
                                        interactor_events=(
                                            "remote_view_events",
                                            ["EndAnimation", "MouseMove"],
                                        ),
                                        MouseMove="remote_view_mouse = $event.position",
                                        mouse_enter="html_view_space = $event.target.getBoundingClientRect()",
                                        __events=[("mouse_enter", "mouseenter")],
                                    )
                                    if reset_camera_button:
                                        v3.VBtn(
                                            icon="mdi-crop-free",
                                            click=view_html.reset_camera,
                                            classes="position-absolute",
                                            style="top: 1rem;right: 1rem; z-index: 1;",
                                            variant="outlined",
                                            size="small",
                                        )

                                    self.ctrl.view_update.add(view_html.update)
                                    self.ctrl.view_reset_camera.add(
                                        view_html.reset_camera
                                    )
                                    self.ctrl.on_data_loaded.add(view_html.reset_camera)
                                    self.html_views.append(view_html)
                                    self.proxy_views.append(view)

    @controller.add("on_data_change")
    def update(self):
        self.ctrl.view_update()

    @controller.set("enable_selection")
    def enable_selection(self, selection=True):
        if self.interactive_modes is None:
            self.interactive_modes = [
                str(v.InteractionMode).replace("'", "") for v in self.proxy_views
            ]

        if selection:
            for v in self.proxy_views:
                v.InteractionMode = "Selection"
        else:
            for v, mode in zip(self.proxy_views, self.interactive_modes, strict=False):
                v.InteractionMode = mode

    def reset_camera(self):
        self.ctrl.view_reset_camera()

    def __getattr__(self, key):
        """Lookup a layout specific container."""
        manager = self.layout_factory.get_manager(key)

        if manager is None:
            raise InvalidContainerNameError(key)

        with self.ui:
            return manager.create_container(key)
