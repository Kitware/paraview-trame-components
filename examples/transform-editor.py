import paraview.web.venv
from paraview import simple

from ptc import Viewer, TransformEditor

render_view = simple.GetActiveViewOrCreate("RenderView")

origin_sphere_source = simple.Sphere()
origin_sphere_source.Radius = 1.0
simple.Show(origin_sphere_source)

# Will be updated
transformed_box_source = simple.Box()
simple.Show(transformed_box_source)
simple.SetActiveSource(transformed_box_source)

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

        def z_scale_changed(_):
            print("Z Scale changed")

        transform_editor.typed_state.bind_changes(
            {transform_editor.typed_state.name.scale.z.value: z_scale_changed}
        )

        transform_editor.set_components_visibilities(
            {
                transform_editor.scale_name.x: False,
                transform_editor.scale_name.y: False,
            }
        )

        transform_editor.set_components_controls_variants(
            {
                transform_editor.scale_name.z: "stacked",
            }
        )

        def on_focus_lost():
            # Example of how to apply a translation when focus is lost on translation's x value
            print("on_focus_lost")
            transform_editor.apply_translation()
            simple.ResetCamera()
            web_app.ctrl.view_update()

        transform_editor.bind_components_on_focus_lost(
            {
                transform_editor.translation_name.x: on_focus_lost,
            }
        )

        def apply_clicked():
            print("Apply button clicked")

        transform_editor.bind_on_apply_button_clicked(apply_clicked)


web_app.start()
