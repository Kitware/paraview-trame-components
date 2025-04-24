from pathlib import Path

import paraview


def find_paraview_root_directory():
    current = Path(paraview.__file__).resolve().parent.parent
    root_path = Path("/").resolve()  # This works on all operating systems
    while "paraview" not in current.name.lower():
        current = current.parent
        if current == root_path:
            # Failed to find it. Exit early.
            return None

    return current


def find_paraview_examples_directory(root_path):
    if root_path is None:
        return None

    for found_file in root_path.glob("**/can.ex2"):
        return found_file.parent

    return None


PARAVIEW_ROOT = find_paraview_root_directory()
PARAVIEW_EXAMPLES = find_paraview_examples_directory(PARAVIEW_ROOT)
PARAVIEW_EXAMPLES_CAN = PARAVIEW_EXAMPLES / "can.ex2" if PARAVIEW_EXAMPLES else None
PARAVIEW_EXAMPLES_DISKOUT = (
    PARAVIEW_EXAMPLES / "dick_out_ref.ex2" if PARAVIEW_EXAMPLES else None
)
PARAVIEW_EXAMPLES_HEAD = PARAVIEW_EXAMPLES / "headsq.vti" if PARAVIEW_EXAMPLES else None

__all__ = [
    "PARAVIEW_ROOT",
    "PARAVIEW_EXAMPLES",
    "PARAVIEW_EXAMPLES_CAN",
    "PARAVIEW_EXAMPLES_DISKOUT",
    "PARAVIEW_EXAMPLES_HEAD",
]
