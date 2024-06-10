# ParaView Trame Components

This project gather helper classes that can be used with ParaView to create quickly and simply web solution for interacting with your data.

## Usage example

The `./examples/` directory gather simple Python scripts using ParaView and exposing them as standalone trame applications.

## Virtual Environment setup

Since ParaView does not come with trame, you need to create a virtual environment that brings all the missing dependency for paraview to use.

```bash
# Create and activate venv
python3.10 -m venv .venv
source .venv/bin/activate

# Install published package
pip install paraview-trame-components

# Let ParaView know about the location of that venv
export PV_VENV=$PWD/.venv
```

## Running examples

```bash
# Adjust path to point to your ParaView executable
export PVPYTHON=/Applications/ParaView-5.12.0.app/Contents/bin/pvpython

# Run the scripts
$PVPYTHON --force-offscreen-rendering ./examples/cone.py
$PVPYTHON --force-offscreen-rendering ./examples/cone-with-slider.py
$PVPYTHON --force-offscreen-rendering ./examples/wavelet-contour-state.py
$PVPYTHON --force-offscreen-rendering ./examples/pipeline.py
$PVPYTHON --force-offscreen-rendering ./examples/selection.py
```

## Scripts structure

Each script add `import paraview.web.venv` at the top to enable your virtual environment via the `PV_VENV` environment variable.

Then we use the ptc (ParaView Trame Components) package to quickly create a trame application to view the data.

The `wavelet-contour-state.py` script was created by ParaView when saving its state as a Python file. Then we added few lines at the end to create an interactive web viewer.

## Check code

```bash
# one time
pip install ".[dev]"
pre-commit install

# check but automatic on commit
pre-commit run --all-files
```

## ParaView code example

```python
import paraview.web.venv
from ptc import Viewer
from paraview import simple

cone = simple.Cone()
simple.Show()
simple.Render()

# Make it a web app
web_app = Viewer()
web_app.start()
```

And if you want to add some UI

```python
import paraview.web.venv
from paraview import simple

from ptc import Viewer
from trame.widgets.vuetify3 import VSlider

cone = simple.Cone()
simple.Show()
simple.Render()

# Make it a web app
web_app = Viewer()

with web_app.side_top:
    VSlider(
        v_model=("resolution", 6),
        min=3, max=60, step=1,
    )

@web_app.state.change("resolution")
def on_resolution_change(resolution, **kwargs):
    cone.Resolution = resolution
    web_app.update()

web_app.start()
```

## Example in image

| ![Code](https://raw.githubusercontent.com/Kitware/paraview-trame-components/main/.web-app-input.png) | ![Web App](https://raw.githubusercontent.com/Kitware/paraview-trame-components/main/.web-app-output.png) |
| :-------------------------: |  :----------------------------: | 
| Write some python code      |  And get a web app              | 