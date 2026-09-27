"""Unit tests for 95th Percentile Burstable Billing Optimizer."""

import unittest
from tier1_isp_np_hard_kernel.core.burstable_billing_optimizer import BurstableBillingOptimizer
from tier1_isp_np_hard_kernel.core.models import TrafficInterval, TransitProvider


class TestBurstableBillingOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = BurstableBillingOptimizer()
        self.providers = [
            TransitProvider("as3356", "Lumen", commit_mbps=10000.0, base_rate_per_mbps=0.05, burst_rate_per_mbps=0.15),
            TransitProvider("as1299", "Arelion", commit_mbps=10000.0, base_rate_per_mbps=0.06, burst_rate_per_mbps=0.16),
        ]

    def test_p95_calculation(self):
        # 100 samples from 1 to 100
        samples = list(range(1, 101))
        p95 = self.optimizer._compute_p95(samples)
        # 95th percentile of 100 sorted samples is 95
        self.assertEqual(p95, 95)

    def test_burstable_water_filling_cost_reduction(self):
        # Create 100 intervals with baseline 15k Mbps and 5 extreme spikes of 30k Mbps
        intervals = []
        for i in range(100):
            val = 30000.0 if i >= 95 else 15000.0
            intervals.append(TrafficInterval(i, val))

        report = self.optimizer.optimize_traffic_split(self.providers, intervals)

        # Cost under optimized water-filling should be strictly less than or equal to unoptimized
        self.assertLessEqual(report.total_optimized_cost_usd, report.total_unoptimized_cost_usd)
        self.assertGreaterEqual(report.savings_pct, 0.0)


if __name__ == "__main__":
    unittest.main()
