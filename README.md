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
pip install ptc

# Let ParaView know about the location of that venv
export PV_VENV=$PWD/.venv
```

## Running examples

```bash
# Adjust path to point to your executable
export PVPYTHON=/Applications/ParaView-5.12.0.app/Contents/bin/pvpython

# Run the scripts
$PVPYTHON --force-offscreen-rendering ./examples/cone.py
$PVPYTHON --force-offscreen-rendering ./examples/cone_width_slider.py
$PVPYTHON --force-offscreen-rendering ./examples/wavelet-contour-state.py
```

## Scripts structure

Each script add `import paraview.web.venv` at the top to enable your virtual environment via the `PV_VENV` environment variable.

Then we use the ptc (ParaView Trame Components) package to quickly create a trame application to view the data.

The `wavelet-contour-state.py` script was created by ParaView when saving its state as a Python file. Then we added few lines at the end to create an interactive web viewer.

## Check code

`pre-commit run --all-files`