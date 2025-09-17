"""
FOAM_GcodeGenerator
Converts Rhino/Grasshopper polylines into G-code using FOAM principles.

Supports 3 modes:
  - "Hot"  (thermoplastic FDM, heated nozzle/bed)
  - "Clay" (concrete / paste extrusion, pressure-based)
  - "Pen"  (pen-plotter or cold motion, no extrusion)

Supports both Cartesian (BedX, BedY, BedZ) and Delta (BedRadius, BedZ) printers.

Author: Luis Borunda
GitHub: https://github.com/lborunda/rhinoFOAM
License: MIT License

Cite: Hierarchical Structures, Free Oriented Additive Manufacturing (FOAM)
Borunda, L., & Anaya, R. (2022). Hierarchical structures: Computational design and digital 3D printing. 
Journal of the International Association for Shell and Spatial Structures, 64(1). 
https://doi.org/10.20898/j.iass.2022.015
L. Borunda, "rhinoFOAM," GitHub repository, 2025. 
[Online]. Available: https://github.com/lborunda/rhinoFOAM
"""

import ast
import Rhino.Geometry as rg
from math import sqrt

# -----------------------------
# Helpers
# -----------------------------
def extract_points(pl):
    """Extracts Point3d coords from Polyline or PolylineCurve."""
    coords = []
    if isinstance(pl, rg.Polyline):
        coords = [rg.Point3d(round(pt.X,3), round(pt.Y,3), round(pt.Z,3)) for pt in pl]
    elif isinstance(pl, rg.PolylineCurve):
        success, poly = pl.TryGetPolyline()
        if success:
            coords = [rg.Point3d(round(pt.X,3), round(pt.Y,3), round(pt.Z,3)) for pt in poly]
    return coords

def in_bounds_cart(x, y, z, bx, by, bz):
    reasons = []
    if x < 0: reasons.append("X<0")
    if y < 0: reasons.append("Y<0")
    if z < 0: reasons.append("Z<0")
    if x > bx: reasons.append("X>BedX")
    if y > by: reasons.append("Y>BedY")
    if z > bz: reasons.append("Z>BedZ")
    return (len(reasons) == 0, reasons)

def in_bounds_delta(x, y, z, radius, bz):
    reasons = []
    r = sqrt(x*x + y*y)
    if r > radius: reasons.append("r>BedRadius")
    if z < 0: reasons.append("Z<0")
    if z > bz: reasons.append("Z>BedZ")
    return (len(reasons) == 0, reasons)


# -----------------------------
# Main
# -----------------------------
def generate_gcode(geometry, profile=None, base_code=None):
    # Handle string input (from GH sometimes)
    if isinstance(profile, str):
        try:
            profile = ast.literal_eval(profile)
        except:
            profile = None

    # Defaults
    mode = "Pen"
    printer_type = "Cartesian"
    bedX, bedY, bedZ = 300, 300, 300
    bedRadius = 150
    params = {}
    Bed = None

    if profile:
        if isinstance(profile, dict):
            # Legacy dict format
            mode = profile.get("Mode", "Pen")
            printer_type = profile.get("PrinterType", "Cartesian")
            params = profile.get("Params", {})
            Bed = profile.get("BedShape", None)

            if printer_type == "Delta":
                bedRadius = profile.get("BedRadius", bedRadius)
                bedZ = profile.get("BedZ", bedZ)
                if Bed is None:
                    Bed = rg.Circle(rg.Plane.WorldXY, bedRadius).ToNurbsCurve()
            else:
                bedX = profile.get("BedX", bedX)
                bedY = profile.get("BedY", bedY)
                bedZ = profile.get("BedZ", bedZ)
                if Bed is None:
                    Bed = rg.Rectangle3d(rg.Plane.WorldXY, bedX, bedY).ToNurbsCurve()

        elif isinstance(profile, list):
            # List format: [Mode, PrinterType, Params, BedX, BedY, BedZ, BedRadius, BedShape]
            mode = profile[0] if len(profile) > 0 else "Pen"
            printer_type = profile[1] if len(profile) > 1 else "Cartesian"
            params = profile[2] if len(profile) > 2 and isinstance(profile[2], dict) else {}

            if printer_type == "Delta":
                bedZ = profile[5] if len(profile) > 5 and profile[5] is not None else bedZ
                bedRadius = profile[6] if len(profile) > 6 and profile[6] is not None else bedRadius
                Bed = profile[7] if len(profile) > 7 else rg.Circle(rg.Plane.WorldXY, bedRadius).ToNurbsCurve()
            else:  # Cartesian
                bedX = profile[3] if len(profile) > 3 and profile[3] is not None else bedX
                bedY = profile[4] if len(profile) > 4 and profile[4] is not None else bedY
                bedZ = profile[5] if len(profile) > 5 and profile[5] is not None else bedZ
                Bed = profile[7] if len(profile) > 7 else rg.Rectangle3d(rg.Plane.WorldXY, bedX, bedY).ToNurbsCurve()

    print(f"[DEBUG] Mode={mode}, PrinterType={printer_type}, bedX={bedX}, bedY={bedY}, bedZ={bedZ}, bedRadius={bedRadius}")

    # -----------------------------
    # Safety checks
    # -----------------------------
    status = "OK"
    preview_paths = []
    violations = 0
    BadPts, BadSegs, WarnDots = [], [], []

    if geometry:
        for pl in geometry:
            coords = extract_points(pl)
            if not coords:
                continue

            # check each point
            for pt in coords:
                x, y, z = pt.X, pt.Y, pt.Z
                if printer_type == "Delta":
                    ok, reasons = in_bounds_delta(x, y, z, bedRadius, bedZ)
                else:
                    ok, reasons = in_bounds_cart(x, y, z, bedX, bedY, bedZ)
                if not ok:
                    violations += 1
                    BadPts.append(pt)
                    WarnDots.append(rg.TextDot(", ".join(reasons), pt))

            # check each segment midpoint too
            for i in range(1, len(coords)):
                a, b = coords[i-1], coords[i]
                mid = rg.Point3d((a.X+b.X)/2, (a.Y+b.Y)/2, (a.Z+b.Z)/2)

                if printer_type == "Delta":
                    okA, _ = in_bounds_delta(a.X, a.Y, a.Z, bedRadius, bedZ)
                    okB, _ = in_bounds_delta(b.X, b.Y, b.Z, bedRadius, bedZ)
                    okM, _ = in_bounds_delta(mid.X, mid.Y, mid.Z, bedRadius, bedZ)
                    if not (okA and okB and okM):
                        BadSegs.append(rg.LineCurve(a, b))
                else:
                    okA, _ = in_bounds_cart(a.X, a.Y, a.Z, bedX, bedY, bedZ)
                    okB, _ = in_bounds_cart(b.X, b.Y, b.Z, bedX, bedY, bedZ)
                    if not (okA and okB):
                        BadSegs.append(rg.LineCurve(a, b))

    if violations > 0:
        status = f"⚠ Out of bounds: {violations} point(s)"
        try:
            import Grasshopper as gh
            ghenv.Component.AddRuntimeMessage(
                gh.Kernel.GH_RuntimeMessageLevel.Warning, status
            )
        except:
            pass

    # -----------------------------
    # Base G-code header
    # -----------------------------
    gcode = []
    if base_code:
        gcode.extend(base_code)
    else:
        gcode.append("; FOAM G-code Generator")
        gcode.append("G28 ; Home all axes")
        if mode == "Hot":
            gcode.append(f"M104 S{params.get('NozzleTemp', 210)} ; set nozzle temp")
            gcode.append(f"M140 S{params.get('BedTemp', 30)} ; set bed temp")
        gcode.append("G92 E0 ; Reset extrusion")

    # -----------------------------
    # Motion kernel
    # -----------------------------
    extrusion = 0
    clearance = params.get("ClearanceHeight", 5)
    feedrate = params.get("FeedRate", 1500)

    for pl in geometry:
        coords = extract_points(pl)
        if not coords:
            continue

        # Preview polyline
        poly_prev = rg.Polyline()
        for pt in coords:
            poly_prev.Add(pt)
        preview_paths.append(poly_prev)

        # Generate G-code
        for j, pt in enumerate(coords):
            x, y, z = pt.X, pt.Y, pt.Z

            if j == 0:
                gcode.append(f"; Start path")
                gcode.append(f"G1 X{x} Y{y} Z{z+clearance} F2000 ; move above start")
                gcode.append(f"G1 X{x} Y{y} Z{z} F{feedrate} ; descend to start")
            else:
                dist = coords[j-1].DistanceTo(pt)
                if mode == "Hot":
                    extrusion += dist * params.get("ExtrusionMultiplier", 0.20)
                    gcode.append(f"G1 X{x} Y{y} Z{z} E{extrusion:.4f} F{feedrate}")
                else:  # Clay and Pen = no extrusion
                    gcode.append(f"G1 X{x} Y{y} Z{z} F{feedrate}")

            if j == len(coords)-1:
                gcode.append(f"; End path")
                gcode.append(f"G1 Z{z+clearance} F2000 ; lift tool")

    # -----------------------------
    # Footer
    # -----------------------------
    gcode.append("; End of FOAM print")
    if mode == "Hot":
        gcode.append("M104 S0 ; turn off hotend")
        gcode.append("M140 S0 ; turn off bed")
    gcode.append("M107 ; fans off")
    gcode.append("G28 X0 ; home X")
    gcode.append("M84 ; disable motors")

    return gcode, preview_paths, status, Bed, BadPts, BadSegs, WarnDots


# -----------------------------
# Grasshopper IO
# -----------------------------
gcode, preview, status, Bed, BadPts, BadSegs, WarnDots = generate_gcode(Geometry, Profile, BaseCode)

# Full G-code (heavy, for saving)
Gcode = gcode      

# Short preview
PreviewText = "\n".join(gcode[:30]) + f"\n... ({len(gcode)} lines total)" if gcode else "⚠ No G-code generated"

# Toolpath preview polylines
Preview = preview  

# Debug info
Report = f"Geometry: {len(Geometry) if Geometry else 0}, Paths: {len(preview)}, G-code lines: {len(gcode)}, Status: {status}"

# Visualization outputs
Bed = Bed
BadPts = BadPts
BadSegs = BadSegs
WarnDots = WarnDots

# Save to file if path provided
if FilePath:
    try:
        with open(FilePath, "w") as f:
            f.write("\n".join(gcode))
    except Exception as e:
        Report = f"⚠ Failed to save G-code: {e}"
