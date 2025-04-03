import ptc


class Lite(ptc.Viewer):
    def __init__(self):
        super().__init__(from_state=True, reset_camera_button=False)

        self.state.trame__title = "ParaView Lite"
        self.state.trame__favicon = "ptc/favicon.png"

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


def main():
    app = Lite()
    app.start()


if __name__ == "__main__":
    main()
