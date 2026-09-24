"""One synthetic clear-sky day in Berlin, for wiring/installation checks only."""
from plug_in_solar import core
site = core.location(52.52, 13.405, "Europe/Berlin", 34)
weather = core.clear_sky(site, "2026-06-21", "2026-06-22", 60)
solar = core.sun_position(site, weather.index)
poa = core.irradiance(weather, solar, 30, 180, 0.2)
power = core.pv_power(poa.poa_global, 800, 800)
print("Synthetic clear-sky example; not a weather-based yield forecast.")
print("Samples:", len(power))
print("AC energy: {:.3f} kWh".format(core.energy_kwh(power.ac_w, 1)))
