"""
Seed Sensei - Main Application & Live Demonstration CLI
Target Crop: Groundnut (Arachis hypogaea)

Pipeline:
Synthetic IoT Sensors -> TinyML Edge Node -> Simulated LoRa Frame -> Central AI -> Recommendations -> Farmer Alert
"""

import sys
import time
import argparse
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import (
    FARM_ZONES,
    TINYML_MODEL_PATH,
    CENTRAL_STRESS_MODEL_PATH,
    CENTRAL_YIELD_MODEL_PATH,
)
from src.farm_simulator import GroundnutFarmSimulator
from src.cli_views import (
    render_technical_view,
    render_farmer_view,
    render_scenario_step_banner,
)


def ensure_models_ready():
    """Verify ML models are present; auto-train if missing."""
    if not (TINYML_MODEL_PATH.exists() and CENTRAL_STRESS_MODEL_PATH.exists() and CENTRAL_YIELD_MODEL_PATH.exists()):
        print("[INIT] Required ML models not found. Running training on synthetic dataset...")
        from train_models import run_training_pipeline
        run_training_pipeline(force_regenerate_data=False)


def run_single_view(sim: GroundnutFarmSimulator, mode: str = "technical", focus_zone_id: int = None):
    """Run full pipeline once and display requested mode."""
    pipeline_output = sim.execute_farm_pipeline()
    if mode.lower() == "farmer":
        render_farmer_view(pipeline_output)
    else:
        render_technical_view(pipeline_output, focus_zone_id=focus_zone_id)


def run_dry_stress_demonstration(sim: GroundnutFarmSimulator, interactive_pause: bool = True):
    """
    Live Demonstration Scenario:
    Demonstrates progressive moisture stress in Zone 2:
    45% -> 34% -> 26% -> 18% moisture depletion.
    Shows real-time model reactivity across the complete pipeline.
    """
    steps = sim.get_dry_stress_scenario_steps()
    total_steps = len(steps)

    print("\n" + "=" * 78)
    print("STARTING LIVE DEMONSTRATION: PROGRESSIVE SOIL MOISTURE STRESS SCENARIO")
    print("TARGET ZONE : Zone 2 (Node N02, Red Sandy Loam, Groundnut Flowering/Pegging Stage)")
    print("TRAJECTORY  : Soil Moisture 45.0% -> 34.0% -> 26.0% -> 18.0%")
    print("=" * 78)

    for step_info in steps:
        step_num = step_info["step"]
        desc = step_info["description"]
        z_id = step_info["zone_id"]

        # Apply simulated telemetry change
        sim.update_zone_telemetry(
            z_id,
            soil_moisture=step_info["soil_moisture"],
            air_temp=step_info["air_temp"],
            humidity=step_info["humidity"],
            soil_temp=step_info["soil_temp"],
        )

        # Execute zone pipeline
        zone_pipeline = sim.execute_zone_pipeline(z_id)
        raw_telemetry = zone_pipeline["raw_sensor_data"]
        edge = zone_pipeline["edge_inference"]
        lora = zone_pipeline["lora_transmission"]
        ai = zone_pipeline["central_ai_analysis"]
        rec = zone_pipeline["recommendation"]
        
        # Get whole farm state for alert
        farm_output = sim.execute_farm_pipeline()

        render_scenario_step_banner(step_num, total_steps, desc, z_id)

        print(f"\n[STEP {step_num} TELEMETRY CHANGE]")
        print(f"  Zone 2 Soil Moisture : {raw_telemetry['soil_moisture']:.1f}%")
        print(f"  Zone 2 Air Temp      : {raw_telemetry['air_temp']:.1f}°C")
        print(f"  Zone 2 Humidity      : {raw_telemetry['humidity']:.1f}%")

        print(f"\n[TINYML EDGE INFERENCE (Node N02)]")
        print(f"  Edge Status          : {edge['edge_status']}")
        print(f"  Confidence           : {edge['edge_confidence']*100:.1f}%")
        print(f"  Noise / Outlier Check: {'PASSED (Sensors Normal)' if not edge['noise_filtered'] else 'ANOMALY FILTERED'}")

        print(f"\n[SIMULATED LORA COMMUNICATION]")
        print(f"  Payload Hex Frame    : 0x{lora['metadata']['hex_dump']}")
        print(f"  Binary Length        : {lora['metadata']['packet_bytes_len']} bytes (Compact frame)")
        print(f"  Airtime (SF7/125kHz) : {lora['metadata']['airtime_ms']} ms")
        print(f"  Signal (RSSI / SNR)  : {lora['metadata']['simulated_rssi_dbm']} dBm / +{lora['metadata']['simulated_snr_db']} dB")
        print(f"  Decoded at Gateway   : MOISTURE={lora['gateway_decoded']['soil_moisture']}% | EDGE_STATUS={lora['gateway_decoded']['edge_status']}")

        print(f"\n[CENTRAL AI ENGINE ANALYSIS]")
        probs = ai["stress_probabilities"]
        print(f"  Predicted Stress     : {ai['predicted_stress_class']}")
        print(f"  Stress Probabilities : High={probs.get('High Stress', 0.0)*100:.1f}%, Mod={probs.get('Moderate Stress', 0.0)*100:.1f}%, Norm={probs.get('Normal', 0.0)*100:.1f}%")
        print(f"  Projected Yield      : {ai['predicted_yield_kg_ha']:.1f} kg/ha (Yield Gap: -{ai['yield_loss_pct']:.1f}%)")
        print(f"  Zone Risk Score      : {ai['risk_score']:.1f} / 100 ({ai['risk_category']})")

        print(f"\n[AI AGRONOMIC RECOMMENDATION]")
        print(f"  Urgency              : {rec['urgency']}")
        print(f"  Action               : {rec['primary_action']}")
        print(f"  Agronomic Rationale  : {rec['rationale']}")

        print(f"\n[FARMER NOTIFICATION DISPATCHED]")
        farmer_card = farm_output["farmer_alert"]
        for line in farmer_card.splitlines()[:10]:
            print(f"  | {line}")
        print("  | ... [Advisory active]")

        if interactive_pause and step_num < total_steps:
            input("\n>> Press [ENTER] to advance to the next simulation step...")
        else:
            time.sleep(0.5)

    print("\n" + "=" * 78)
    print("DEMONSTRATION COMPLETED: Notice how changing telemetry drove real ML model outputs,")
    print("escalated risk scores, projected yield loss, and updated recommendations dynamically.")
    print("=" * 78 + "\n")


def run_heat_stress_demonstration(sim: GroundnutFarmSimulator, interactive_pause: bool = True):
    """
    Live Demonstration Scenario:
    Demonstrates thermal spike in Zone 6:
    29.0°C -> 33.5°C -> 37.0°C -> 40.5°C ambient temperature.
    """
    steps = [
        {"step": 1, "temp": 29.0, "soil_temp": 26.5, "hum": 60.0, "desc": "Optimal Ambient Conditions (29.0°C)"},
        {"step": 2, "temp": 33.5, "soil_temp": 29.5, "hum": 48.0, "desc": "Elevated Afternoon Temperature (33.5°C)"},
        {"step": 3, "temp": 37.0, "soil_temp": 32.5, "hum": 36.0, "desc": "Moderate Heat Stress Threshold (37.0°C)"},
        {"step": 4, "temp": 40.5, "soil_temp": 35.0, "hum": 28.0, "desc": "Severe Groundnut Heat Wave (40.5°C)"},
    ]

    print("\n" + "=" * 78)
    print("STARTING LIVE DEMONSTRATION: PROGRESSIVE THERMAL STRESS SCENARIO")
    print("TARGET ZONE : Zone 6 (Node N06, Red Loam, Groundnut Flowering/Pegging Stage)")
    print("TRAJECTORY  : Air Temperature 29.0°C -> 33.5°C -> 37.0°C -> 40.5°C")
    print("=" * 78)

    for s in steps:
        step_num = s["step"]
        desc = s["desc"]
        sim.update_zone_telemetry(6, air_temp=s["temp"], soil_temp=s["soil_temp"], humidity=s["hum"])
        res = sim.execute_zone_pipeline(6)
        ai = res["central_ai_analysis"]
        edge = res["edge_inference"]
        rec = res["recommendation"]

        render_scenario_step_banner(step_num, len(steps), desc, 6)
        print(f"  Telemetry       : Air Temp = {s['temp']:.1f}°C | Humidity = {s['hum']:.1f}%")
        print(f"  TinyML Edge     : {edge['edge_status']} (Confidence: {edge['edge_confidence']*100:.1f}%)")
        print(f"  Central Stress  : {ai['predicted_stress_class']} | Risk: {ai['risk_score']:.1f}/100 ({ai['risk_category']})")
        print(f"  Projected Yield : {ai['predicted_yield_kg_ha']:.1f} kg/ha")
        print(f"  Recommendation  : {rec['primary_action']}")
        if rec.get("thermal_mitigation"):
            print(f"  Heat Advisory   : {rec['thermal_mitigation']}")

        if interactive_pause and step_num < len(steps):
            input("\n>> Press [ENTER] to advance to the next heat step...")
        else:
            time.sleep(0.5)


def interactive_menu(sim: GroundnutFarmSimulator):
    """Interactive command console for live presentations."""
    while True:
        print("\n" + "=" * 70)
        print("SEED SENSEI :: PROTOTYPE DEMONSTRATION CONSOLE")
        print("Crop: Groundnut (Arachis hypogaea) | AI-Driven Precision Agriculture")
        print("=" * 70)
        print("  1. View Current Farm Status (Technical Presentation Mode)")
        print("  2. View Current Farmer Advisory (Farmer Mode)")
        print("  3. Run Live Stress Demo: Zone 2 Progressive Drying (45% -> 18%)")
        print("  4. Run Live Heat Demo: Zone 6 Progressive Heat Wave (29°C -> 40.5°C)")
        print("  5. Reset Farm to Normal Balanced Conditions")
        print("  6. Live Sensor Value Injection (Custom Test)")
        print("  7. Retrain ML Models on Synthetic Data")
        print("  8. Exit")
        print("=" * 70)
        
        choice = input("Select an option [1-8]: ").strip()

        if choice == "1":
            run_single_view(sim, mode="technical")
        elif choice == "2":
            run_single_view(sim, mode="farmer")
        elif choice == "3":
            run_dry_stress_demonstration(sim, interactive_pause=True)
        elif choice == "4":
            run_heat_stress_demonstration(sim, interactive_pause=True)
        elif choice == "5":
            sim.set_balanced_normal()
            print("\n[SUCCESS] Farm reset to healthy balanced conditions across all 6 zones.")
            run_single_view(sim, mode="technical")
        elif choice == "6":
            try:
                z_id = int(input("Enter Zone ID [1-6]: ").strip())
                if z_id not in FARM_ZONES:
                    print("Invalid zone ID.")
                    continue
                moist = float(input(f"Enter Soil Moisture for Zone {z_id} (% e.g. 19.5): ").strip())
                temp = float(input(f"Enter Air Temperature for Zone {z_id} (°C e.g. 36.0): ").strip())
                sim.update_zone_telemetry(z_id, soil_moisture=moist, air_temp=temp)
                print(f"\n[UPDATED] Zone {z_id} updated with Moisture={moist}%, Temp={temp}°C")
                run_single_view(sim, mode="technical", focus_zone_id=z_id)
            except ValueError:
                print("Invalid numeric input.")
        elif choice == "7":
            from train_models import run_training_pipeline
            run_training_pipeline(force_regenerate_data=True)
            # Reload AI engine with newly trained models
            sim.central_ai._load_or_train_models()
        elif choice == "8":
            print("\nExiting Seed Sensei prototype. Goodbye.\n")
            break
        else:
            print("Invalid selection. Please choose an option from 1 to 8.")


def main():
    parser = argparse.ArgumentParser(
        description="Seed Sensei: AI-Driven Precision Agriculture Prototype for Groundnut Farming"
    )
    parser.add_argument(
        "--mode",
        choices=["technical", "farmer"],
        default=None,
        help="Display output mode: 'technical' or 'farmer'",
    )
    parser.add_argument(
        "--simulate-stress",
        "--simulate-dry-condition",
        action="store_true",
        dest="simulate_stress",
        help="Trigger the live Zone 2 drying demonstration scenario (45%% -> 18%%)",
    )
    parser.add_argument(
        "--simulate-heat",
        action="store_true",
        help="Trigger the live Zone 6 heat wave demonstration scenario",
    )
    parser.add_argument(
        "--zone",
        type=int,
        choices=[1, 2, 3, 4, 5, 6],
        default=None,
        help="Focus display on a specific logical zone",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without pausing for user input during demonstrations",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Force regeneration of synthetic data and retrain ML models",
    )

    args = parser.parse_args()

    # Ensure models exist
    ensure_models_ready()

    if args.train:
        from train_models import run_training_pipeline
        run_training_pipeline(force_regenerate_data=True)
        return

    sim = GroundnutFarmSimulator()

    # Check CLI scenario triggers
    if args.simulate_stress:
        run_dry_stress_demonstration(sim, interactive_pause=not args.non_interactive)
        return

    if args.simulate_heat:
        run_heat_stress_demonstration(sim, interactive_pause=not args.non_interactive)
        return

    if args.mode:
        run_single_view(sim, mode=args.mode, focus_zone_id=args.zone)
        return

    # Default to interactive menu if no arguments passed
    interactive_menu(sim)


if __name__ == "__main__":
    main()
