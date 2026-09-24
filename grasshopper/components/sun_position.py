#! python 3
# requirements: pvlib==0.13.0, numpy==1.26.4, pandas==2.2.3, scipy==1.13.1
# Rhino 8 Python 3 / Script Mode. Configure ports per docs/COMPONENTS.md.
# project_root is the folder containing pyproject.toml; all inputs Item access.
import sys
from pathlib import Path
import Grasshopper.Kernel as GH

solar = None
altitude_deg = None
azimuth_deg = None
try:
    source = Path(str(project_root)).expanduser() / "src"
    if not (source / "plug_in_solar" / "__init__.py").is_file():
        raise ValueError("Set project_root to your Plug-In-Solar repository folder.")
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))
    from plug_in_solar import core
    solar = core.sun_position(site, weather.index)
    altitude_deg = solar.apparent_elevation.tolist()
    azimuth_deg = solar.azimuth.tolist()
except Exception as exc:
    ghenv.Component.AddRuntimeMessage(GH.GH_RuntimeMessageLevel.Error, str(exc))
