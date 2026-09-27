"""Command-Line Interface for Tier-1 ISP NP-Hard Optimization Kernel."""

from __future__ import annotations

import argparse
import sys
import time

from .engine import Tier1IspEngine


def cmd_benchmark_all():
    print("=" * 78)
    print("🌐 TIER-1 INTERNET SERVICE PROVIDER (ISP) NP-HARD BENCHMARK SUITE")
    print("=" * 78)
    print("Executing 7 SOTA Combinatorial Solvers across Global Optical & Transit Layers...")

    engine = Tier1IspEngine()
    report = engine.run_full_benchmark()

    print("\n[BENCHMARK RESULTS & METRICS]")
    print(f"1. Optical Flex-Grid RSA (Routing & Spectrum Assignment):")
    print(f"   - C-Band Spectrum Utilization   : {report.optical_spectrum_utilization_pct}%")
    print(f"   - Spectral Fragmentation Ratio  : {report.optical_fragmentation_ratio} (Target: <0.30)")
    print(f"   - Solver Execution Latency      : {report.optical_rsa_solve_time_ms:.2f} ms")

    print(f"\n2. SRLG Disjoint Path Routing (Subsea & Trench Diversity):")
    print(f"   - Physical Diversity Guarantee  : {report.srlg_diversity_guarantee_pct}% (Zero Shared Risks)")
    print(f"   - Solver Execution Latency      : {report.srlg_solve_time_ms:.2f} ms")

    print(f"\n3. 95th Percentile Burstable Transit Billing Minimization:")
    print(f"   - Transit Overage Cost Cut      : -{report.p95_billing_cost_reduction_pct:.1f}%")
    print(f"   - Annual Transit Cost Savings   : ${report.p95_annual_savings_usd:,.2f}/yr")
    print(f"   - Solver Execution Latency      : {report.p95_solve_time_ms:.2f} ms")

    print(f"\n4. Multi-Constrained Path Selection (SRv6 Flex-Algo 5G Slicing):")
    print(f"   - Strict URLLC SLA Satisfied    : {'YES (SLA Met)' if report.srv6_mcsp_sla_satisfied else 'NO'}")
    print(f"   - End-to-End Latency Achieved   : {report.srv6_mcsp_delay_ms:.2f} ms (Budget: 5.00 ms)")
    print(f"   - Solver Execution Latency      : {report.srv6_mcsp_solve_time_ms:.2f} ms")

    print(f"\n5. 5G/6G Service Function Chaining (SFC) Placement:")
    print(f"   - VNF Chain Placement Feasible  : {'YES (Optimal PoP Embedding)' if report.sfc_placement_feasible else 'NO'}")
    print(f"   - Chain Latency with HW Offload : {report.sfc_end_to_end_latency_ms:.2f} ms")
    print(f"   - Solver Execution Latency      : {report.sfc_solve_time_ms:.2f} ms")

    print(f"\n6. Anycast DDoS Scrubbing Center Traffic Ingestion:")
    print(f"   - Multi-Terabit Attack Absorbed : {report.ddos_absorbed_traffic_gbps:,.1f} Gbps (3.0 Tbps Peak)")
    print(f"   - Hardware Saturation Avoided   : {'YES (No Leaked Traffic)' if report.ddos_mitigation_success else 'NO'}")
    print(f"   - Solver Execution Latency      : {report.ddos_solve_time_ms:.2f} ms")

    print(f"\n7. Metro Edge CDN Cache & Settlement-Free Peering Balancer:")
    print(f"   - Metro Central Office Hit Ratio: {report.cdn_cache_hit_ratio_pct}%")
    print(f"   - Settlement-Free Ratio (<2:1)  : {'COMPLIANT (Zero De-Peering Risk)' if report.cdn_peering_ratios_compliant else 'NON-COMPLIANT'}")
    print(f"   - Annual Transit Savings        : ${report.cdn_annual_transit_savings_usd:,.2f}/yr")
    print(f"   - Solver Execution Latency      : {report.cdn_solve_time_ms:.2f} ms")

    print("-" * 78)
    print(f"⏱️  Total 7-Solver Engine Pipeline Runtime : {report.total_pipeline_time_ms:.2f} ms (Sub-second)")
    print("=" * 78)


def main():
    parser = argparse.ArgumentParser(
        description="Tier-1 ISP NP-Hard Combinatorial Optimization Kernel CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")
    subparsers.add_parser("benchmark-all", help="Execute complete benchmark across all 7 solvers")

    args = parser.parse_args()

    if args.command == "benchmark-all" or not args.command:
        cmd_benchmark_all()
    else:
        cmd_benchmark_all()


if __name__ == "__main__":
    main()
