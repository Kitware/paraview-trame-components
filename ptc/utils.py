from pathlib import Path

import paraview


def find_paraview_root_directory():
    current = Path(paraview.__file__).resolve().parent.parent
    while "paraview" not in current.name.lower():
        current = current.parent
    return current


def find_paraview_examples_directory(root_path):
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
