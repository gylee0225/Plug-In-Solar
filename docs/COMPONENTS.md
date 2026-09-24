# Component ports
Configure the following inputs in order. All inputs use **Item access** and are required. Keep the standard `out` port; add the named outputs below it.
Every component has `project_root` (Text) as its first input. Connect the repository path to it. `object` means **No Type Hint**, `str` means Text, and `float` means a decimal number.
For pandas/pvlib object wires, enable **Avoid Marshalling Inputs** and **Avoid Marshalling Outputs** in the Python component advanced menu so frames and location objects remain Python objects. Pass the object output directly between components, not through a Panel. Rhino interoperability still needs an in-app check.

## Location
Geographic location; altitude in metres; IANA timezone.

Inputs: `project_root` (str), `latitude` (float), `longitude` (float), `timezone` (str), `altitude_m` (float)

Outputs: `site`

## Clear Sky
Synthetic clear-sky irradiance only; end is exclusive.

Inputs: `project_root` (str), `site` (object), `start` (str), `end` (str), `step_minutes` (float)

Outputs: `weather`, `timestamps`

## Sun Position
Apparent altitude and clockwise-from-north azimuth in degrees.

Inputs: `project_root` (str), `site` (object), `weather` (object)

Outputs: `solar`, `altitude_deg`, `azimuth_deg`

## Panel Orientation
Front-face panel normal. Model north rotates clockwise from +Y toward +X.

Inputs: `project_root` (str), `normal` (Vector3d), `north_deg` (float)

Outputs: `tilt_deg`, `azimuth_deg`

## Panel Irradiance
Isotropic sky transposition, W/m²; no local geometry shading.

Inputs: `project_root` (str), `weather` (object), `solar` (object), `tilt_deg` (float), `azimuth_deg` (float), `albedo` (float)

Outputs: `poa`, `poa_w_m2`

## PV Power
Simplified PVWatts model; constant ambient conditions; capacity in watts.

Inputs: `project_root` (str), `poa` (object), `dc_capacity_w` (float), `ac_limit_w` (float), `air_temp_c` (float), `wind_m_s` (float), `gamma_pdc` (float), `losses_pct` (float)

Outputs: `power`, `dc_w`, `ac_w`

## Energy Yield
Energy over supplied intervals, not automatically an annual forecast.

Inputs: `project_root` (str), `power` (object), `step_hours` (float)

Outputs: `total_kwh`
