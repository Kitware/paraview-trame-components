import paraview.web.venv
import ptc

web_app = ptc.Viewer()

with web_app.ui:
    ptc.HoverPoint()

    with web_app.col_left:
        ptc.PipelineBrowser()

    with web_app.side_top:
        with ptc.VRow(classes="ptc-region align-center"):
            ptc.VSpacer()
            ptc.OpenFileToggle()
            ptc.VBtn(
                icon=("enable_point_hover ? 'mdi-target' : 'mdi-crosshairs-off'",),
                click="enable_point_hover = !enable_point_hover",
                classes="mx-2",
            )
            ptc.VBtn(
                icon=(
                    "hover_mode === 'points' ? 'mdi-dots-triangle' : 'mdi-triangle-outline'",
                ),
                click="hover_mode = hover_mode === 'points' ? 'cells' : 'points'",
                classes="mx-2",
            )
            with ptc.ColorBy() as color:
                with color.prepend:
                    ptc.RepresentBy(classes="mr-2")
            ptc.VSpacer()

web_app.start()
