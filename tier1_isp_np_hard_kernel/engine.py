"""Hyperscale Tier-1 ISP Benchmark Engine and Multi-Solver Orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Dict, List, Tuple

from .core.models import (
    AttackVector,
    ContentCatalogItem,
    FiberSpan,
    FlexAlgoEdge,
    LightpathDemand,
    MetroCentralOffice,
    MultiConstrainedSla,
    PeeringPartner,
    ScrubbingCenter,
    ServiceChainDemand,
    SrlgLink,
    TelcoComputeNode,
    TrafficInterval,
    TransitProvider,
    VirtualNetworkFunction,
)
from .core.optical_rsa_flexgrid import FlexGridRsaSolver
from .core.srlg_disjoint_routing import SrlgDisjointRoutingSolver
from .core.burstable_billing_optimizer import BurstableBillingOptimizer
from .core.srv6_flex_algo_mcsp import Srv6FlexAlgoMcspSolver
from .core.sfc_vnf_orchestrator import SfcVnfOrchestrator
from .core.ddos_anycast_scrubber import AnycastDdosScrubber
from .core.cdn_peering_balancer import CdnPeeringBalancer


@dataclass
class Tier1IspBenchmarkReport:
    """Consolidated KPI report across all 7 Tier-1 ISP Combinatorial Solvers."""
    # 1. Flex-Grid RSA
    optical_spectrum_utilization_pct: float
    optical_fragmentation_ratio: float
    optical_rsa_solve_time_ms: float
    # 2. SRLG Disjoint Routing
    srlg_diversity_guarantee_pct: float
    srlg_solve_time_ms: float
    # 3. 95th Percentile Burstable Billing
    p95_billing_cost_reduction_pct: float
    p95_annual_savings_usd: float
    p95_solve_time_ms: float
    # 4. SRv6 Flex-Algo MCSP
    srv6_mcsp_sla_satisfied: bool
    srv6_mcsp_delay_ms: float
    srv6_mcsp_solve_time_ms: float
    # 5. 5G/6G SFC Placement
    sfc_placement_feasible: bool
    sfc_end_to_end_latency_ms: float
    sfc_solve_time_ms: float
    # 6. Anycast DDoS Scrubbing
    ddos_absorbed_traffic_gbps: float
    ddos_mitigation_success: bool
    ddos_solve_time_ms: float
    # 7. Metro Edge CDN & Peering Balancer
    cdn_cache_hit_ratio_pct: float
    cdn_peering_ratios_compliant: bool
    cdn_annual_transit_savings_usd: float
    cdn_solve_time_ms: float
    # Total runtime
    total_pipeline_time_ms: float


class Tier1IspEngine:
    """Unified Orchestration Engine for Major Internet Service Provider Solvers."""

    def __init__(self):
        self.rsa_solver = FlexGridRsaSolver(k_paths=3)
        self.srlg_solver = SrlgDisjointRoutingSolver()
        self.billing_optimizer = BurstableBillingOptimizer()
        self.mcsp_solver = Srv6FlexAlgoMcspSolver(norm_q=4)
        self.sfc_orchestrator = SfcVnfOrchestrator(hardware_offload_speedup=0.30)
        self.ddos_scrubber = AnycastDdosScrubber(target_max_utilization=0.85)
        self.cdn_balancer = CdnPeeringBalancer(transit_cost_per_mbps_month=0.08)

    def run_full_benchmark(self) -> Tier1IspBenchmarkReport:
        """Executes full benchmark suite across all 7 Tier-1 ISP combinatorial optimization solvers."""
        t0 = time.perf_counter()

        # 1. Optical Flex-Grid RSA Simulation (Trans-Atlantic & European Core)
        spans = [
            FiberSpan("span_lon_par", "London", "Paris", 450.0),
            FiberSpan("span_par_fra", "Paris", "Frankfurt", 500.0),
            FiberSpan("span_lon_fra", "London", "Frankfurt", 650.0),
            FiberSpan("span_fra_ams", "Frankfurt", "Amsterdam", 400.0),
            FiberSpan("span_ams_lon", "Amsterdam", "London", 380.0),
            FiberSpan("span_subsea_nyc_lon", "New_York", "London", 5500.0),  # Trans-oceanic
        ]
        demands = [
            LightpathDemand("dem_800g_core", "New_York", "Frankfurt", 800.0, priority=2),
            LightpathDemand("dem_400g_metro1", "London", "Paris", 400.0, priority=1),
            LightpathDemand("dem_400g_metro2", "Paris", "Frankfurt", 400.0, priority=1),
            LightpathDemand("dem_100g_ams", "London", "Amsterdam", 100.0, priority=1),
        ]
        rsa_res = self.rsa_solver.solve_rsa(spans, demands)

        # 2. SRLG Disjoint Path Simulation (Subsea Cable Choke Point & Trench Diversity)
        srlg_links = [
            SrlgLink("l1", "London", "Bude_Landing", 380.0, {"trench_m4_conduit"}),
            SrlgLink("l2", "Bude_Landing", "Halifax_Subsea", 4800.0, {"subsea_tata_tgn_atlantic"}),
            SrlgLink("l3", "Halifax_Subsea", "New_York", 950.0, {"trench_i95_conduit"}),
            # Diverse Route (Zero shared SRLGs)
            SrlgLink("l4", "London", "Brighton_Landing", 90.0, {"trench_railway_uk"}),
            SrlgLink("l5", "Brighton_Landing", "Long_Island_Landing", 5600.0, {"subsea_apollo_north"}),
            SrlgLink("l6", "Long_Island_Landing", "New_York", 60.0, {"conduit_metro_ny"}),
        ]
        srlg_res = self.srlg_solver.solve_disjoint_pairs(srlg_links, [("London", "New_York")])

        # 3. 95th Percentile Burstable Billing Simulation (Multi-Homed Transit Commit Optimization)
        providers = [
            TransitProvider("as3356", "Lumen", commit_mbps=100000.0, base_rate_per_mbps=0.05, burst_rate_per_mbps=0.12),
            TransitProvider("as1299", "Arelion", commit_mbps=80000.0, base_rate_per_mbps=0.06, burst_rate_per_mbps=0.14),
            TransitProvider("as2914", "NTT", commit_mbps=60000.0, base_rate_per_mbps=0.07, burst_rate_per_mbps=0.15),
        ]
        # Generate 288 samples (24-hour cycle of 5-min intervals) with realistic peak bursting
        traffic_intervals = []
        for i in range(288):
            # Diurnal sinusoidal traffic curve with extreme peak burst in evening (samples 200-220)
            base_traffic = 160000.0 + 50000.0 * (1.0 + (i % 72) / 72.0)
            if 200 <= i <= 215:  # High-volume peak spike exceeding total commit (240k Mbps)
                base_traffic += 80000.0
            traffic_intervals.append(TrafficInterval(i, round(base_traffic, 1)))

        billing_res = self.billing_optimizer.optimize_traffic_split(providers, traffic_intervals)

        # 4. Multi-Constrained Path Selection (SRv6 Flex-Algo URLLC 5G Slicing)
        edges = [
            FlexAlgoEdge("cell_site_01", "aggr_node_01", delay_ms=1.2, jitter_ms=0.3, packet_loss_rate=0.0001, financial_cost=10.0, bandwidth_gbps=100.0, srv6_sid="fc00:10::1"),
            FlexAlgoEdge("aggr_node_01", "core_router_01", delay_ms=1.8, jitter_ms=0.4, packet_loss_rate=0.0001, financial_cost=15.0, bandwidth_gbps=100.0, srv6_sid="fc00:20::1"),
            FlexAlgoEdge("core_router_01", "edge_upf_cloud", delay_ms=1.1, jitter_ms=0.2, packet_loss_rate=0.00005, financial_cost=5.0, bandwidth_gbps=100.0, srv6_sid="fc00:30::1"),
            # Backup slow high-loss path
            FlexAlgoEdge("cell_site_01", "core_router_01", delay_ms=8.5, jitter_ms=2.5, packet_loss_rate=0.005, financial_cost=2.0, bandwidth_gbps=50.0, srv6_sid="fc00:99::1"),
        ]
        sla = MultiConstrainedSla(
            src="cell_site_01",
            dst="edge_upf_cloud",
            max_delay_ms=5.0,     # Strict 5ms URLLC bound
            max_jitter_ms=1.5,
            max_loss_rate=0.001,
            min_bw_gbps=10.0,
            max_cost=50.0,
        )
        mcsp_res = self.mcsp_solver.solve_mcsp(edges, sla)

        # 5. 5G/6G Service Function Chaining (SFC) Telco Cloud Placement
        telco_nodes = [
            TelcoComputeNode("pop_metro_central", "Metro Central Office", "region_east", total_cores=128.0, available_cores=64.0, total_ram_gb=512.0, available_ram_gb=256.0, has_hardware_offload=True),
            TelcoComputeNode("pop_regional_dc", "Regional Edge DC", "region_east", total_cores=256.0, available_cores=128.0, total_ram_gb=1024.0, available_ram_gb=512.0, has_hardware_offload=False),
        ]
        chain_demand = ServiceChainDemand(
            chain_id="5g_urllc_slice_001",
            ingress_node="pop_metro_central",
            egress_node="pop_regional_dc",
            vnf_sequence=[
                VirtualNetworkFunction("vnf_upf", "UPF", required_cores=16.0, required_ram_gb=32.0, processing_delay_ms=1.5),
                VirtualNetworkFunction("vnf_cgnat", "CGNAT", required_cores=8.0, required_ram_gb=16.0, processing_delay_ms=0.8),
                VirtualNetworkFunction("vnf_firewall", "FIREWALL", required_cores=8.0, required_ram_gb=16.0, processing_delay_ms=1.0),
            ],
            max_end_to_end_latency_ms=6.0,
            traffic_rate_mbps=10000.0,
        )
        delays = {("pop_metro_central", "pop_regional_dc"): 1.8}
        sfc_res = self.sfc_orchestrator.solve_sfc_placement(telco_nodes, chain_demand, delays)

        # 6. Anycast DDoS Scrubbing Center Simulation (Multi-Terabit Volumetric Flood)
        scrubbing_centers = [
            ScrubbingCenter("scrub_lon", "London", capacity_gbps=1500.0, fixed_cost_monthly_usd=12000.0),
            ScrubbingCenter("scrub_fra", "Frankfurt", capacity_gbps=1500.0, fixed_cost_monthly_usd=12000.0),
            ScrubbingCenter("scrub_nyc", "New_York", capacity_gbps=2000.0, fixed_cost_monthly_usd=15000.0),
        ]
        attacks = [
            AttackVector("atk_dns_amplification", "Europe", peak_volume_gbps=1800.0, attack_type="UDP_REFLECTION"),
            AttackVector("atk_syn_flood", "North_America", peak_volume_gbps=1200.0, attack_type="SYN_FLOOD"),
        ]
        proximity = {
            ("Europe", "London"): 5.0,
            ("Europe", "Frankfurt"): 4.0,
            ("Europe", "New_York"): 75.0,
            ("North_America", "New_York"): 8.0,
            ("North_America", "London"): 75.0,
            ("North_America", "Frankfurt"): 80.0,
        }
        ddos_res = self.ddos_scrubber.mitigate_volumetric_attacks(scrubbing_centers, attacks, proximity)

        # 7. Metro Edge CDN Cache & Settlement-Free Peering Balancer
        metro_cos = [
            MetroCentralOffice("co_chicago_01", "Chicago Metro", cache_capacity_tb=100.0),
            MetroCentralOffice("co_dallas_01", "Dallas Metro", cache_capacity_tb=80.0),
        ]
        catalog = [
            ContentCatalogItem(f"video_asset_{i}", size_gb=20.0, popularity_score=1.0 / (i + 1)**0.8)
            for i in range(2000)
        ]
        peers = [
            PeeringPartner("peer_google", "Google AS15169", max_ratio=2.0, current_outbound_gbps=150.0),
            PeeringPartner("peer_netflix", "Netflix AS2906", max_ratio=2.0, current_outbound_gbps=100.0),
        ]
        cdn_res = self.cdn_balancer.balance_peering_and_cache(metro_cos, catalog, peers, total_eyeball_demand_gbps=400.0)

        total_pipeline_time_ms = (time.perf_counter() - t0) * 1000.0

        return Tier1IspBenchmarkReport(
            optical_spectrum_utilization_pct=rsa_res.spectrum_utilization_pct,
            optical_fragmentation_ratio=rsa_res.fragmentation_ratio,
            optical_rsa_solve_time_ms=rsa_res.solve_time_ms,
            srlg_diversity_guarantee_pct=srlg_res.diversity_guarantee_pct,
            srlg_solve_time_ms=srlg_res.solve_time_ms,
            p95_billing_cost_reduction_pct=billing_res.savings_pct,
            p95_annual_savings_usd=billing_res.net_savings_usd * 12.0,
            p95_solve_time_ms=billing_res.solve_time_ms,
            srv6_mcsp_sla_satisfied=mcsp_res.is_sla_satisfied,
            srv6_mcsp_delay_ms=mcsp_res.accumulated_delay_ms,
            srv6_mcsp_solve_time_ms=mcsp_res.solve_time_ms,
            sfc_placement_feasible=sfc_res.is_feasible,
            sfc_end_to_end_latency_ms=sfc_res.end_to_end_latency_ms,
            sfc_solve_time_ms=sfc_res.solve_time_ms,
            ddos_absorbed_traffic_gbps=ddos_res.total_scrubbed_gbps,
            ddos_mitigation_success=ddos_res.mitigation_success,
            ddos_solve_time_ms=ddos_res.solve_time_ms,
            cdn_cache_hit_ratio_pct=cdn_res.cache_hit_ratio_pct,
            cdn_peering_ratios_compliant=cdn_res.all_peering_ratios_compliant,
            cdn_annual_transit_savings_usd=cdn_res.annual_transit_savings_usd,
            cdn_solve_time_ms=cdn_res.solve_time_ms,
            total_pipeline_time_ms=round(total_pipeline_time_ms, 2),
        )
