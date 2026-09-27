"""End-to-End integration tests for Tier1IspEngine."""

import unittest
from tier1_isp_np_hard_kernel.engine import Tier1IspEngine


class TestTier1IspEngine(unittest.TestCase):
    def setUp(self):
        self.engine = Tier1IspEngine()

    def test_full_benchmark_run(self):
        report = self.engine.run_full_benchmark()

        # 1. Optical Flex-Grid RSA
        self.assertGreater(report.optical_spectrum_utilization_pct, 0.0)
        self.assertGreaterEqual(report.optical_fragmentation_ratio, 0.0)

        # 2. SRLG Disjoint Routing
        self.assertEqual(report.srlg_diversity_guarantee_pct, 100.0)

        # 3. 95th Percentile Burstable Billing
        self.assertGreater(report.p95_billing_cost_reduction_pct, 0.0)
        self.assertGreater(report.p95_annual_savings_usd, 0.0)

        # 4. SRv6 Flex-Algo MCSP
        self.assertTrue(report.srv6_mcsp_sla_satisfied)
        self.assertLessEqual(report.srv6_mcsp_delay_ms, 5.0)

        # 5. 5G SFC Placement
        self.assertTrue(report.sfc_placement_feasible)
        self.assertLessEqual(report.sfc_end_to_end_latency_ms, 6.0)

        # 6. Anycast DDoS Scrubbing
        self.assertTrue(report.ddos_mitigation_success)
        self.assertGreater(report.ddos_absorbed_traffic_gbps, 0.0)

        # 7. Metro CDN Peering Balancer
        self.assertGreater(report.cdn_cache_hit_ratio_pct, 0.0)
        self.assertGreater(report.cdn_annual_transit_savings_usd, 0.0)

        # Total pipeline time must be sub-second (under 1000 ms)
        self.assertLess(report.total_pipeline_time_ms, 1000.0)


if __name__ == "__main__":
    unittest.main()
