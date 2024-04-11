import paraview.web.venv
from pathlib import Path
from paraview import simple
from ptc import Viewer

IMAGE_STATE = str(Path(__file__).with_name("wavelet-state.png").resolve())

simple.LoadState(IMAGE_STATE)
web_app = Viewer(from_state=True)
web_app.start()
