import unittest
import pandas as pd
from plug_in_solar import core

class SolarTests(unittest.TestCase):
    def test_orientation(self):
        self.assertEqual(core.orientation(0, -1, 0), (90, 180))
        self.assertEqual(core.orientation(1, 0, 0, 90), (90, 0))
        with self.assertRaises(ValueError): core.orientation(0,0,0)

    def test_energy_intervals_and_rejection(self):
        idx = pd.date_range("2026-01-01", periods=4, freq="30min", tz="UTC")
        self.assertEqual(core.energy_kwh(pd.Series([1000]*4,index=idx),0.5),2)
        with self.assertRaises(ValueError): core.energy_kwh(pd.Series([1000]*4,index=idx),1)
        with self.assertRaises(ValueError): core.energy_kwh(pd.Series([float("nan")]*4,index=idx),0.5)

    def test_night_and_ac_clipping(self):
        idx = pd.date_range("2026-06-21", periods=3, freq="h", tz="UTC")
        result = core.pv_power(pd.Series([0,1000,1500],index=idx),2000,600,losses_pct=0)
        self.assertEqual(result.ac_w.iloc[0],0)
        self.assertLessEqual(result.ac_w.max(),600.000001)
        self.assertAlmostEqual(result.ac_w.iloc[-1],600)

    def test_horizontal_irradiance_identity(self):
        site=core.location(52.52,13.405,"Europe/Berlin")
        weather=core.clear_sky(site,"2026-06-21 10:00","2026-06-21 15:00")
        solar=core.sun_position(site,weather.index)
        poa=core.irradiance(weather,solar,0,180)
        for a,b in zip(poa.poa_global,weather.ghi): self.assertAlmostEqual(a,b,places=5)
        with self.assertRaises(ValueError): core.irradiance(weather,solar.iloc[1:],0,180)

    def test_dst_elapsed_intervals(self):
        site=core.location(52.52,13.405,"Europe/Berlin")
        self.assertEqual(len(core.times_for(site,"2026-03-29","2026-03-30")),23)

if __name__ == "__main__": unittest.main()
