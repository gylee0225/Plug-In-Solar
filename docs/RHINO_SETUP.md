# Reopen Rhino 8: first component

1. Open Grasshopper and place a **Python 3 Script** component (not IronPython).
2. Use Script Mode. Add inputs/outputs exactly as listed in `COMPONENTS.md` for Location. Keep the `out` port.
3. Paste `grasshopper/components/location.py` into its editor.
4. Connect a Text Panel containing the full repository path to `project_root`. On this machine: `/Users/igayeon/Documents/GitHub/Plug-In-Solar`.
5. Connect latitude `52.52`, longitude `13.405`, timezone `Europe/Berlin`, and altitude_m `34`. These are demo values, not your project's assumed location.
6. In Shift + right-click advanced options, enable **Avoid Marshalling Inputs** and **Avoid Marshalling Outputs**. Use No Type Hint and Item access for Python object wires. Numerical list outputs will also remain Python objects under these settings; convert them separately for native Grasshopper list processing.
7. First execution installs the declared packages. The Location `site` output should be a Python location object. Errors appear on the component.

## Build the demo chain
Create the other Python components using the matching scripts and port guide. Supply the same `project_root` to each.

- **Clear Sky**: site from Location; start `2026-06-21`; end `2026-06-22`; step_minutes `60`.
- **Sun Position**: site from Location and weather from Clear Sky.
- **Panel Orientation**: normal `(0, -0.5, 0.8660254)`; north_deg `0`. Expected tilt ~30°, azimuth 180°.
- **Panel Irradiance**: weather and solar from upstream; tilt_deg and azimuth_deg from Panel Orientation; albedo `0.2`.
- **PV Power**: poa from Panel Irradiance; dc_capacity_w `800`; ac_limit_w `800`; air_temp_c `20`; wind_m_s `1`; gamma_pdc `-0.004`; losses_pct `14`.
- **Energy Yield**: power from PV Power; step_hours `1`.

Save this as `grasshopper/PlugInSolar.gh` after checking the chain. Every input is required, including scenario defaults shown here.

## Icons and toolbar
For initial reusable components, use Grasshopper's Create User Object workflow, set the category to `Plug-In Solar`, set the matching subcategory from the catalogue, and choose the matching 24 px PNG icon.

For a compiled toolbar, create a project in Rhino's `ScriptEditor`, add the saved `.gh` via **Add Components**, and assign the matching SVG icons and descriptions to each component. Use `plug_in_solar.svg` for the project icon. Retain the same source component instances after publishing to preserve their IDs.

Before distributing, add the Python package as a shared library and replace the development `project_root` bootstrap in each script with the configured library reference/import. The current path-based adapters are for local development. Build and test locally before publishing a Yak package. No public publishing is done by this starter.

## Development notes
Python caches imported modules. Restart Rhino after editing the core if old behavior persists. Avoid pointing the same Rhino session at multiple checkouts with the same package name.

## References
- [Python components, marshalling and user objects](https://developer.rhino3d.com/guides/scripting/scripting-gh-python/)
- [Script Editor package requirements](https://developer.rhino3d.com/guides/scripting/scripting-command/)
- [Creating script plugins and assigning icons](https://developer.rhino3d.com/guides/scripting/projects-create/)
- [pvlib documentation](https://pvlib-python.readthedocs.io/en/v0.13.0/)
