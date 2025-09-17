"""
FOAM_PrinterSetup_Clay
Creates a printer profile for paste/clay/concrete extrusion.
Supports Cartesian (rectangular bed) and Delta (circular bed) printers.
Outputs a list that plugs into FOAM_GcodeGenerator.

Author: Luis Borunda
GitHub: https://github.com/lborunda/rhinoFOAM
License: MIT License

Cite: Hierarchical Structures, Free Oriented Additive Manufacturing (FOAM)
Borunda, L., & Anaya, R. (2022). Hierarchical structures: Computational design and digital 3D printing. 
Journal of the International Association for Shell and Spatial Structures, 64(1). 
https://doi.org/10.20898/j.iass.2022.015
L. Borunda, "rhinoFOAM," GitHub repository, 2025. [Online]. Available: https://github.com/lborunda/rhinoFOAM
"""

import Rhino.Geometry as rg

def make_clay_profile(printer_type="Cartesian",
                      bx=None, by=None, bz=None, radius=None,
                      pressure=None, flow=None, retract=None, cure=None,
                      fr=None, clr=None):
    """
    Returns profile as a list (better for Grasshopper wiring):
    [ Mode, PrinterType, Params, BedX, BedY, BedZ, BedRadius, BedShape ]
    """

    # Safe defaults
    bx = bx if bx is not None else 300
    by = by if by is not None else 300
    bz = bz if bz is not None else 300
    radius = radius if radius is not None else 150

    pressure = pressure if pressure is not None else 4.0
    flow = flow if flow is not None else 10.0
    retract = retract if retract is not None else 0.5
    cure = cure if cure is not None else 0.0
    fr = fr if fr is not None else 800
    clr = clr if clr is not None else 5

    params = {
        "ExtrusionPressure": pressure,
        "FlowRate": flow,
        "RetractionDelay": retract,
        "CurePause": cure,
        "FeedRate": fr,
        "ClearanceHeight": clr
    }

    if printer_type == "Delta":
        bedshape = rg.Circle(rg.Plane.WorldXY, float(radius)).ToNurbsCurve()
        profile = ["Clay", "Delta", params, None, None, float(bz), float(radius), bedshape]
    else:  # Cartesian
        bedshape = rg.Rectangle3d(rg.Plane.WorldXY, float(bx), float(by)).ToNurbsCurve()
        profile = ["Clay", "Cartesian", params, float(bx), float(by), float(bz), None, bedshape]

    return profile


# -----------------------------
# Grasshopper I/O
# -----------------------------
# Convert numeric toggle into string if coming from GH (0 = Cartesian, 1 = Delta)
if PrinterType == 1:
    PrinterType = "Delta"
elif PrinterType == 0:
    PrinterType = "Cartesian"

Profile = make_clay_profile(
    printer_type=PrinterType,
    bx=BedX, by=BedY, bz=BedZ,
    radius=BedRadius,
    pressure=ExtrusionPressure, flow=FlowRate,
    retract=RetractionDelay, cure=CurePause,
    fr=FeedRate, clr=ClearanceHeight
)

