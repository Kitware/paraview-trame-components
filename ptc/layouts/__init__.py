from .col import ColumnsManager
from .factory import LayoutFactory
from .side import SideOverlayManager

__all__ = [
    "create_layout_manager",
]


def create_layout_manager(viewer):
    layout_manager = LayoutFactory(viewer)

    # Add more layout implementation
    layout_manager.register_manager(SideOverlayManager())
    layout_manager.register_manager(ColumnsManager())

    return layout_manager
