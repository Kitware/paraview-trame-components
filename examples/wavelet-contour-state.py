# state file generated using paraview version 5.12.0
import paraview

paraview.compatibility.major = 5
paraview.compatibility.minor = 12

#### import the simple module from the paraview
from paraview.simple import *

#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# get the material library
materialLibrary1 = GetMaterialLibrary()

# Create a new 'Render View'
renderView1 = CreateView("RenderView")
renderView1.ViewSize = [1574, 1074]
renderView1.AxesGrid = "Grid Axes 3D Actor"
renderView1.StereoType = "Crystal Eyes"
renderView1.CameraPosition = [0.0, 0.0, 66.92130429902464]
renderView1.CameraFocalDisk = 1.0
renderView1.CameraParallelScale = 17.320508075688775
renderView1.LegendGrid = "Legend Grid Actor"
renderView1.BackEnd = "OSPRay raycaster"
renderView1.OSPRayMaterialLibrary = materialLibrary1

SetActiveView(None)

# ----------------------------------------------------------------
# setup view layouts
# ----------------------------------------------------------------

# create new layout object 'Layout #1'
layout1 = CreateLayout(name="Layout #1")
layout1.AssignView(0, renderView1)
layout1.SetSize(1574, 1074)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'Wavelet'
wavelet1 = Wavelet(registrationName="Wavelet1")

# create a new 'Contour'
contour1 = Contour(registrationName="Contour1", Input=wavelet1)
contour1.ContourBy = ["POINTS", "RTData"]
contour1.Isosurfaces = [157.0909652709961]
contour1.PointMergeMethod = "Uniform Binning"

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from wavelet1
wavelet1Display = Show(wavelet1, renderView1, "UniformGridRepresentation")

# trace defaults for the display properties.
wavelet1Display.Representation = "Outline"
wavelet1Display.ColorArrayName = ["POINTS", ""]
wavelet1Display.SelectTCoordArray = "None"
wavelet1Display.SelectNormalArray = "None"
wavelet1Display.SelectTangentArray = "None"
wavelet1Display.OSPRayScaleArray = "RTData"
wavelet1Display.OSPRayScaleFunction = "Piecewise Function"
wavelet1Display.Assembly = ""
wavelet1Display.SelectOrientationVectors = "None"
wavelet1Display.ScaleFactor = 2.0
wavelet1Display.SelectScaleArray = "RTData"
wavelet1Display.GlyphType = "Arrow"
wavelet1Display.GlyphTableIndexArray = "RTData"
wavelet1Display.GaussianRadius = 0.1
wavelet1Display.SetScaleArray = ["POINTS", "RTData"]
wavelet1Display.ScaleTransferFunction = "Piecewise Function"
wavelet1Display.OpacityArray = ["POINTS", "RTData"]
wavelet1Display.OpacityTransferFunction = "Piecewise Function"
wavelet1Display.DataAxesGrid = "Grid Axes Representation"
wavelet1Display.PolarAxes = "Polar Axes Representation"
wavelet1Display.ScalarOpacityUnitDistance = 1.7320508075688774
wavelet1Display.OpacityArrayName = ["POINTS", "RTData"]
wavelet1Display.ColorArray2Name = ["POINTS", "RTData"]
wavelet1Display.IsosurfaceValues = [157.0909652709961]
wavelet1Display.SliceFunction = "Plane"
wavelet1Display.Slice = 10
wavelet1Display.SelectInputVectors = [None, ""]
wavelet1Display.WriteLog = ""

# init the 'Piecewise Function' selected for 'ScaleTransferFunction'
wavelet1Display.ScaleTransferFunction.Points = [
    37.35310363769531,
    0.0,
    0.5,
    0.0,
    276.8288269042969,
    1.0,
    0.5,
    0.0,
]

# init the 'Piecewise Function' selected for 'OpacityTransferFunction'
wavelet1Display.OpacityTransferFunction.Points = [
    37.35310363769531,
    0.0,
    0.5,
    0.0,
    276.8288269042969,
    1.0,
    0.5,
    0.0,
]

# show data from contour1
contour1Display = Show(contour1, renderView1, "GeometryRepresentation")

# get 2D transfer function for 'RTData'
rTDataTF2D = GetTransferFunction2D("RTData")

# get color transfer function/color map for 'RTData'
rTDataLUT = GetColorTransferFunction("RTData")
rTDataLUT.TransferFunction2D = rTDataTF2D
rTDataLUT.RGBPoints = [
    157.09097290039062,
    0.231373,
    0.298039,
    0.752941,
    157.10659790039062,
    0.865003,
    0.865003,
    0.865003,
    157.12222290039062,
    0.705882,
    0.0156863,
    0.14902,
]
rTDataLUT.ScalarRangeInitialized = 1.0

# trace defaults for the display properties.
contour1Display.Representation = "Surface"
contour1Display.ColorArrayName = ["POINTS", "RTData"]
contour1Display.LookupTable = rTDataLUT
contour1Display.SelectTCoordArray = "None"
contour1Display.SelectNormalArray = "Normals"
contour1Display.SelectTangentArray = "None"
contour1Display.OSPRayScaleArray = "RTData"
contour1Display.OSPRayScaleFunction = "Piecewise Function"
contour1Display.Assembly = ""
contour1Display.SelectOrientationVectors = "None"
contour1Display.ScaleFactor = 2.0
contour1Display.SelectScaleArray = "RTData"
contour1Display.GlyphType = "Arrow"
contour1Display.GlyphTableIndexArray = "RTData"
contour1Display.GaussianRadius = 0.1
contour1Display.SetScaleArray = ["POINTS", "RTData"]
contour1Display.ScaleTransferFunction = "Piecewise Function"
contour1Display.OpacityArray = ["POINTS", "RTData"]
contour1Display.OpacityTransferFunction = "Piecewise Function"
contour1Display.DataAxesGrid = "Grid Axes Representation"
contour1Display.PolarAxes = "Polar Axes Representation"
contour1Display.SelectInputVectors = ["POINTS", "Normals"]
contour1Display.WriteLog = ""

# init the 'Piecewise Function' selected for 'ScaleTransferFunction'
contour1Display.ScaleTransferFunction.Points = [
    157.09097290039062,
    0.0,
    0.5,
    0.0,
    157.12222290039062,
    1.0,
    0.5,
    0.0,
]

# init the 'Piecewise Function' selected for 'OpacityTransferFunction'
contour1Display.OpacityTransferFunction.Points = [
    157.09097290039062,
    0.0,
    0.5,
    0.0,
    157.12222290039062,
    1.0,
    0.5,
    0.0,
]

# setup the color legend parameters for each legend in this view

# get color legend/bar for rTDataLUT in view renderView1
rTDataLUTColorBar = GetScalarBar(rTDataLUT, renderView1)
rTDataLUTColorBar.Title = "RTData"
rTDataLUTColorBar.ComponentTitle = ""

# set color bar visibility
rTDataLUTColorBar.Visibility = 1

# show color legend
contour1Display.SetScalarBarVisibility(renderView1, True)

# ----------------------------------------------------------------
# setup color maps and opacity maps used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get opacity transfer function/opacity map for 'RTData'
rTDataPWF = GetOpacityTransferFunction("RTData")
rTDataPWF.Points = [
    157.09097290039062,
    0.0,
    0.5,
    0.0,
    157.12222290039062,
    1.0,
    0.5,
    0.0,
]
rTDataPWF.ScalarRangeInitialized = 1

# ----------------------------------------------------------------
# setup animation scene, tracks and keyframes
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get the time-keeper
timeKeeper1 = GetTimeKeeper()

# initialize the timekeeper

# get time animation track
timeAnimationCue1 = GetTimeTrack()

# initialize the animation track

# get animation scene
animationScene1 = GetAnimationScene()

# initialize the animation scene
animationScene1.ViewModules = renderView1
animationScene1.Cues = timeAnimationCue1
animationScene1.AnimationTime = 0.0

# initialize the animation scene

# ----------------------------------------------------------------
# restore active source
SetActiveSource(contour1)
# ----------------------------------------------------------------

# ---------------------------------------------------------
# Add-on to turn ParaView Python script to a web app
# ---------------------------------------------------------

import paraview.web.venv
from ptc import Viewer
from trame.widgets.vuetify3 import VSlider


web_app = Viewer()

# add-on UI
with web_app.side_top:
    VSlider(
        v_model=("value", contour1.Isosurfaces[0]),
        min=37,
        max=276,
        step=0.5,
        color="primary",
        style="margin: 0 100px;",
    )


@web_app.state.change("value")
def on_contour_value_change(value, **kwargs):
    contour1.Isosurfaces = [value]
    web_app.update()


web_app.start()
