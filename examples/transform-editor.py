import paraview.web.venv
from paraview import simple

from ptc import Viewer, TransformEditor

render_view = simple.GetActiveViewOrCreate("RenderView")

# Will not be updated
sphere = simple.Sphere()
sphere.Radius = 1.0
simple.Show(sphere)

# Will be updated
box_source = simple.Box()
simple.Show(box_source)
simple.SetActiveSource(box_source)

web_app = Viewer()

with web_app.ui:
    with web_app.col_left:
        transform_editor = TransformEditor(
            show_translation=True,
            show_scale=True,
            show_origin=True,
            show_orientation=True,
            show_apply_button=True,
        )

        def z_scale_changed_2(_):
            print("Z Scale changed 2")

        transform_editor.typed_state.bind_changes(
            {transform_editor.typed_state.name.scale.z.value: z_scale_changed_2}
        )

        transform_editor.typed_state.data.scale.x.visibility = False
        transform_editor.typed_state.data.scale.y.visibility = False
        transform_editor.typed_state.data.scale.z.control_variant = "stacked"
        transform_editor.typed_state.data.translation.x.on_focus_lost_ctrl_callback_name = "on_focus_lost"

        @web_app.ctrl.set("on_focus_lost")
        def on_focus_lost():
            # Example of how to apply a translation when focus is lost on translation's x value
            transform_editor.apply_translation()
            simple.ResetCamera()
            web_app.ctrl.view_update()


@web_app.ctrl.set("on_apply_clicked")
def apply_clicked():
    print("Apply button clicked")


@web_app.state.change(transform_editor.typed_state.name.scale.z.value)
def z_scale_changed(**kwargs):
    print("Z Scale changed")


web_app.start()
