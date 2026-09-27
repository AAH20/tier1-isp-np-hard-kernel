"""Unit tests for Service Function Chaining Solver."""

import unittest
from tier1_isp_np_hard_kernel.core.models import (
    ServiceChainDemand,
    TelcoComputeNode,
    VirtualNetworkFunction,
)
from tier1_isp_np_hard_kernel.core.sfc_vnf_orchestrator import SfcVnfOrchestrator


class TestSfcVnfOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orchestrator = SfcVnfOrchestrator(hardware_offload_speedup=0.30)
        self.nodes = [
            TelcoComputeNode("pop1", "PoP Edge 1", "reg1", 32.0, 32.0, 128.0, 128.0, has_hardware_offload=True),
            TelcoComputeNode("pop2", "PoP Edge 2", "reg1", 32.0, 32.0, 128.0, 128.0, has_hardware_offload=False),
        ]
        self.demand = ServiceChainDemand(
            chain_id="chain_5g",
            ingress_node="pop1",
            egress_node="pop2",
            vnf_sequence=[
                VirtualNetworkFunction("vnf1", "UPF", 8.0, 16.0, 2.0),
                VirtualNetworkFunction("vnf2", "FIREWALL", 4.0, 8.0, 1.0),
            ],
            max_end_to_end_latency_ms=10.0,
            traffic_rate_mbps=1000.0,
        )
        self.delays = {("pop1", "pop2"): 1.5}

    def test_sfc_embedding_feasibility(self):
        res = self.orchestrator.solve_sfc_placement(self.nodes, self.demand, self.delays)

        self.assertTrue(res.is_feasible)
        self.assertEqual(len(res.vnf_node_mapping), 2)
        self.assertLessEqual(res.end_to_end_latency_ms, 10.0)
        # Verify node resources were deducted
        self.assertLess(self.nodes[0].available_cores, 32.0)


if __name__ == "__main__":
    unittest.main()
