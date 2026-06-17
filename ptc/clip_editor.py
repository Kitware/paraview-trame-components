import numpy as np
from paraview import simple

from .plane_widget_editor import PlaneWidgetEditor


class ClipEditor(PlaneWidgetEditor):
    def __init__(self):
        super().__init__(simple.Clip(), "Clip editor", "clip_editor")

    def _show(self, *args, **kwargs):
        if self.source is not None:
            if self.state[self.show_key]:
                simple.Hide(self.source)
            else:
                simple.Show(self.source)
        super()._show(*args, **kwargs)

    def _on_origin_change(self, *_args, **_kwargs):
        origin = self.origin_editor.value
        if any(not isinstance(v, float) for v in origin):
            return
        self.pv_filter.ClipType.Origin = origin

        self.plane.SetOrigin(origin)
        self.ctrl.view_update()

    def _on_normal_change(self, *_args, **_kwargs):
        normal = self.normal_editor.value
        if (
            any(not isinstance(v, float) for v in normal)
            or np.linalg.norm(normal) < 1e-6
        ):
            return

        self.pv_filter.ClipType.Normal = normal

        self.plane.SetNormal(normal)
        self.ctrl.view_update()
