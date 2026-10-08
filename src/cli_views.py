import sys
from typing import Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import FARM_ZONES, POTENTIAL_MAX_YIELD_KG_HA


def render_technical_view(pipeline_output: Dict[str, Any], focus_zone_id: Optional[int] = None):
    """
    Render comprehensive technical terminal view for presenters and engineers.
    Displays end-to-end dataflow without emojis or gimmicks.
    """
    farm_summary = pipeline_output["farm_summary"]
    zone_results = pipeline_output["zone_results"]
    recommendations = pipeline_output["farm_recommendations"]
    crop = pipeline_output["crop"]
    crop_age = pipeline_output["crop_age_days"]

    width = 82
    sep = "=" * width
    subsep = "-" * width

    print(sep)
    print("SEED SENSEI :: AI-DRIVEN OILSEED PRECISION AGRICULTURE SYSTEM")
    print(subsep)
    print(f"CROP TARGET        : {crop} | Age: {crop_age} Days (Flowering & Pegging Stage)")
    print(f"SYSTEM STATUS      : ACTIVE MONITORING (6 Spatial Logical Zones)")
    print("DATA NOTICE        : Software proof-of-concept operating on synthetic farm data")
    print(sep)

    # 1. FIELD DATA TELEMETRY
    print("\n[1. FIELD SENSOR TELEMETRY (SYNTHETIC)]")
    print(f"{'ZONE':<8} {'NODE':<6} {'SOIL MOIST':<12} {'SOIL TEMP':<11} {'AIR TEMP':<10} {'HUMIDITY':<10} {'NUTRIENT':<10}")
    print("-" * 70)
    for z in zone_results:
        raw = z["raw_sensor_data"]
        z_id = z["zone_id"]
        node_id = FARM_ZONES[z_id]["node_id"]
        print(
            f"Zone {z_id:<3} {node_id:<6} {raw['soil_moisture']:>6.1f}%       "
            f"{raw['soil_temp']:>5.1f}°C     {raw['air_temp']:>5.1f}°C    "
            f"{raw['humidity']:>5.1f}%     {raw['nutrient_index']:>5.2f} (Index)"
        )

    # 2. EDGE INTELLIGENCE (TINYML)
    print("\n[2. EDGE INTELLIGENCE (TINYML ON-NODE INFERENCE)]")
    for z in zone_results:
        edge = z["edge_inference"]
        z_id = z["zone_id"]
        node_id = edge["node_id"]
        status = edge["edge_status"]
        conf = edge["edge_confidence"]
        mcu = edge["mcu_specs"]
        noise_flag = "OK" if not edge["noise_filtered"] else "FILTERED"
        print(
            f"  * Node {node_id} (Zone {z_id}): {status:<18} "
            f"[Confidence: {conf*100:>4.1f}% | Outlier Check: {noise_flag} | Est. RAM: {mcu['est_ram_bytes']}B | Latency: {mcu['est_latency_ms']}ms]"
        )

    # 3. COMMUNICATION LAYER (SIMULATED LORA)
    print("\n[3. COMMUNICATION LAYER (SIMULATED LORA LINK)]")
    # Highlight focused zone or highest risk zone
    display_tx = None
    if focus_zone_id:
        for z in zone_results:
            if z["zone_id"] == focus_zone_id:
                display_tx = z
                break
    if not display_tx:
        # Default to highest risk zone
        display_tx = max(zone_results, key=lambda x: x["central_ai_analysis"]["risk_score"])

    lora = display_tx["lora_transmission"]
    meta = lora["metadata"]
    decoded = lora["gateway_decoded"]
    
    print(f"  Frame Origin      : Node {decoded['node_id']} -> Gateway (Logical Zone {decoded['zone_id']})")
    print(f"  Payload Hex Dump  : 0x{meta['hex_dump']} ({meta['packet_bytes_len']} bytes binary frame)")
    print(
        f"  Decoded Payload   : MOISTURE={decoded['soil_moisture']}% | "
        f"TEMP={decoded['air_temp']}°C | HUM={decoded['humidity']}% | EDGE_STATUS={decoded['edge_status']}"
    )
    print(
        f"  RF Physical Link  : Freq: {meta['frequency_mhz']} MHz | SF{meta['spreading_factor']} | "
        f"BW {meta['bandwidth_khz']} kHz | CRC16: VALID"
    )
    print(
        f"  Link Quality      : RSSI: {meta['simulated_rssi_dbm']} dBm | "
        f"SNR: +{meta['simulated_snr_db']} dB | Airtime: {meta['airtime_ms']} ms"
    )
    print(f"  Link Status       : {meta['status']} (Simulated Software Protocol)")

    # 4. CENTRAL AI ENGINE
    print("\n[4. CENTRAL AI ENGINE (HIGHER-LEVEL INFERENCE)]")
    print(f"{'ZONE':<8} {'STRESS CLASS':<16} {'PROB (HIGH/MOD/NORM)':<24} {'YIELD EST':<14} {'RISK SCORE':<12}")
    print("-" * 76)
    for z in zone_results:
        ai = z["central_ai_analysis"]
        z_id = z["zone_id"]
        probs = ai["stress_probabilities"]
        prob_str = f"{probs.get('High Stress', 0.0):.2f} / {probs.get('Moderate Stress', 0.0):.2f} / {probs.get('Normal', 0.0):.2f}"
        print(
            f"Zone {z_id:<3} {ai['predicted_stress_class']:<16} {prob_str:<24} "
            f"{ai['predicted_yield_kg_ha']:>6.1f} kg/ha   {ai['risk_score']:>5.1f} ({ai['risk_category']})"
        )

    # 5. FARM-LEVEL AI SUMMARY
    print("\n[5. FARM-LEVEL AI SUMMARY]")
    print(f"  Overall Status            : {farm_summary['overall_status']}")
    print(f"  High Risk Zones           : {farm_summary['high_risk_count']} {farm_summary.get('high_risk_zone_names', [])}")
    print(f"  Moderate Risk Zones       : {farm_summary['moderate_risk_count']} {farm_summary.get('moderate_risk_zone_names', [])}")
    print(f"  Normal Zones              : {farm_summary['normal_risk_count']}")
    print(f"  Farm Mean Projected Yield : {farm_summary['average_predicted_yield_kg_ha']} kg/ha (Potential Max: {POTENTIAL_MAX_YIELD_KG_HA:.1f} kg/ha)")
    print(f"  Overall Farm Risk Score   : {farm_summary['overall_farm_risk_score']} / 100")

    # 6. ACTIONABLE RECOMMENDATIONS
    print("\n[6. ACTIONABLE AGRONOMIC RECOMMENDATIONS]")
    for idx, rec in enumerate(recommendations, 1):
        print(f"  {idx}. [{rec['urgency']}] {rec['primary_action']}")
        print(f"     Rationale: {rec['rationale']}")
        if rec.get("thermal_mitigation"):
            print(f"     Heat Advisory: {rec['thermal_mitigation']}")
        if rec.get("nutrient_advisory"):
            print(f"     Nutrient Advisory: {rec['nutrient_advisory']}")

    # 7. FARMER ALERT STATUS
    print("\n[7. FARMER ALERT DISPATCH]")
    print("  Status: Farmer alert notification successfully generated from AI outputs.")
    print(sep)


def render_farmer_view(pipeline_output: Dict[str, Any]):
    """
    Render clean, distraction-free advisory card for the farmer.
    Hides all engineering variables, ML mechanics, and raw numbers.
    """
    print(pipeline_output["farmer_alert"])


def render_scenario_step_banner(step_num: int, total_steps: int, description: str, zone_id: int):
    """
    Render clear step banner during live stress demonstration.
    """
    print("\n" + "=" * 70)
    print(f">> LIVE STRESS DEMONSTRATION :: STEP {step_num} OF {total_steps} [Zone {zone_id}]")
    print(f">> SCENARIO EVENT: {description}")
    print("=" * 70)
