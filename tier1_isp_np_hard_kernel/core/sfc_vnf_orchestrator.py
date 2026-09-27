"""5G/6G Service Function Chaining (SFC) & VNF Placement Solver for Telco Cloud PoPs."""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

from .models import (
    ServiceChainDemand,
    SfcPlacementResult,
    TelcoComputeNode,
    VirtualNetworkFunction,
)


class SfcVnfOrchestrator:
    """Solves the NP-Hard Service Function Chaining (SFC) Placement Problem.
    
    Embeds an ordered chain of Virtual Network Functions (VNFs)—such as 5G UPF,
    CGNAT, DPI, and Firewall—onto distributed edge Telco Cloud PoPs (Central Offices)
    subject to:
      1. Node compute constraints (CPU cores, RAM)
      2. Hardware accelerator affinity (SmartNIC/DPU offloading for UPF)
      3. Strict 3GPP end-to-end latency budgets (<= 5 ms for URLLC)
    """

    def __init__(self, hardware_offload_speedup: float = 0.30):
        # Hardware offload (e.g. NVIDIA BlueField / Intel IPU) reduces processing delay to 30%
        self.offload_speedup = hardware_offload_speedup

    def solve_sfc_placement(
        self,
        nodes: List[TelcoComputeNode],
        demand: ServiceChainDemand,
        inter_pop_delays: Dict[Tuple[str, str], float],
    ) -> SfcPlacementResult:
        """Embeds a single service chain demand across telco cloud PoPs."""
        t0 = time.perf_counter()

        node_map = {n.node_id: n for n in nodes}
        mapping: Dict[str, str] = {}

        current_node_id = demand.ingress_node
        accumulated_latency = 0.0
        feasible = True

        for vnf in demand.vnf_sequence:
            # Candidate nodes that have sufficient CPU and RAM
            candidates = [
                n for n in nodes
                if n.available_cores >= vnf.required_cores
                and n.available_ram_gb >= vnf.required_ram_gb
            ]

            if not candidates:
                feasible = False
                break

            # Best candidate minimizes: transport_delay(current_node -> candidate) + vnf_processing_delay
            best_node = None
            min_added_delay = float("inf")

            for cand in candidates:
                # Inter-PoP delay (0.0 if co-located on same node)
                if cand.node_id == current_node_id:
                    transport_delay = 0.0
                else:
                    transport_delay = inter_pop_delays.get(
                        (current_node_id, cand.node_id),
                        inter_pop_delays.get((cand.node_id, current_node_id), 10.0),
                    )

                # Processing delay with hardware offload discount for UPF/DPI
                proc_delay = vnf.processing_delay_ms
                if cand.has_hardware_offload and vnf.vnf_type in {"UPF", "DPI", "FIREWALL"}:
                    proc_delay *= self.offload_speedup

                total_stage_delay = transport_delay + proc_delay

                if total_stage_delay < min_added_delay:
                    min_added_delay = total_stage_delay
                    best_node = cand

            if not best_node:
                feasible = False
                break

            # Deduct resources and record placement
            best_node.available_cores -= vnf.required_cores
            best_node.available_ram_gb -= vnf.required_ram_gb
            mapping[vnf.vnf_id] = best_node.node_id
            accumulated_latency += min_added_delay
            current_node_id = best_node.node_id

        # Add egress transport delay to final egress node
        if feasible:
            if current_node_id != demand.egress_node:
                final_transport = inter_pop_delays.get(
                    (current_node_id, demand.egress_node),
                    inter_pop_delays.get((demand.egress_node, current_node_id), 5.0),
                )
                accumulated_latency += final_transport

            if accumulated_latency > demand.max_end_to_end_latency_ms:
                feasible = False

        solve_time_ms = (time.perf_counter() - t0) * 1000.0

        return SfcPlacementResult(
            chain_id=demand.chain_id,
            vnf_node_mapping=mapping,
            end_to_end_latency_ms=round(accumulated_latency, 2),
            is_feasible=feasible,
            solve_time_ms=round(solve_time_ms, 2),
        )
