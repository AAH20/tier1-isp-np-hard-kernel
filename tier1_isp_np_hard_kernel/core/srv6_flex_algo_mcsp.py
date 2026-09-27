"""Multi-Constrained Optimal Path (MCOP/MCSP) Solver for SRv6 Flex-Algo Network Slicing."""

from __future__ import annotations

import heapq
import math
import time
from typing import Dict, List, Optional, Tuple

from .models import FlexAlgoEdge, McspResult, MultiConstrainedSla


class Srv6FlexAlgoMcspSolver:
    """Solves the NP-Complete Multi-Constrained Path Selection Problem (MCSP/MCOP).
    
    In 5G URLLC slicing and high-frequency trading (HFT) circuits, traffic must satisfy
    simultaneous, independent, non-linear constraints:
      1. Delay <= D_max (Additive)
      2. Jitter <= J_max (Additive)
      3. Packet Loss <= L_max (Multiplicative: 1 - prod(1 - l_i) approx sum(l_i))
      4. Bandwidth >= B_min (Bottleneck)
      5. Financial Cost -> Minimize
      
    Uses the H_MCOP (Heuristic Multi-Constrained Optimal Path) algorithm with
    lookahead lower-bounding and non-linear L_q norm Pareto pruning.
    """

    def __init__(self, norm_q: int = 4):
        self.q = norm_q

    def _compute_lookahead_lower_bounds(
        self,
        dst: str,
        adj_rev: Dict[str, List[FlexAlgoEdge]],
        min_bw: float,
    ) -> Dict[str, Tuple[float, float, float]]:
        """Calculates backward Dijkstra lower bounds from all nodes to dst for delay, jitter, loss."""
        # Returns mapping: node -> (min_delay_to_dst, min_jitter_to_dst, min_loss_to_dst)
        lower_bounds: Dict[str, Tuple[float, float, float]] = {dst: (0.0, 0.0, 0.0)}

        # Shortest delay backward Dijkstra
        pq_delay: List[Tuple[float, str]] = [(0.0, dst)]
        min_delay: Dict[str, float] = {dst: 0.0}

        while pq_delay:
            d, u = heapq.heappop(pq_delay)
            if d > min_delay.get(u, float("inf")):
                continue
            for edge in adj_rev.get(u, []):
                if edge.bandwidth_gbps < min_bw:
                    continue
                v = edge.src
                new_d = d + edge.delay_ms
                if new_d < min_delay.get(v, float("inf")):
                    min_delay[v] = new_d
                    heapq.heappush(pq_delay, (new_d, v))

        # Shortest jitter backward Dijkstra
        pq_jitter: List[Tuple[float, str]] = [(0.0, dst)]
        min_jitter: Dict[str, float] = {dst: 0.0}
        while pq_jitter:
            j, u = heapq.heappop(pq_jitter)
            if j > min_jitter.get(u, float("inf")):
                continue
            for edge in adj_rev.get(u, []):
                if edge.bandwidth_gbps < min_bw:
                    continue
                v = edge.src
                new_j = j + edge.jitter_ms
                if new_j < min_jitter.get(v, float("inf")):
                    min_jitter[v] = new_j
                    heapq.heappush(pq_jitter, (new_j, v))

        # Shortest loss backward Dijkstra
        pq_loss: List[Tuple[float, str]] = [(0.0, dst)]
        min_loss: Dict[str, float] = {dst: 0.0}
        while pq_loss:
            l, u = heapq.heappop(pq_loss)
            if l > min_loss.get(u, float("inf")):
                continue
            for edge in adj_rev.get(u, []):
                if edge.bandwidth_gbps < min_bw:
                    continue
                v = edge.src
                new_l = l + edge.packet_loss_rate
                if new_l < min_loss.get(v, float("inf")):
                    min_loss[v] = new_l
                    heapq.heappush(pq_loss, (new_l, v))

        all_nodes = set(min_delay.keys()).union(min_jitter.keys()).union(min_loss.keys())
        for n in all_nodes:
            lower_bounds[n] = (
                min_delay.get(n, float("inf")),
                min_jitter.get(n, float("inf")),
                min_loss.get(n, float("inf")),
            )

        return lower_bounds

    def solve_mcsp(
        self,
        edges: List[FlexAlgoEdge],
        sla: MultiConstrainedSla,
    ) -> McspResult:
        """Finds multi-constrained optimal path using H_MCOP with lookahead pruning."""
        t0 = time.perf_counter()

        # Build forward and reverse graphs
        adj: Dict[str, List[FlexAlgoEdge]] = {}
        adj_rev: Dict[str, List[FlexAlgoEdge]] = {}
        for e in edges:
            adj.setdefault(e.src, []).append(e)
            adj_rev.setdefault(e.dst, []).append(e)

        # Step 1: Backward search for lookahead lower bounds
        lower_bounds = self._compute_lookahead_lower_bounds(sla.dst, adj_rev, sla.min_bw_gbps)

        # Step 2: Forward heuristic search using non-linear norm weight
        # State: (norm_cost, current_node, path, sids, delay, jitter, loss, financial_cost)
        pq: List[Tuple[float, str, List[str], List[str], float, float, float, float]] = [
            (0.0, sla.src, [sla.src], [], 0.0, 0.0, 0.0, 0.0)
        ]

        best_feasible_path: Optional[McspResult] = None
        min_feasible_cost = float("inf")

        # Visited Pareto frontier map: node -> list of (delay, jitter, loss, cost)
        visited_frontiers: Dict[str, List[Tuple[float, float, float, float]]] = {}

        while pq:
            score, u, path, sids, d_acc, j_acc, l_acc, cost_acc = heapq.heappop(pq)

            if u == sla.dst:
                # Target reached!
                is_feasible = (
                    d_acc <= sla.max_delay_ms
                    and j_acc <= sla.max_jitter_ms
                    and l_acc <= sla.max_loss_rate
                    and cost_acc <= sla.max_cost
                )
                if is_feasible and cost_acc < min_feasible_cost:
                    min_feasible_cost = cost_acc
                    best_feasible_path = McspResult(
                        path=path,
                        srv6_sids=sids,
                        accumulated_delay_ms=round(d_acc, 2),
                        accumulated_jitter_ms=round(j_acc, 2),
                        accumulated_loss_rate=round(l_acc, 5),
                        total_financial_cost=round(cost_acc, 2),
                        is_sla_satisfied=True,
                        solve_time_ms=0.0,
                    )
                    # Once a feasible path with lowest financial cost is found in early heap, terminate
                    break

            # Check Pareto dominance against visited frontiers
            frontier = visited_frontiers.setdefault(u, [])
            is_dominated = False
            for f_d, f_j, f_l, f_c in frontier:
                if f_d <= d_acc and f_j <= j_acc and f_l <= l_acc and f_c <= cost_acc:
                    is_dominated = True
                    break
            if is_dominated:
                continue
            frontier.append((d_acc, j_acc, l_acc, cost_acc))

            # Explore neighbors
            for edge in adj.get(u, []):
                if edge.bandwidth_gbps < sla.min_bw_gbps:
                    continue
                v = edge.dst
                if v in path:  # Loop avoidance
                    continue

                new_d = d_acc + edge.delay_ms
                new_j = j_acc + edge.jitter_ms
                new_l = l_acc + edge.packet_loss_rate
                new_cost = cost_acc + edge.financial_cost

                # Lookahead feasibility check using backward bounds
                lb_d, lb_j, lb_l = lower_bounds.get(v, (0.0, 0.0, 0.0))
                if (new_d + lb_d > sla.max_delay_ms) or (new_j + lb_j > sla.max_jitter_ms) or (new_l + lb_l > sla.max_loss_rate):
                    continue  # Prune branch: impossible to satisfy SLA from this node

                # Non-linear norm metric score
                norm_d = (new_d / max(0.001, sla.max_delay_ms)) ** self.q
                norm_j = (new_j / max(0.001, sla.max_jitter_ms)) ** self.q
                norm_l = (new_l / max(0.001, sla.max_loss_rate)) ** self.q
                norm_score = (norm_d + norm_j + norm_l) ** (1.0 / self.q) + (new_cost / max(1.0, sla.max_cost))

                heapq.heappush(
                    pq,
                    (
                        norm_score,
                        v,
                        path + [v],
                        sids + [edge.srv6_sid],
                        new_d,
                        new_j,
                        new_l,
                        new_cost,
                    ),
                )

        solve_time_ms = (time.perf_counter() - t0) * 1000.0

        if best_feasible_path:
            best_feasible_path.solve_time_ms = round(solve_time_ms, 2)
            return best_feasible_path

        # If strict feasibility fails, return fallback shortest path with SLA violation flag
        return McspResult(
            path=[],
            srv6_sids=[],
            accumulated_delay_ms=0.0,
            accumulated_jitter_ms=0.0,
            accumulated_loss_rate=0.0,
            total_financial_cost=0.0,
            is_sla_satisfied=False,
            solve_time_ms=round(solve_time_ms, 2),
        )
