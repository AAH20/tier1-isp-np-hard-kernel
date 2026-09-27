"""Strongly-typed data models for Tier-1 ISP NP-Hard Kernel."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


# ============================================================================
# 1. Optical Flex-Grid RSA Models
# ============================================================================

class ModulationFormat(Enum):
    QPSK = "QPSK"       # Up to 6000 km, 2 bits/baud (Trans-oceanic subsea)
    QAM16 = "16-QAM"    # Up to 1500 km, 4 bits/baud (Long-haul terrestrial)
    QAM64 = "64-QAM"    # Up to 350 km,  6 bits/baud (Regional / Metro core)


@dataclass
class FiberSpan:
    span_id: str
    src: str
    dst: str
    length_km: float
    total_slots: int = 384  # Standard C-Band: 384 x 12.5 GHz = 4.8 THz
    occupied_slots: List[bool] = field(default_factory=list)
    chromatic_dispersion_ps_nm: float = 17.0  # SMF-28 standard dispersion
    attenuation_db_per_km: float = 0.20

    def __post_init__(self):
        if not self.occupied_slots:
            self.occupied_slots = [False] * self.total_slots


@dataclass
class LightpathDemand:
    demand_id: str
    src: str
    dst: str
    bitrate_gbps: float  # e.g., 100, 400, 800, 1200 Gbps
    priority: int = 1


@dataclass
class LightpathAllocation:
    demand_id: str
    path: List[str]
    start_slot: int
    slot_count: int
    modulation: ModulationFormat
    osnr_margin_db: float


@dataclass
class RsaSolverResult:
    allocations: List[LightpathAllocation]
    unserved_demands: List[str]
    spectrum_utilization_pct: float
    fragmentation_ratio: float
    solve_time_ms: float


# ============================================================================
# 2. SRLG Disjoint Path Routing Models
# ============================================================================

@dataclass
class SrlgLink:
    link_id: str
    src: str
    dst: str
    length_km: float
    srlg_ids: Set[str]  # Shared physical risks (conduits, bridges, subsea trenches)
    cost: float = 1.0


@dataclass
class DisjointPathPair:
    src: str
    dst: str
    primary_path: List[str]
    secondary_path: List[str]
    primary_srlgs: Set[str]
    secondary_srlgs: Set[str]
    is_strictly_disjoint: bool
    total_latency_ms: float


@dataclass
class SrlgSolverResult:
    pairs: List[DisjointPathPair]
    shared_srlg_violations: int
    diversity_guarantee_pct: float
    solve_time_ms: float


# ============================================================================
# 3. 95th Percentile Burstable Billing Models
# ============================================================================

@dataclass
class TransitProvider:
    provider_id: str
    name: str
    commit_mbps: float
    base_rate_per_mbps: float   # e.g., $0.05 / Mbps
    burst_rate_per_mbps: float  # e.g., $0.12 / Mbps (1.5x - 2.5x penalty)
    fixed_port_fee: float = 1000.0


@dataclass
class TrafficInterval:
    interval_id: int
    total_egress_mbps: float


@dataclass
class BurstableBillingReport:
    provider_p95_usage: Dict[str, float]
    provider_billed_amounts: Dict[str, float]
    total_optimized_cost_usd: float
    total_unoptimized_cost_usd: float
    net_savings_usd: float
    savings_pct: float
    solve_time_ms: float


# ============================================================================
# 4. Multi-Constrained Optimal Path (MCSP for SRv6 Flex-Algo)
# ============================================================================

@dataclass
class FlexAlgoEdge:
    src: str
    dst: str
    delay_ms: float
    jitter_ms: float
    packet_loss_rate: float
    financial_cost: float
    bandwidth_gbps: float
    srv6_sid: str


@dataclass
class MultiConstrainedSla:
    src: str
    dst: str
    max_delay_ms: float
    max_jitter_ms: float
    max_loss_rate: float
    min_bw_gbps: float
    max_cost: float


@dataclass
class McspResult:
    path: List[str]
    srv6_sids: List[str]
    accumulated_delay_ms: float
    accumulated_jitter_ms: float
    accumulated_loss_rate: float
    total_financial_cost: float
    is_sla_satisfied: bool
    solve_time_ms: float


# ============================================================================
# 5. 5G/6G Service Function Chaining (SFC) Models
# ============================================================================

@dataclass
class VirtualNetworkFunction:
    vnf_id: str
    vnf_type: str  # "UPF", "CGNAT", "DPI", "FIREWALL", "TRAFFIC_SHAPER"
    required_cores: float
    required_ram_gb: float
    processing_delay_ms: float


@dataclass
class ServiceChainDemand:
    chain_id: str
    ingress_node: str
    egress_node: str
    vnf_sequence: List[VirtualNetworkFunction]
    max_end_to_end_latency_ms: float
    traffic_rate_mbps: float


@dataclass
class TelcoComputeNode:
    node_id: str
    name: str
    region: str
    total_cores: float
    available_cores: float
    total_ram_gb: float
    available_ram_gb: float
    has_hardware_offload: bool = True


@dataclass
class SfcPlacementResult:
    chain_id: str
    vnf_node_mapping: Dict[str, str]
    end_to_end_latency_ms: float
    is_feasible: bool
    solve_time_ms: float


# ============================================================================
# 6. Anycast DDoS Scrubbing Center Models
# ============================================================================

@dataclass
class ScrubbingCenter:
    center_id: str
    location: str
    capacity_gbps: float
    fixed_cost_monthly_usd: float
    active_load_gbps: float = 0.0


@dataclass
class AttackVector:
    attack_id: str
    origin_region: str
    peak_volume_gbps: float
    attack_type: str  # "UDP_REFLECTION", "SYN_FLOOD", "NTP_AMPLIFICATION"


@dataclass
class DdosMitigationReport:
    active_scrubbing_centers: List[str]
    total_scrubbed_gbps: float
    dropped_traffic_gbps: float
    center_utilization_pct: Dict[str, float]
    total_scrubbing_cost_usd: float
    mitigation_success: bool
    solve_time_ms: float


# ============================================================================
# 7. Metro Edge CDN Cache & Peering Ratio Models
# ============================================================================

@dataclass
class MetroCentralOffice:
    co_id: str
    metro_name: str
    cache_capacity_tb: float
    occupied_storage_tb: float = 0.0


@dataclass
class ContentCatalogItem:
    content_id: str
    size_gb: float
    popularity_score: float  # Zipf frequency


@dataclass
class PeeringPartner:
    peer_id: str
    name: str
    max_ratio: float = 2.0  # e.g., 2:1 inbound to outbound max
    current_inbound_gbps: float = 0.0
    current_outbound_gbps: float = 0.0


@dataclass
class PeeringBalanceResult:
    cache_hit_ratio_pct: float
    offloaded_transit_gbps: float
    peer_ratios: Dict[str, float]
    all_peering_ratios_compliant: bool
    annual_transit_savings_usd: float
    solve_time_ms: float
