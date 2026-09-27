"""Unit tests for Optical Flex-Grid RSA Solver."""

import unittest
from tier1_isp_np_hard_kernel.core.models import (
    FiberSpan,
    LightpathDemand,
    ModulationFormat,
)
from tier1_isp_np_hard_kernel.core.optical_rsa_flexgrid import FlexGridRsaSolver


class TestOpticalRsaSolver(unittest.TestCase):
    def setUp(self):
        self.solver = FlexGridRsaSolver(k_paths=3)
        self.spans = [
            FiberSpan("s1", "NYC", "BOS", 350.0),   # <=350 km -> 64-QAM
            FiberSpan("s2", "BOS", "MTL", 500.0),   # <=1500 km -> 16-QAM
            FiberSpan("s3", "NYC", "LON", 5500.0),  # >1500 km -> QPSK
        ]

    def test_distance_adaptive_modulation(self):
        mod_short, bits_short = self.solver._select_modulation(300.0)
        self.assertEqual(mod_short, ModulationFormat.QAM64)
        self.assertEqual(bits_short, 6)

        mod_med, bits_med = self.solver._select_modulation(1200.0)
        self.assertEqual(mod_med, ModulationFormat.QAM16)
        self.assertEqual(bits_med, 4)

        mod_long, bits_long = self.solver._select_modulation(6000.0)
        self.assertEqual(mod_long, ModulationFormat.QPSK)
        self.assertEqual(bits_long, 2)

    def test_rsa_continuity_and_contiguity(self):
        demands = [
            LightpathDemand("dem_400g_metro", "NYC", "BOS", 400.0),
            LightpathDemand("dem_800g_subsea", "NYC", "LON", 800.0),
        ]
        res = self.solver.solve_rsa(self.spans, demands)

        self.assertEqual(len(res.allocations), 2)
        self.assertEqual(len(res.unserved_demands), 0)

        for alloc in res.allocations:
            self.assertGreater(alloc.slot_count, 0)
            self.assertGreaterEqual(alloc.start_slot, 0)
            self.assertGreater(alloc.osnr_margin_db, 0.0)

        # Verify Metro demand used 64-QAM, while Subsea used QPSK
        metro_alloc = [a for a in res.allocations if a.demand_id == "dem_400g_metro"][0]
        subsea_alloc = [a for a in res.allocations if a.demand_id == "dem_800g_subsea"][0]

        self.assertEqual(metro_alloc.modulation, ModulationFormat.QAM64)
        self.assertEqual(subsea_alloc.modulation, ModulationFormat.QPSK)


if __name__ == "__main__":
    unittest.main()
