"""Unit tests for Anycast DDoS Scrubbing Solver."""

import unittest
from tier1_isp_np_hard_kernel.core.ddos_anycast_scrubber import AnycastDdosScrubber
from tier1_isp_np_hard_kernel.core.models import AttackVector, ScrubbingCenter


class TestDdosScrubber(unittest.TestCase):
    def setUp(self):
        self.scrubber = AnycastDdosScrubber(target_max_utilization=0.85)
        self.centers = [
            ScrubbingCenter("c1", "London", capacity_gbps=1000.0, fixed_cost_monthly_usd=10000.0),
            ScrubbingCenter("c2", "Frankfurt", capacity_gbps=1000.0, fixed_cost_monthly_usd=10000.0),
        ]
        self.attacks = [
            AttackVector("atk1", "Europe", peak_volume_gbps=1200.0, attack_type="UDP_REFLECTION")
        ]
        self.proximity = {
            ("Europe", "London"): 5.0,
            ("Europe", "Frankfurt"): 6.0,
        }

    def test_ddos_mitigation(self):
        report = self.scrubber.mitigate_volumetric_attacks(self.centers, self.attacks, self.proximity)

        self.assertTrue(report.mitigation_success)
        self.assertEqual(report.total_scrubbed_gbps, 1200.0)
        self.assertEqual(report.dropped_traffic_gbps, 0.0)
        # London should be filled up to target or slightly above, Frankfurt absorbs spillover
        self.assertGreater(report.center_utilization_pct["c1"], 0.0)
        self.assertGreater(report.center_utilization_pct["c2"], 0.0)


if __name__ == "__main__":
    unittest.main()
