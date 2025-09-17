"""
FOAM_PrinterSetup_Pen
Creates a printer profile for pen-plotter or motion-only setups.
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

def make_pen_profile(printer_type="Cartesian",
                     bx=None, by=None, bz=None, radius=None,
                     up=None, down=None, delay=None, fr=None):
    """
    Returns profile as a list (better for Grasshopper wiring):
    [ Mode, PrinterType, Params, BedX, BedY, BedZ, BedRadius, BedShape ]
    """

    # Safe defaults
    bx = bx if bx is not None else 300
    by = by if by is not None else 300
    bz = bz if bz is not None else 300
    radius = radius if radius is not None else 150

    up = up if up is not None else 5
    down = down if down is not None else 0.2
    delay = delay if delay is not None else 100
    fr = fr if fr is not None else 1000

    params = {
        "PenUpHeight": up,
        "PenDownOffset": down,
        "PenDownDelay": delay,
        "FeedRate": fr
    }

    if printer_type == "Delta":
        bedshape = rg.Circle(rg.Plane.WorldXY, float(radius)).ToNurbsCurve()
        profile = ["Pen", "Delta", params, None, None, float(bz), float(radius), bedshape]
    else:  # Cartesian
        bedshape = rg.Rectangle3d(rg.Plane.WorldXY, float(bx), float(by)).ToNurbsCurve()
        profile = ["Pen", "Cartesian", params, float(bx), float(by), float(bz), None, bedshape]

    return profile


# -----------------------------
# Grasshopper I/O
# -----------------------------
# Convert numeric toggle into string if coming from GH (0 = Cartesian, 1 = Delta; or string)

PrinterType=(int(PrinterType))
if PrinterType == 1:
    PrinterType = "Delta"
elif PrinterType == 0:
    PrinterType = "Cartesian"

print (PrinterType)

Profile = make_pen_profile(
    printer_type=PrinterType,
    bx=BedX, by=BedY, bz=BedZ,
    radius=BedRadius,
    up=PenUpHeight, down=PenDownOffset,
    delay=PenDownDelay, fr=FeedRate
)

