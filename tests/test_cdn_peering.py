"""Unit tests for Metro Edge CDN Cache & Peering Balancer."""

import unittest
from tier1_isp_np_hard_kernel.core.cdn_peering_balancer import CdnPeeringBalancer
from tier1_isp_np_hard_kernel.core.models import (
    ContentCatalogItem,
    MetroCentralOffice,
    PeeringPartner,
)


class TestCdnPeeringBalancer(unittest.TestCase):
    def setUp(self):
        self.balancer = CdnPeeringBalancer(transit_cost_per_mbps_month=0.08)
        self.offices = [
            MetroCentralOffice("co1", "Chicago", cache_capacity_tb=10.0),
        ]
        self.catalog = [
            ContentCatalogItem("v1", size_gb=100.0, popularity_score=10.0),
            ContentCatalogItem("v2", size_gb=100.0, popularity_score=5.0),
        ]
        self.peers = [
            PeeringPartner("p1", "Google AS15169", max_ratio=2.0, current_outbound_gbps=50.0),
        ]

    def test_cache_hit_and_peering_ratio(self):
        res = self.balancer.balance_peering_and_cache(
            self.offices, self.catalog, self.peers, total_eyeball_demand_gbps=100.0
        )

        self.assertGreater(res.cache_hit_ratio_pct, 0.0)
        self.assertGreater(res.offloaded_transit_gbps, 0.0)
        self.assertGreater(res.annual_transit_savings_usd, 0.0)


if __name__ == "__main__":
    unittest.main()
