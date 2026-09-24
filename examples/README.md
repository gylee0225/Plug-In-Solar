# Plug-In Solar example

Open `PlugInSolar_Example.gh` in Rhino 8 / Grasshopper. The `.ghx` file contains the same definition in XML form; use either file, not both.

The example uses all seven compiled Plug-In Solar components, wired from location and clear-sky irradiance through PV power to energy. Editable input panels set a Berlin location, one summer day, and 800 W DC / 800 W AC capacities. Panel orientation is stored as the front-face normal on the Panel Orientation component. The energy panel shows approximately **4.843 kWh** for these inputs.

This is synthetic clear-sky data, not measured weather or an annual forecast. The end date is exclusive. The weather sample interval is 60 minutes; the energy interval is 1 hour. If changing the interval, update both inputs consistently. Other PV model inputs use the component defaults (20 °C air, 1 m/s wind, -0.004/°C power coefficient, 14% lumped losses).

## Prerequisites

The compiled library must be loaded from `build/grasshopper/PlugInSolar.gha`, and the repository's `.venv` must contain pvlib. `scripts/build_plugin.sh` builds the library and writes the `.ghlink` in the Rhino 8 Grasshopper Libraries folder. It requires a .NET 7 SDK (`SOLAR_DOTNET` may specify an executable path) and Python 3.9–3.12. Restart Rhino after rebuilding a loaded library.

The compiled components use a small C# interface and invoke the existing Python calculation core. They have no `project_root` input: they locate the repository from the build folder. Keep the repository and build folder together. A fresh solve starts Python for each changed component; this starter may take several seconds, especially on first use.
