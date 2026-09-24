# Plug-In Solar
A Rhino 8 / Grasshopper Python 3 starter for a university plug-in PV project.

## Included
- Seven Python component scripts and a machine-readable port/icon catalogue.
- A separate `plug_in_solar` calculation package using pvlib.
- Original light/dark SVG icons and 24/48 px PNG exports.
- A synthetic clear-sky example and calculation checks.

A compiled Rhino 8 library is available in `build/grasshopper/PlugInSolar.gha`. Rebuild and install its library link with `scripts/build_plugin.sh`. Open [the wired example](examples/PlugInSolar_Example.gh), or its [GHX equivalent](examples/PlugInSolar_Example.ghx). See [example notes](examples/README.md) for setup and assumptions. The original Python Script Mode adapters remain available; their setup is documented in [Rhino setup](docs/RHINO_SETUP.md) and [component ports](docs/COMPONENTS.md).

## Layout
- `src/plug_in_solar/` — calculation core, no Rhino dependency
- `grasshopper/components/` — Python 3 Script Mode adapters
- `grasshopper/components.json` — component names, categories, ports and icon paths (our own catalogue, not a Rhino project file)
- `assets/icons/` — editable SVGs and PNG exports
- `examples/clear_sky_demo.py` — end-to-end example
- `tests/` — physical/convention and time-integration checks

## Local development
Use Python 3.9–3.12 for the pinned dependency set:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests
python examples/clear_sky_demo.py
```

The pinned versions target Rhino 8's Python 3.9 environment. Dependency compatibility inside Rhino must still be checked when Rhino is reopened. First component execution may download dependencies.

## Modelling boundaries
Clear Sky produces synthetic irradiance, not historical weather or a typical year. Irradiance uses an isotropic diffuse sky and a fixed albedo. PV Power uses Faiman temperature, PVWatts DC/inverter, constant ambient temperature/wind, and a user-specified lumped DC loss. POA is used as effective irradiance without spectral/AOI losses. No obstacle shading, bypass diode/mismatch model, electrical design or grid compliance model is included. AC limit is a modelling input, not a legal recommendation.

Energy is rectangle integration using an explicit interval duration; point samples from the demo approximate interval-average power. The result covers only the provided period. North is +Y in Rhino by default; positive north rotation is clockwise toward +X. Solar azimuth is clockwise from geographic north. Keep timezone-aware timestamps throughout.

## Next additions
Measured/TMY weather import with units and timestamp normalization; shading from Rhino geometry; module/inverter presets; design comparison; saved `.gh` examples; packaged toolbar.
