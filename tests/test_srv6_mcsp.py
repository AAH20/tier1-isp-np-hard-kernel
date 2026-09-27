"""Unit tests for Multi-Constrained Path Selection Solver."""

import unittest
from tier1_isp_np_hard_kernel.core.models import FlexAlgoEdge, MultiConstrainedSla
from tier1_isp_np_hard_kernel.core.srv6_flex_algo_mcsp import Srv6FlexAlgoMcspSolver


class TestSrv6FlexAlgoMcsp(unittest.TestCase):
    def setUp(self):
        self.solver = Srv6FlexAlgoMcspSolver(norm_q=4)
        self.edges = [
            # Low-latency, low-jitter path
            FlexAlgoEdge("n1", "n2", delay_ms=1.5, jitter_ms=0.2, packet_loss_rate=0.0001, financial_cost=10.0, bandwidth_gbps=100.0, srv6_sid="fc00:1::1"),
            FlexAlgoEdge("n2", "n3", delay_ms=1.5, jitter_ms=0.3, packet_loss_rate=0.0001, financial_cost=10.0, bandwidth_gbps=100.0, srv6_sid="fc00:2::1"),
            # High-delay detour
            FlexAlgoEdge("n1", "n3", delay_ms=12.0, jitter_ms=4.0, packet_loss_rate=0.01, financial_cost=2.0, bandwidth_gbps=100.0, srv6_sid="fc00:9::1"),
        ]

    def test_mcsp_sla_satisfaction(self):
        sla = MultiConstrainedSla(
            src="n1",
            dst="n3",
            max_delay_ms=5.0,
            max_jitter_ms=1.0,
            max_loss_rate=0.001,
            min_bw_gbps=10.0,
            max_cost=30.0,
        )
        res = self.solver.solve_mcsp(self.edges, sla)

        self.assertTrue(res.is_sla_satisfied)
        self.assertEqual(res.path, ["n1", "n2", "n3"])
        self.assertLessEqual(res.accumulated_delay_ms, 5.0)
        self.assertLessEqual(res.accumulated_jitter_ms, 1.0)


if __name__ == "__main__":
    unittest.main()
