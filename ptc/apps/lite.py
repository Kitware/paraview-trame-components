import ptc
from trame.widgets.trame import MouseTrap
from paraview import simple


class Lite(ptc.Viewer):
    def __init__(self):
        super().__init__(from_state=True, reset_camera_button=False)

        self.state.trame__title = "ParaView Lite"
        self.state.trame__favicon = "ptc/favicon.png"

        with self.ui:
            with MouseTrap(
                ptcResetCamera=(self.reset_camera, "[$event?.altKey]"),
                ptcFileOpen="ptc_openfile_dialog_open = !ptc_openfile_dialog_open",
                ptcFilterAdd="ptc_filter_dialog_open = !ptc_filter_dialog_open",
                ptcPipeline="ptc_drawer_pipeline = !ptc_drawer_pipeline",
                ptcColor="ptc_show_color_by = !ptc_show_color_by",
                ptcTime="ptc_show_vcr = !ptc_show_vcr",
                ptcThemeLight="ptc_light_theme = true",
                ptcThemeDark="ptc_light_theme = false",
            ) as mt:
                mt.bind(["r", "alt+r"], "ptcResetCamera")
                mt.bind(["meta+o", "ctrl+o"], "ptcFileOpen")
                mt.bind(["alt+space", "meta+space", "ctrl+space"], "ptcFilterAdd")
                mt.bind(["p"], "ptcPipeline")
                mt.bind(["c"], "ptcColor")
                mt.bind(["t"], "ptcTime")
                mt.bind(["l"], "ptcThemeLight")
                mt.bind(["d"], "ptcThemeDark")

        with self.ui_layout:
            with ptc.VerticalToolbar().bar:
                ptc.VListItem(
                    prepend_icon=(
                        "ptc_show_color_by ? 'mdi-format-color-fill' : 'mdi-format-color-fill'",
                    ),
                    click="ptc_show_color_by = !ptc_show_color_by",
                )
                ptc.VListItem(
                    prepend_icon=(
                        "ptc_show_vcr ? 'mdi-clock-time-four-outline' : 'mdi-clock-time-four-outline'",
                    ),
                    click="ptc_show_vcr = !ptc_show_vcr",
                )

            ptc.AddFilterDialog()

        with self.ui_view_container:
            with ptc.Div(
                v_show=("ptc_show_vcr", False),
                style="position: absolute; bottom: 0.5rem; left: 5rem; right: 5rem;",
            ):
                ptc.TimeControl()

        with self.col_center:
            with ptc.ColorBy() as color:
                color.v_show = ("ptc_show_color_by", False)
                with color.prepend:
                    ptc.RepresentBy(classes="mr-2")

    def reset_camera(self, use_active_proxy_bounds=False):
        bounds = None
        view = simple.GetActiveView()
        source = simple.GetActiveSource()

        if use_active_proxy_bounds and source:
            bounds = source.GetDataInformation().DataInformation.GetBounds()

        view.ResetCamera(bounds)
        self.update()


def main():
    app = Lite()
    app.start()


if __name__ == "__main__":
    main()
