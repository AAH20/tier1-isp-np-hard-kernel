"""Flex-Grid Elastic Optical Network (EON) Routing and Spectrum Assignment (RSA) Solver."""

from __future__ import annotations

import heapq
import math
import time
from typing import Dict, List, Optional, Set, Tuple

from .models import (
    FiberSpan,
    LightpathAllocation,
    LightpathDemand,
    ModulationFormat,
    RsaSolverResult,
)


class FlexGridRsaSolver:
    """Solves the NP-Hard Routing and Spectrum Assignment (RSA) problem in Flex-Grid EONs.
    
    Adheres strictly to the optical physics constraints:
    1. Spectrum Continuity: Same frequency slots across all spans in the lightpath.
    2. Spectrum Contiguity: Allocated frequency slots must be contiguous in frequency.
    3. Non-Overlapping Spectrum: No overlapping slots on the same fiber span.
    4. Distance-Adaptive Modulation Format: Selects QPSK, 16-QAM, or 64-QAM based on OSNR reach.
    """

    SLOT_WIDTH_GHZ = 12.5  # Standard ITU-T G.694.1 flex-grid slot

    def __init__(self, k_paths: int = 3):
        self.k_paths = k_paths

    def _select_modulation(self, path_length_km: float) -> Tuple[ModulationFormat, int]:
        """Selects distance-adaptive modulation format and bits per baud."""
        if path_length_km <= 350.0:
            return ModulationFormat.QAM64, 6
        elif path_length_km <= 1500.0:
            return ModulationFormat.QAM16, 4
        else:
            return ModulationFormat.QPSK, 2

    def _calculate_slots_needed(self, bitrate_gbps: float, bits_per_baud: int) -> int:
        """Calculates contiguous 12.5 GHz slots needed with guard band."""
        # Spectral efficiency approx: bitrate / (baud_rate * bits_per_symbol)
        # Standard: 100G = 2-3 slots, 400G = 4-6 slots, 800G = 8-12 slots
        effective_spectral_eff = bits_per_baud * 0.8  # FEC overhead adjustment
        bandwidth_ghz = bitrate_gbps / effective_spectral_eff
        raw_slots = math.ceil(bandwidth_ghz / self.SLOT_WIDTH_GHZ)
        # Add 1 slot for optical filter guard band
        return max(2, raw_slots + 1)

    def _find_k_shortest_paths(
        self,
        src: str,
        dst: str,
        spans: Dict[Tuple[str, str], FiberSpan],
        k: int,
    ) -> List[Tuple[List[str], float]]:
        """Finds up to K shortest paths using Dijkstra variant."""
        adj: Dict[str, List[Tuple[str, float]]] = {}
        for (u, v), span in spans.items():
            adj.setdefault(u, []).append((v, span.length_km))

        paths: List[Tuple[List[str], float]] = []
        pq: List[Tuple[float, List[str]]] = [(0.0, [src])]
        visited_paths: Set[Tuple[str, ...]] = set()

        while pq and len(paths) < k:
            dist, path = heapq.heappop(pq)
            u = path[-1]
            if u == dst:
                paths.append((path, dist))
                continue

            path_tuple = tuple(path)
            if path_tuple in visited_paths:
                continue
            visited_paths.add(path_tuple)

            for neighbor, length in adj.get(u, []):
                if neighbor not in path:  # Loop-free
                    heapq.heappush(pq, (dist + length, path + [neighbor]))

        return paths

    def _find_common_free_slots(
        self,
        path: List[str],
        spans: Dict[Tuple[str, str], FiberSpan],
    ) -> List[bool]:
        """Calculates intersection of available slots across all spans in path (Continuity)."""
        num_slots = spans[list(spans.keys())[0]].total_slots
        common_free = [True] * num_slots

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            span = spans.get((u, v))
            if not span:
                return [False] * num_slots
            for s in range(num_slots):
                if span.occupied_slots[s]:
                    common_free[s] = False

        return common_free

    def _find_first_fit_contiguous_block(
        self,
        common_free: List[bool],
        slots_needed: int,
    ) -> Optional[int]:
        """Finds first contiguous free slot block (Contiguity & Non-overlapping)."""
        count = 0
        start_idx = -1
        for i, is_free in enumerate(common_free):
            if is_free:
                if count == 0:
                    start_idx = i
                count += 1
                if count == slots_needed:
                    return start_idx
            else:
                count = 0
                start_idx = -1
        return None

    def solve_rsa(
        self,
        spans: List[FiberSpan],
        demands: List[LightpathDemand],
    ) -> RsaSolverResult:
        """Executes K-Shortest Path First-Fit RSA with distance-adaptive modulation."""
        t0 = time.perf_counter()

        # Build bidirectional span map
        span_map: Dict[Tuple[str, str], FiberSpan] = {}
        for s in spans:
            span_map[(s.src, s.dst)] = s
            # Create reverse span if asymmetric
            if (s.dst, s.src) not in span_map:
                rev_span = FiberSpan(
                    span_id=f"{s.span_id}_rev",
                    src=s.dst,
                    dst=s.src,
                    length_km=s.length_km,
                    total_slots=s.total_slots,
                    occupied_slots=list(s.occupied_slots),
                )
                span_map[(s.dst, s.src)] = rev_span

        # Sort demands by priority (descending) and bitrate (descending)
        sorted_demands = sorted(demands, key=lambda d: (d.priority, d.bitrate_gbps), reverse=True)

        allocations: List[LightpathAllocation] = []
        unserved: List[str] = []

        for dem in sorted_demands:
            candidate_paths = self._find_k_shortest_paths(dem.src, dem.dst, span_map, self.k_paths)
            allocated = False

            for path, length_km in candidate_paths:
                mod_format, bits_per_baud = self._select_modulation(length_km)
                slots_needed = self._calculate_slots_needed(dem.bitrate_gbps, bits_per_baud)

                common_free = self._find_common_free_slots(path, span_map)
                start_slot = self._find_first_fit_contiguous_block(common_free, slots_needed)

                if start_slot is not None:
                    # Allocate slots across all spans in path
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i + 1]
                        for s_idx in range(start_slot, start_slot + slots_needed):
                            span_map[(u, v)].occupied_slots[s_idx] = True

                    # Calculate OSNR margin (simplified realistic model)
                    base_osnr = 28.0 - (length_km / 250.0)
                    osnr_margin = max(2.5, base_osnr)

                    allocations.append(
                        LightpathAllocation(
                            demand_id=dem.demand_id,
                            path=path,
                            start_slot=start_slot,
                            slot_count=slots_needed,
                            modulation=mod_format,
                            osnr_margin_db=round(osnr_margin, 2),
                        )
                    )
                    allocated = True
                    break

            if not allocated:
                unserved.append(dem.demand_id)

        # Calculate metrics
        total_slots_system = sum(s.total_slots for s in spans)
        total_occupied_slots = sum(sum(s.occupied_slots) for s in spans)
        util_pct = (total_occupied_slots / max(1, total_slots_system)) * 100.0

        # Calculate spectral fragmentation ratio across spans
        frag_scores = []
        for s in spans:
            free_slots = s.total_slots - sum(s.occupied_slots)
            if free_slots > 0:
                max_contiguous = 0
                curr = 0
                for occ in s.occupied_slots:
                    if not occ:
                        curr += 1
                        max_contiguous = max(max_contiguous, curr)
                    else:
                        curr = 0
                frag_scores.append(1.0 - (max_contiguous / free_slots))
            else:
                frag_scores.append(0.0)

        avg_frag = sum(frag_scores) / max(1, len(frag_scores))
        solve_time_ms = (time.perf_counter() - t0) * 1000.0

        return RsaSolverResult(
            allocations=allocations,
            unserved_demands=unserved,
            spectrum_utilization_pct=round(util_pct, 2),
            fragmentation_ratio=round(avg_frag, 3),
            solve_time_ms=round(solve_time_ms, 2),
        )
