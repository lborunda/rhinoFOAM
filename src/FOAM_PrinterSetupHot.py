"""
FOAM_PrinterSetup_Hot
Creates a printer profile for thermoplastic FDM (Hot) printing.
Supports Cartesian (rectangular bed) and Delta (circular bed) printers.
Outputs a list that plugs into FOAM_GcodeGenerator.

Author: Luis Borunda
GitHub: https://github.com/lborunda/rhinoFOAM
License: MIT License

Cite: Hierarchical Structures, Free Oriented Additive Manufacturing (FOAM)
Borunda, L., & Anaya, R. (2022). Hierarchical structures: Computational design and digital 3D printing. Journal of the International Association for Shell and Spatial Structures, 64(1). https://doi.org/10.20898/j.iass.2022.015
L. Borunda, "rhinoFOAM," GitHub repository, 2025. [Online]. Available: https://github.com/lborunda/rhinoFOAM
"""

import Rhino.Geometry as rg

def make_hot_profile(printer_type="Cartesian",
                     bx=None, by=None, bz=None, radius=None,
                     nozzle=None, bed=None, mult=None,
                     fr=None, clr=None):
    """
    Returns profile as a list (better for Grasshopper wiring):
    [ Mode, PrinterType, Params, BedX, BedY, BedZ, BedRadius, BedShape ]
    """

    # Use safe defaults if None
    bx = bx if bx is not None else 300
    by = by if by is not None else 300
    bz = bz if bz is not None else 300
    radius = radius if radius is not None else 150

    nozzle = nozzle if nozzle is not None else 210
    bed = bed if bed is not None else 30
    mult = mult if mult is not None else 0.20
    fr = fr if fr is not None else 1500
    clr = clr if clr is not None else 5

    params = {
        "NozzleTemp": nozzle,
        "BedTemp": bed,
        "ExtrusionMultiplier": mult,
        "FeedRate": fr,
        "ClearanceHeight": clr
    }

    if printer_type == "Delta":
        bedshape = rg.Circle(rg.Plane.WorldXY, float(radius)).ToNurbsCurve()
        profile = ["Hot", "Delta", params, None, None, float(bz), float(radius), bedshape]
    else:  # Cartesian
        bedshape = rg.Rectangle3d(rg.Plane.WorldXY, float(bx), float(by)).ToNurbsCurve()
        profile = ["Hot", "Cartesian", params, float(bx), float(by), float(bz), None, bedshape]

    return profile


# -----------------------------
# Grasshopper I/O
# -----------------------------
# Convert numeric toggle into string if coming from GH (0 = Cartesian, 1 = Delta)
if PrinterType == 1:
    PrinterType = "Delta"
elif PrinterType == 0:
    PrinterType = "Cartesian"

Profile = make_hot_profile(
    printer_type=PrinterType,
    bx=BedX, by=BedY, bz=BedZ,
    radius=BedRadius,
    nozzle=NozzleTemp, bed=BedTemp,
    mult=ExtrusionMultiplier,
    fr=FeedRate, clr=ClearanceHeight
)
