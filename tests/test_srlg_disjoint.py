"""Unit tests for SRLG Disjoint Path Routing Solver."""

import unittest
from tier1_isp_np_hard_kernel.core.models import SrlgLink
from tier1_isp_np_hard_kernel.core.srlg_disjoint_routing import SrlgDisjointRoutingSolver


class TestSrlgDisjointRouting(unittest.TestCase):
    def setUp(self):
        self.solver = SrlgDisjointRoutingSolver()
        # Diamond topology with distinct shared risk conduits
        self.links = [
            # Path A (Upper route via Highway 1)
            SrlgLink("l1", "London", "Frankfurt_North", 300.0, {"srlg_conduit_hwy1"}),
            SrlgLink("l2", "Frankfurt_North", "Frankfurt", 350.0, {"srlg_bridge_rhine_north"}),
            # Path B (Lower route via Railway)
            SrlgLink("l3", "London", "Frankfurt_South", 320.0, {"srlg_railway_trench"}),
            SrlgLink("l4", "Frankfurt_South", "Frankfurt", 360.0, {"srlg_bridge_rhine_south"}),
        ]

    def test_srlg_strict_disjointness(self):
        res = self.solver.solve_disjoint_pairs(self.links, [("London", "Frankfurt")])

        self.assertEqual(len(res.pairs), 1)
        pair = res.pairs[0]

        # Ensure primary and secondary are strictly disjoint
        self.assertTrue(pair.is_strictly_disjoint)
        self.assertEqual(len(pair.primary_srlgs.intersection(pair.secondary_srlgs)), 0)
        self.assertEqual(res.shared_srlg_violations, 0)
        self.assertEqual(res.diversity_guarantee_pct, 100.0)


if __name__ == "__main__":
    unittest.main()
