"""
Seed Sensei - Web Application
AI-Powered Precision Agriculture Product for Groundnut Farming

Modern, clean Enterprise Agricultural Dashboard.
Hides all technical engineering internals (TinyML, LoRa, Random Forest, scikit-learn, probabilities, RMSE).
Focuses 100% on farmer decisions, crop health, risk, recommendations, and alerts.
"""

import sys
import os
import time
import argparse
import threading
import subprocess
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import gradio as gr
from src.farm_simulator import GroundnutFarmSimulator
from src.product_ui import (
    PRODUCT_CSS,
    render_brand_header_html,
    render_overview_cards_html,
    render_farm_map_grid_html,
    render_zone_detail_drawer_html,
    render_ai_insights_html,
    render_recommendations_html,
    render_alert_center_html,
)

# Global simulation instance for the web app session
sim = GroundnutFarmSimulator()
current_selected_zone = 1


def get_current_ui_components(selected_zone: int = 1):
    """Run backend farm pipeline and return all HTML component views."""
    output = sim.execute_farm_pipeline()
    overview_html = render_overview_cards_html(output)
    farm_grid_html = render_farm_map_grid_html(output, selected_zone_id=selected_zone)
    zone_detail_html = render_zone_detail_drawer_html(output, zone_id=selected_zone)
    insights_html = render_ai_insights_html(output)
    recs_html = render_recommendations_html(output)
    alerts_html = render_alert_center_html(output)
    return (
        overview_html,
        farm_grid_html,
        zone_detail_html,
        insights_html,
        recs_html,
        alerts_html,
    )


def reset_to_normal(selected_zone: int = 1):
    """Reset farm state to optimal conditions and refresh UI."""
    sim.set_balanced_normal()
    status_msg = "✅ Field restored to optimal healthy conditions across all 6 zones."
    ov, grid, drawer, ins, rec, alt = get_current_ui_components(selected_zone)
    return ov, grid, drawer, ins, rec, alt, status_msg


def select_zone(zone_id: int):
    """Update active zone inspector view."""
    global current_selected_zone
    current_selected_zone = zone_id
    output = sim.execute_farm_pipeline()
    grid = render_farm_map_grid_html(output, selected_zone_id=zone_id)
    drawer = render_zone_detail_drawer_html(output, zone_id=zone_id)
    return grid, drawer


def apply_step(step_idx: int):
    """Apply a specific demo drying step to Zone 2."""
    steps = sim.get_dry_stress_scenario_steps()
    step_info = steps[step_idx]
    sim.update_zone_telemetry(
        2,
        soil_moisture=step_info["soil_moisture"],
        air_temp=step_info["air_temp"],
        humidity=step_info["humidity"],
        soil_temp=step_info["soil_temp"],
    )
    status_msg = f"📍 Simulation: Step {step_idx+1}/4 applied — {step_info['description']}"
    ov, grid, drawer, ins, rec, alt = get_current_ui_components(selected_zone=2)
    return ov, grid, drawer, ins, rec, alt, status_msg


def run_animated_stress_scenario():
    """
    Live Demonstration:
    Progressively transitions Zone 2 through drying steps:
    45% -> 34% -> 26% -> 18% with dynamic live UI updates.
    """
    steps = sim.get_dry_stress_scenario_steps()
    for idx, s in enumerate(steps):
        sim.update_zone_telemetry(
            2,
            soil_moisture=s["soil_moisture"],
            air_temp=s["air_temp"],
            humidity=s["humidity"],
            soil_temp=s["soil_temp"],
        )
        status_msg = f"⏳ Running Stress Scenario: Step {idx+1} of 4 — {s['description']}"
        ov, grid, drawer, ins, rec, alt = get_current_ui_components(selected_zone=2)
        yield ov, grid, drawer, ins, rec, alt, status_msg
        if idx < len(steps) - 1:
            time.sleep(1.8)

    final_msg = "🚨 Stress Scenario Complete: Zone 2 moisture critical (18%). Immediate irrigation recommended."
    yield ov, grid, drawer, ins, rec, alt, final_msg


def run_animated_heat_scenario():
    """
    Live Demonstration:
    Progressively transitions Zone 6 through heat wave steps:
    29°C -> 33.5°C -> 37°C -> 40.5°C with dynamic live UI updates.
    """
    heat_steps = [
        {"temp": 29.0, "soil_temp": 26.5, "hum": 60.0, "desc": "Optimal Ambient (29.0°C)"},
        {"temp": 33.5, "soil_temp": 29.5, "hum": 48.0, "desc": "Elevated Afternoon Heat (33.5°C)"},
        {"temp": 37.0, "soil_temp": 32.5, "hum": 36.0, "desc": "Moderate Heat Stress (37.0°C)"},
        {"temp": 40.5, "soil_temp": 35.0, "hum": 28.0, "desc": "Severe Heat Wave (40.5°C)"},
    ]
    for idx, s in enumerate(heat_steps):
        sim.update_zone_telemetry(
            6,
            air_temp=s["temp"],
            soil_temp=s["soil_temp"],
            humidity=s["hum"],
        )
        status_msg = f"⏳ Running Heat Scenario: Step {idx+1} of 4 — {s['desc']}"
        ov, grid, drawer, ins, rec, alt = get_current_ui_components(selected_zone=6)
        yield ov, grid, drawer, ins, rec, alt, status_msg
        if idx < len(heat_steps) - 1:
            time.sleep(1.8)

    final_msg = "☀️ Heat Scenario Complete: Zone 6 temperature severe (40.5°C). Canopy cooling recommended."
    yield ov, grid, drawer, ins, rec, alt, final_msg


def build_app():
    """Build the Gradio application layout."""
    with gr.Blocks(title="Seed Sensei - Precision Agriculture") as demo:
        # Header Brand Banner
        gr.HTML(render_brand_header_html())

        # Live Demo Control Bar
        with gr.Group():
            with gr.Row():
                btn_stress = gr.Button("💧 Run Stress Scenario (Zone 2 Drying)", variant="primary", scale=2)
                btn_heat = gr.Button("☀️ Run Heat Scenario (Zone 6 Heat)", variant="secondary", scale=2)
                btn_reset = gr.Button("🔄 Reset to Healthy", variant="secondary", scale=1)

            with gr.Row():
                btn_s1 = gr.Button("1. Normal (45%)", size="sm", scale=1)
                btn_s2 = gr.Button("2. Mild Deficit (34%)", size="sm", scale=1)
                btn_s3 = gr.Button("3. Moderate Stress (26%)", size="sm", scale=1)
                btn_s4 = gr.Button("4. Severe Drought (18%)", size="sm", scale=1)

            status_banner = gr.Markdown(
                "**Status:** System initialized. Click **Run Stress Scenario** to demonstrate live AI detection.",
                elem_id="status_banner"
            )

        # Main Navigation Tabs
        with gr.Tabs():
            # 1. Overview Tab
            with gr.TabItem("📊 Overview"):
                overview_display = gr.HTML()

            # 2. Farm Health Tab
            with gr.TabItem("🗺️ Farm Health"):
                farm_grid_display = gr.HTML()
                
                gr.Markdown("#### Select an area to inspect details & AI interpretation:")
                with gr.Row():
                    btn_z1 = gr.Button("Zone 1 (Sandy Loam)", size="sm")
                    btn_z2 = gr.Button("Zone 2 (Red Sandy Loam)", size="sm", variant="primary")
                    btn_z3 = gr.Button("Zone 3 (Sandy Loam)", size="sm")
                    btn_z4 = gr.Button("Zone 4 (Loamy Sand)", size="sm")
                    btn_z5 = gr.Button("Zone 5 (Sandy Loam)", size="sm")
                    btn_z6 = gr.Button("Zone 6 (Red Loam)", size="sm")

                zone_detail_display = gr.HTML()

            # 3. AI Insights Tab
            with gr.TabItem("🧠 AI Insights"):
                insights_display = gr.HTML()

            # 4. Recommendations Tab
            with gr.TabItem("📋 Recommendations"):
                recommendations_display = gr.HTML()

            # 5. Alerts Tab
            with gr.TabItem("🔔 Alerts"):
                alerts_display = gr.HTML()

        # Footer Note
        gr.HTML("""
        <div style="text-align: center; margin-top: 24px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 13px; color: #94a3b8;">
            Seed Sensei AI Platform • Prototype powered by simulated agricultural data • Groundnut Field Intelligence
        </div>
        """)

        # Event Bindings
        # Load initial UI state
        init_views = get_current_ui_components(selected_zone=1)
        demo.load(
            fn=lambda: (*get_current_ui_components(1), "**Status:** Live field monitoring active."),
            outputs=[
                overview_display,
                farm_grid_display,
                zone_detail_display,
                insights_display,
                recommendations_display,
                alerts_display,
                status_banner,
            ],
        )

        # Scenarios
        btn_stress.click(
            fn=run_animated_stress_scenario,
            outputs=[
                overview_display,
                farm_grid_display,
                zone_detail_display,
                insights_display,
                recommendations_display,
                alerts_display,
                status_banner,
            ],
        )

        btn_heat.click(
            fn=run_animated_heat_scenario,
            outputs=[
                overview_display,
                farm_grid_display,
                zone_detail_display,
                insights_display,
                recommendations_display,
                alerts_display,
                status_banner,
            ],
        )

        btn_reset.click(
            fn=reset_to_normal,
            outputs=[
                overview_display,
                farm_grid_display,
                zone_detail_display,
                insights_display,
                recommendations_display,
                alerts_display,
                status_banner,
            ],
        )

        # Individual steps
        btn_s1.click(
            fn=lambda: apply_step(0),
            outputs=[
                overview_display,
                farm_grid_display,
                zone_detail_display,
                insights_display,
                recommendations_display,
                alerts_display,
                status_banner,
            ],
        )
        btn_s2.click(
            fn=lambda: apply_step(1),
            outputs=[
                overview_display,
                farm_grid_display,
                zone_detail_display,
                insights_display,
                recommendations_display,
                alerts_display,
                status_banner,
            ],
        )
        btn_s3.click(
            fn=lambda: apply_step(2),
            outputs=[
                overview_display,
                farm_grid_display,
                zone_detail_display,
                insights_display,
                recommendations_display,
                alerts_display,
                status_banner,
            ],
        )
        btn_s4.click(
            fn=lambda: apply_step(3),
            outputs=[
                overview_display,
                farm_grid_display,
                zone_detail_display,
                insights_display,
                recommendations_display,
                alerts_display,
                status_banner,
            ],
        )

        # Zone Inspector buttons
        btn_z1.click(fn=lambda: select_zone(1), outputs=[farm_grid_display, zone_detail_display])
        btn_z2.click(fn=lambda: select_zone(2), outputs=[farm_grid_display, zone_detail_display])
        btn_z3.click(fn=lambda: select_zone(3), outputs=[farm_grid_display, zone_detail_display])
        btn_z4.click(fn=lambda: select_zone(4), outputs=[farm_grid_display, zone_detail_display])
        btn_z5.click(fn=lambda: select_zone(5), outputs=[farm_grid_display, zone_detail_display])
        btn_z6.click(fn=lambda: select_zone(6), outputs=[farm_grid_display, zone_detail_display])

    return demo


def main():

    parser = argparse.ArgumentParser(description="Seed Sensei Web Product Application")

    parser.add_argument(

        "--port",

        type=int,

        default=int(os.environ.get("PORT", 7860)),

        help="Port to run web app (default: 7860)"
    )
    parser.add_argument(
        "--no-share",
        action="store_true",
        help="Disable public sharing"
    )

    args = parser.parse_args()

    demo = build_app()

    print("\n" + "=" * 76)
    print("SEED SENSEI :: ENTERPRISE WEB PRODUCT")
    print("AI-Powered Precision Agriculture for Groundnut Farming")
    print("=" * 76)
    print(f"Local URL: http://127.0.0.1:{args.port}")

    if args.no_share:
        demo.launch(
            server_name="127.0.0.1",
            server_port=args.port,
            prevent_thread_lock=False,
            css=PRODUCT_CSS,
        )
    else:
        demo.launch(
            server_name="0.0.0.0",
            server_port=args.port,
            share=True,
            prevent_thread_lock=False,
            css=PRODUCT_CSS,
        )


if __name__ == "__main__":
    main()