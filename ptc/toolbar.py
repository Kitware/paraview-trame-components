from trame.widgets import vuetify3 as v3, html
import ptc


class VerticalToolbar(v3.VNavigationDrawer):
    def __init__(self, **_):
        super().__init__(
            theme="dark",
            permanent=True,
            rail=True,
            rail_width=40,
        )

        with self:
            with v3.VList(density="compact", nav=True, classes="pa-0") as self.bar:
                v3.VListItem(
                    prepend_icon="mdi-crop-free",
                    click=self.ctrl.view_reset_camera,
                )
                v3.VListItem(
                    style="transform: scale(1, -1);",
                    prepend_icon="mdi-source-branch",
                    click="ptc_drawer_pipeline = !ptc_drawer_pipeline",
                )
                v3.VListItem(
                    prepend_icon="mdi-file-plus-outline",
                    click="ptc_openfile_dialog_open = !ptc_openfile_dialog_open",
                )
                v3.VListItem(
                    prepend_icon="mdi-database-plus-outline",
                )
            with html.Div(classes="position-absolute bottom-0 left-0"):
                ptc.PalettePicker()

        # Add another drawer for pipeline + editor
        with v3.VNavigationDrawer(
            v_model=("ptc_drawer_pipeline", False),
            width=320,
            disable_resize_watcher=True,
            disable_route_watcher=True,
            floating=True,
            absolute=True,
        ):
            ptc.PipelineBrowser(
                flat=True,
                width=320,
                classes="elevation-0",
            )
            with ptc.ProxyEditor() as self.proxy_editor:
                # register UI we want to have available
                ptc.proxy_editor.InfoPanel()
                ptc.proxy_editor.PlaneEditorPanel()

        # Add File browser
        ptc.OpenFileDialog(dialog_open=False)
