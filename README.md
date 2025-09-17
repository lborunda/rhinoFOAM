# rhinoFOAM

**FOAM_GcodeGenerator** converts Rhino/Grasshopper polylines into G-code using **Free-Oriented Additive Manufacturing (FOAM)** principles.  
Supports multiple **printer modes** and **printer types** (Cartesian & Delta).  

---

## 📦 Components

- **FOAM_PrinterSetup_Hot** → FDM / thermoplastic printing (heated nozzle + bed)  
- **FOAM_PrinterSetup_Clay** → Clay / paste / concrete extrusion (pressure-based)  
- **FOAM_PrinterSetup_Pen** → Pen-plotter or motion-only setups (no extrusion)  
- **FOAM_GcodeGenerator** → Converts toolpaths into validated, bounded G-code  

---

## 🔧 Profile Format

All printer setup components output **lists** for easier wiring in Grasshopper:

```
[ Mode, PrinterType, Params, BedX, BedY, BedZ, BedRadius, BedShape ]
```

- **Mode** → `"Hot"`, `"Clay"`, or `"Pen"`  
- **PrinterType** → `"Cartesian"` or `"Delta"`  
- **Params** → dictionary of parameters (varies by mode)  
- **BedX, BedY, BedZ** → Cartesian bed dimensions (use `None` if Delta)  
- **BedRadius, BedZ** → Delta bed dimensions (use `None` if Cartesian)  
- **BedShape** → Rhino curve for visualization (`Rectangle` or `Circle`)  

---

## ⚙️ Examples

### Hot (Cartesian, 300×300×300 mm)

```python
Profile = [
  "Hot", "Cartesian",
  {"NozzleTemp": 210, "BedTemp": 30, "ExtrusionMultiplier": 0.2,
   "FeedRate": 1500, "ClearanceHeight": 5},
  300, 300, 300, None,
  <Rectangle NurbsCurve>
]
```

### Clay (Delta, radius 150 mm, height 300 mm)

```python
Profile = [
  "Clay", "Delta",
  {"ExtrusionPressure": 4.0, "FlowRate": 10.0, "RetractionDelay": 0.5,
   "CurePause": 0.0, "FeedRate": 800, "ClearanceHeight": 5},
  None, None, 300, 150,
  <Circle NurbsCurve>
]
```

### Pen (Cartesian, 200×200×200 mm)

```python
Profile = [
  "Pen", "Cartesian",
  {"PenUpHeight": 5, "PenDownOffset": 0.2,
   "PenDownDelay": 100, "FeedRate": 1000},
  200, 200, 200, None,
  <Rectangle NurbsCurve>
]
```

---

## 📊 Parameter Tables

### Hot (FDM thermoplastic)

| Param              | Default | Description                     |
|--------------------|---------|---------------------------------|
| `NozzleTemp`       | 210 °C  | Hotend temperature              |
| `BedTemp`          | 30 °C   | Heated bed temperature          |
| `ExtrusionMultiplier` | 0.20 | Extrusion volume scaling        |
| `FeedRate`         | 1500    | Motion feedrate (mm/min)        |
| `ClearanceHeight`  | 5       | Lift height between paths       |

### Clay (Paste/Concrete)

| Param               | Default | Description                     |
|---------------------|---------|---------------------------------|
| `ExtrusionPressure` | 4.0 bar | Syringe/pressure setting        |
| `FlowRate`          | 10.0    | Material flow rate              |
| `RetractionDelay`   | 0.5 s   | Pause before retracting pressure|
| `CurePause`         | 0.0 s   | Optional curing dwell time      |
| `FeedRate`          | 800     | Motion feedrate (mm/min)        |
| `ClearanceHeight`   | 5       | Lift height between paths       |

### Pen (Plotter/Motion-only)

| Param            | Default | Description                     |
|------------------|---------|---------------------------------|
| `PenUpHeight`    | 5 mm    | Z-height when pen is lifted     |
| `PenDownOffset`  | 0.2 mm  | Offset below surface for plotting |
| `PenDownDelay`   | 100 ms  | Delay after lowering pen        |
| `FeedRate`       | 1000    | Motion feedrate (mm/min)        |

---

## 🖨️ FOAM_GcodeGenerator

**Inputs**

- `Geometry` → Polylines or PolylineCurves (toolpaths, ordered by Z for printing)  
- `Profile` → List from any FOAM_PrinterSetup component  
- `BaseCode` → Optional header/footer G-code lines  
- `FilePath` → Optional path to save G-code file  

**Outputs**

- `Gcode` → Full list of G-code strings  
- `Preview` → Rhino polylines for visualization  
- `PreviewText` → Short preview (first 30 lines)  
- `Report` → Debug info + warnings  
- `Bed` → Bed outline curve (rectangle or circle)  
- `BadPts`, `BadSegs`, `WarnDots` → Out-of-bounds diagnostics  

---

## 📖 Citation

Borunda, L., & Anaya, R. (2022). *Hierarchical structures: Computational design and digital 3D printing.*  
Journal of the International Association for Shell and Spatial Structures, 64(1).  
https://doi.org/10.20898/j.iass.2022.015  

L. Borunda, *rhinoFOAM*, GitHub repository, 2025.  
[Online]. Available: https://github.com/lborunda/rhinoFOAM
