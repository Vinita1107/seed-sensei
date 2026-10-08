"""
Seed Sensei - Enterprise Product UI Engine
Translates backend agricultural ML pipeline data into modern, clean SaaS components.
Hides all technical internals (No TinyML, LoRa, RF, scikit-learn, probabilities, RMSE).
Focuses strictly on farmer & agronomist decision making.
"""

from typing import Dict, Any, List
import html

# Custom CSS for modern enterprise agricultural SaaS dashboard
PRODUCT_CSS = """
/* Seed Sensei Enterprise Theme */
body, .gradio-container { 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important; 
    background-color: #f8fafc !important; 
    color: #1e293b !important; 
}
/* Seed Sensei Navigation */
.seed-sensei-tabs {
    background: #ffffff !important;
}

.seed-sensei-tabs .tab-nav {
    background: #ffffff !important;
    border-bottom: 1px solid #cbd5e1 !important;
}

.seed-sensei-tabs .tab-nav button,
.seed-sensei-tabs button[role="tab"] {
    color: #334155 !important;
    background: #ffffff !important;
    opacity: 1 !important;
    font-weight: 600 !important;
    text-shadow: none !important;
}

.seed-sensei-tabs .tab-nav button:hover,
.seed-sensei-tabs button[role="tab"]:hover {
    color: #047857 !important;
    background: #f0fdf4 !important;
}

.seed-sensei-tabs .tab-nav button.selected,
.seed-sensei-tabs button[role="tab"][aria-selected="true"] {
    color: #047857 !important;
    background: #ffffff !important;
    opacity: 1 !important;
    border-bottom: 2px solid #047857 !important;
}
.brand-header {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 60%, #047857 100%);
    color: #ffffff;
    padding: 24px 32px;
    border-radius: 14px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(6, 78, 59, 0.15);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand-title {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.brand-tagline {
    font-size: 14px;
    color: #a7f3d0;
    margin-top: 4px;
    font-weight: 400;
}

.brand-badge {
    background: rgba(255, 255, 255, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.25);
    color: #ffffff;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}

.subtle-notice {
    font-size: 12px;
    color: #64748b;
    text-align: right;
    margin-top: 6px;
}

/* Control Bar */
.control-panel-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* Overview Metric Cards */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.metric-card:hover {
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    transform: translateY(-2px);
}

.metric-label {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    margin-bottom: 6px;
}

.metric-sub {
    font-size: 13px;
    color: #64748b;
}

/* Status Badges */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.3px;
}

.status-healthy {
    background-color: #dcfce7;
    color: #15803d;
    border: 1px solid #bbf7d0;
}

.status-attention {
    background-color: #fef3c7;
    color: #b45309;
    border: 1px solid #fde68a;
}

.status-critical {
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fecaca;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

.dot-healthy { background-color: #22c55e; }
.dot-attention { background-color: #f59e0b; }
.dot-critical { background-color: #ef4444; }

/* Farm Grid Map */
.farm-map-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 14px;
    margin-bottom: 24px;
}

.zone-tile {
    background: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: left;
}

.zone-tile:hover {
    border-color: #059669;
    box-shadow: 0 4px 12px rgba(5, 150, 105, 0.1);
}

.zone-tile.active-zone {
    border-color: #059669;
    background: #f0fdf4;
}

.zone-tile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.zone-name {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
}

.zone-metric-line {
    font-size: 13px;
    color: #475569;
    margin-bottom: 4px;
}

/* Zone Detail Inspector */
.inspector-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    margin-top: 16px;
}

/* Action Cards */
.action-card {
    background: #ffffff;
    border-left: 5px solid #059669;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.action-card.critical {
    border-left-color: #ef4444;
}

.action-card.attention {
    border-left-color: #f59e0b;
}

/* WhatsApp Chat Bubble Preview */
.whatsapp-preview-box {
    background: #e5ddd5;
    background-image: radial-gradient(#d4cbbe 10%, transparent 11%);
    background-size: 12px 12px;
    padding: 20px;
    border-radius: 12px;
    margin-top: 14px;
    max-width: 520px;
}

.whatsapp-bubble {
    background: #ffffff;
    border-radius: 8px 8px 8px 0px;
    padding: 14px 16px;
    font-size: 14px;
    line-height: 1.5;
    color: #111827;
    box-shadow: 0 1px 2px rgba(0,0,0,0.15);
}

.whatsapp-time {
    font-size: 11px;
    color: #9ca3af;
    text-align: right;
    margin-top: 6px;
}
"""


def get_zone_status_info(risk_category: str) -> tuple[str, str, str]:
    """Return (display_label, css_class, dot_class) based on risk category."""
    if risk_category == "HIGH RISK":
        return "Critical", "status-critical", "dot-critical"
    elif risk_category == "MODERATE RISK":
        return "Attention", "status-attention", "dot-attention"
    else:
        return "Healthy", "status-healthy", "dot-healthy"


def render_brand_header_html() -> str:
    """Render top product banner with inline stylesheet."""
    return f"""
    <style>
    {PRODUCT_CSS}
    </style>
    <div class="brand-header">
        <div>
            <div class="brand-title">
                🌱 SEED SENSEI
            </div>
            <div class="brand-tagline">
                AI-Powered Precision Agriculture for Groundnut Farming
            </div>
        </div>
        <div style="text-align: right;">
            <span class="brand-badge">Groundnut (Arachis hypogaea) • Flowering & Pegging</span>
            <div class="subtle-notice">Prototype powered by simulated agricultural data</div>
        </div>
    </div>
    """


def render_overview_cards_html(pipeline_output: Dict[str, Any]) -> str:
    """
    Render 4 key enterprise metric cards:
    - Predicted Yield (t/ha)
    - Farm Health (%)
    - High-Risk Areas (count)
    - Water Stress level
    """
    farm_summary = pipeline_output["farm_summary"]
    zone_results = pipeline_output["zone_results"]
    
    # 1. Predicted Yield in t/ha
    avg_yield_kg = farm_summary.get("average_predicted_yield_kg_ha", 2200.0)
    avg_yield_tons = avg_yield_kg / 1000.0
    
    # 2. Farm Health (100 - risk_score)
    farm_risk = farm_summary.get("overall_farm_risk_score", 30.0)
    farm_health_pct = int(max(10, min(100, round(100.0 - farm_risk))))
    
    # 3. High Risk Areas Count
    high_risk_count = farm_summary.get("high_risk_count", 0)
    
    # 4. Water Stress Condition
    moistures = [z["raw_sensor_data"]["soil_moisture"] for z in zone_results]
    min_moisture = min(moistures) if moistures else 50.0
    if min_moisture < 26.0:
        water_stress = "Critical"
        water_stress_color = "#b91c1c"
        water_desc = f"Lowest area at {min_moisture:.1f}% moisture"
    elif min_moisture < 36.0:
        water_stress = "Moderate"
        water_stress_color = "#b45309"
        water_desc = f"Lowest area at {min_moisture:.1f}% moisture"
    else:
        water_stress = "Optimal"
        water_stress_color = "#15803d"
        water_desc = "All zones within healthy moisture band"

    # Overall Status badge
    overall_status = farm_summary.get("overall_status", "HEALTHY / OPTIMAL")
    if "CRITICAL" in overall_status:
        status_label = "CRITICAL ACTION REQUIRED"
        status_cls = "status-critical"
        dot_cls = "dot-critical"
    elif "ATTENTION" in overall_status or "MODERATE" in overall_status:
        status_label = "ATTENTION REQUIRED"
        status_cls = "status-attention"
        dot_cls = "dot-attention"
    else:
        status_label = "HEALTHY"
        status_cls = "status-healthy"
        dot_cls = "dot-healthy"

    return f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #0f172a;">GROUNDNUT FARM • 6 SPATIAL ZONES</h3>
                <span style="font-size: 13px; color: #64748b;">Autonomous continuous soil & crop health monitoring</span>
            </div>
            <div>
                <span class="status-pill {status_cls}">
                    <span class="status-dot {dot_cls}"></span>
                    {status_label}
                </span>
            </div>
        </div>

        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-label">Predicted Yield</div>
                <div class="metric-value">{avg_yield_tons:.2f} <span style="font-size: 18px; font-weight: 500; color: #64748b;">t/ha</span></div>
                <div class="metric-sub">Benchmark Potential: 3.40 t/ha</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Farm Health Index</div>
                <div class="metric-value" style="color: {'#15803d' if farm_health_pct >= 70 else ('#b45309' if farm_health_pct >= 45 else '#b91c1c')};">
                    {farm_health_pct}%
                </div>
                <div class="metric-sub">Weighted across all 6 management zones</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">High-Risk Areas</div>
                <div class="metric-value" style="color: {'#b91c1c' if high_risk_count > 0 else '#15803d'};">
                    {high_risk_count} <span style="font-size: 16px; font-weight: 500; color: #64748b;">of 6 zones</span>
                </div>
                <div class="metric-sub">{'Requires irrigation or heat intervention' if high_risk_count > 0 else 'All zones operating normally'}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Water Stress</div>
                <div class="metric-value" style="color: {water_stress_color}; font-size: 26px;">
                    {water_stress}
                </div>
                <div class="metric-sub">{water_desc}</div>
            </div>
        </div>
    </div>
    """


def render_farm_map_grid_html(pipeline_output: Dict[str, Any], selected_zone_id: int = 1) -> str:
    """
    Render 3x2 interactive Farm Map Field Grid.
    """
    zone_results = pipeline_output["zone_results"]
    
    tiles_html = []
    for z in zone_results:
        z_id = z["zone_id"]
        ai = z["central_ai_analysis"]
        raw = z["raw_sensor_data"]
        risk_cat = ai["risk_category"]
        label, badge_cls, dot_cls = get_zone_status_info(risk_cat)
        
        # Determine soil condition description
        moisture = raw["soil_moisture"]
        temp = raw["air_temp"]
        
        if moisture < 26.0:
            moist_desc = "Critically Dry"
            moist_color = "#b91c1c"
        elif moisture < 36.0:
            moist_desc = "Depleting"
            moist_color = "#b45309"
        else:
            moist_desc = "Adequate"
            moist_color = "#15803d"

        if temp > 36.0:
            temp_desc = "Extreme Heat"
            temp_color = "#b91c1c"
        elif temp > 32.5:
            temp_desc = "Elevated"
            temp_color = "#b45309"
        else:
            temp_desc = "Optimal"
            temp_color = "#15803d"

        is_selected = "active-zone" if z_id == selected_zone_id else ""

        tile = f"""
        <div class="zone-tile {is_selected}">
            <div class="zone-tile-header">
                <span class="zone-name">Zone {z_id}</span>
                <span class="status-pill {badge_cls}">
                    <span class="status-dot {dot_cls}"></span>
                    {label}
                </span>
            </div>
            <div class="zone-metric-line">
                <strong>Soil Moisture:</strong> <span style="color: {moist_color}; font-weight: 600;">{moist_desc} ({moisture:.1f}%)</span>
            </div>
            <div class="zone-metric-line">
                <strong>Temperature:</strong> <span style="color: {temp_color}; font-weight: 600;">{temp_desc} ({temp:.1f}°C)</span>
            </div>
            <div class="zone-metric-line" style="margin-top: 6px; font-size: 12px; color: #64748b;">
                Soil: {z['recommendation'].get('soil_type', 'Sandy Loam')} • Groundnut Day 50
            </div>
        </div>
        """
        tiles_html.append(tile)

    return f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #0f172a;">FIELD MANAGEMENT MAP (6 LOGICAL ZONES)</h3>
                <span style="font-size: 13px; color: #64748b;">Visual zoning representation of groundnut acreage</span>
            </div>
            <span style="font-size: 12px; color: #047857; font-weight: 600; background: #ecfdf5; padding: 4px 10px; border-radius: 6px;">
                ● Real-time AI Zone Health Mapping
            </span>
        </div>
        <div class="farm-map-grid">
            {''.join(tiles_html)}
        </div>
    </div>
    """


def render_zone_detail_drawer_html(pipeline_output: Dict[str, Any], zone_id: int = 1) -> str:
    """
    Render inspector card for selected zone.
    """
    target_zone = None
    for z in pipeline_output["zone_results"]:
        if z["zone_id"] == zone_id:
            target_zone = z
            break
            
    if not target_zone:
        target_zone = pipeline_output["zone_results"][0]

    ai = target_zone["central_ai_analysis"]
    raw = target_zone["raw_sensor_data"]
    rec = target_zone["recommendation"]
    z_name = target_zone.get("zone_name", f"Zone {zone_id}")
    risk_cat = ai["risk_category"]
    label, badge_cls, dot_cls = get_zone_status_info(risk_cat)

    # Convert yield to t/ha
    yield_t_ha = ai["predicted_yield_kg_ha"] / 1000.0
    moisture = raw["soil_moisture"]
    air_temp = raw["air_temp"]

    # AI interpretation in natural language
    if moisture < 26.0:
        interpretation = (
            f"{z_name} is in critical soil moisture deficit. Topsoil has dropped to {moisture:.1f}%. "
            "Because groundnut plants are in the Flowering & Pegging stage, gynophores cannot penetrate "
            "hardened dry soil to form pods, causing severe yield reduction."
        )
    elif moisture < 36.0:
        interpretation = (
            f"{z_name} is showing noticeable moisture depletion ({moisture:.1f}%). Without irrigation within 24 hours, "
            "it will cross into drought stress."
        )
    elif air_temp > 36.0:
        interpretation = (
            f"{z_name} is experiencing elevated heat stress ({air_temp:.1f}°C). Temperatures above 36°C "
            "impair pollen viability and flower retention."
        )
    else:
        interpretation = (
            f"{z_name} is maintaining optimal agronomic conditions. Root hydration ({moisture:.1f}%) "
            f"and ambient temperatures ({air_temp:.1f}°C) support vigorous pegging and pod development."
        )

    return f"""
    <div class="inspector-card">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 14px; margin-bottom: 16px;">
            <div>
                <h3 style="margin: 0; font-size: 20px; font-weight: 700; color: #0f172a;">{z_name} Detailed Analysis</h3>
                <span style="font-size: 13px; color: #64748b;">Crop: Groundnut • Phenology: Flowering & Pegging (Day 50)</span>
            </div>
            <span class="status-pill {badge_cls}" style="font-size: 14px; padding: 6px 14px;">
                <span class="status-dot {dot_cls}"></span>
                {label}
            </span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 20px;">
            <div style="background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <div style="font-size: 12px; color: #64748b; font-weight: 600;">SOIL MOISTURE</div>
                <div style="font-size: 22px; font-weight: 700; color: {'#b91c1c' if moisture < 26 else ('#b45309' if moisture < 36 else '#15803d')};">
                    {moisture:.1f}%
                </div>
                <div style="font-size: 12px; color: #64748b;">Optimal band: 45 - 68%</div>
            </div>

            <div style="background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <div style="font-size: 12px; color: #64748b; font-weight: 600;">TEMPERATURE</div>
                <div style="font-size: 22px; font-weight: 700; color: {'#b91c1c' if air_temp > 36 else ('#b45309' if air_temp > 32 else '#15803d')};">
                    {air_temp:.1f}°C
                </div>
                <div style="font-size: 12px; color: #64748b;">Optimal band: 24 - 31°C</div>
            </div>

            <div style="background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <div style="font-size: 12px; color: #64748b; font-weight: 600;">PROJECTED HARVEST</div>
                <div style="font-size: 22px; font-weight: 700; color: #0f172a;">
                    {yield_t_ha:.2f} t/ha
                </div>
                <div style="font-size: 12px; color: #64748b;">Potential: 3.40 t/ha</div>
            </div>

            <div style="background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0;">
                <div style="font-size: 12px; color: #64748b; font-weight: 600;">FIELD RISK LEVEL</div>
                <div style="font-size: 22px; font-weight: 700; color: {'#b91c1c' if 'HIGH' in risk_cat else ('#b45309' if 'MODERATE' in risk_cat else '#15803d')};">
                    {risk_cat}
                </div>
                <div style="font-size: 12px; color: #64748b;">Evaluated across 7 microclimate factors</div>
            </div>
        </div>

        <div style="margin-bottom: 16px;">
            <div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">🧠 AI FIELD INTERPRETATION</div>
            <div style="background: #f1f5f9; padding: 14px 18px; border-radius: 8px; font-size: 14px; line-height: 1.6; color: #334155;">
                {interpretation}
            </div>
        </div>

        <div>
            <div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 6px;">⚡ RECOMMENDED ACTION</div>
            <div style="background: #ecfdf5; border: 1px solid #a7f3d0; padding: 14px 18px; border-radius: 8px; font-size: 14px; line-height: 1.6; color: #065f46;">
                <strong>{rec['primary_action']}</strong>
                <div style="margin-top: 4px; font-size: 13px; color: #047857;">{rec['rationale']}</div>
            </div>
        </div>
    </div>
    """


def render_ai_insights_html(pipeline_output: Dict[str, Any]) -> str:
    """
    Render AI Insights page with natural-language agronomic conclusions.
    """
    farm_summary = pipeline_output["farm_summary"]
    zone_results = pipeline_output["zone_results"]
    
    high_zones = farm_summary.get("high_risk_zone_names", [])
    mod_zones = farm_summary.get("moderate_risk_zone_names", [])
    avg_yield_t = farm_summary.get("average_predicted_yield_kg_ha", 2200.0) / 1000.0

    insights = []

    # Moisture stress insight
    dry_zones = [z for z in zone_results if z["raw_sensor_data"]["soil_moisture"] < 28.0]
    if dry_zones:
        names = ", ".join([f"Zone {z['zone_id']}" for z in dry_zones])
        insights.append({
            "title": "Severe Soil Moisture Deficit Detected",
            "body": f"{names} is showing critical moisture depletion below the 26% wilting threshold. Groundnut is in the Flowering & Pegging stage (Day 50), which has the highest sensitivity to drought in the entire crop cycle. Pegs entering dry soil will suffer desiccation without irrigation.",
            "impact": "High yield penalty if unaddressed today",
            "type": "critical"
        })

    # Heat stress insight
    hot_zones = [z for z in zone_results if z["raw_sensor_data"]["air_temp"] > 35.5]
    if hot_zones:
        names = ", ".join([f"Zone {z['zone_id']}" for z in hot_zones])
        insights.append({
            "title": "Elevated Thermal Canopy Stress",
            "body": f"{names} is experiencing temperatures exceeding 36°C. Excessive ambient heat restricts pollination and induces midday flower wilting. Supplemental row mulching or cooling mist is recommended.",
            "impact": "Reduces floral retention and peg set",
            "type": "attention"
        })

    # Farm trend
    insights.append({
        "title": "Farm Irrigation & Moisture Trend",
        "body": "Spatial analysis shows rapid soil moisture depletion on sandy loam zones (Zone 2, Zone 4). The current farm trend indicates rising irrigation demand across the southern plots.",
        "impact": "Plan irrigation cycles within 24 to 48 hours",
        "type": "info"
    })

    # Yield gap projection
    gap_pct = max(0.0, (1.0 - (avg_yield_t / 3.40)) * 100.0)
    insights.append({
        "title": "Harvest Yield Benchmark Projection",
        "body": f"The current projected farm harvest yield is {avg_yield_t:.2f} t/ha compared to the regional potential benchmark of 3.40 t/ha (a {gap_pct:.1f}% yield gap). Restoring optimal root-zone hydration can recover up to 65% of this yield potential.",
        "impact": f"Yield forecast: {avg_yield_t:.2f} t/ha",
        "type": "info"
    })

    # Healthy reassurance
    healthy_zones = [z for z in zone_results if z["central_ai_analysis"]["risk_category"] == "LOW RISK"]
    if healthy_zones:
        h_names = ", ".join([f"Zone {z['zone_id']}" for z in healthy_zones])
        insights.append({
            "title": "Optimal Growth Zones",
            "body": f"{h_names} are maintaining balanced hydration and moderate temperatures. Root nodules and foliage health are stable.",
            "impact": "Standard routine maintenance",
            "type": "healthy"
        })

    cards_html = []
    for ins in insights:
        border_color = "#ef4444" if ins["type"] == "critical" else ("#f59e0b" if ins["type"] == "attention" else ("#10b981" if ins["type"] == "healthy" else "#0284c7"))
        bg_pill = "#fee2e2" if ins["type"] == "critical" else ("#fef3c7" if ins["type"] == "attention" else ("#dcfce7" if ins["type"] == "healthy" else "#e0f2fe"))
        text_pill = "#b91c1c" if ins["type"] == "critical" else ("#b45309" if ins["type"] == "attention" else ("#15803d" if ins["type"] == "healthy" else "#0369a1"))

        card = f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 5px solid {border_color}; border-radius: 10px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; font-size: 16px; font-weight: 700; color: #0f172a;">{ins['title']}</h4>
                <span style="background: {bg_pill}; color: {text_pill}; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 12px;">
                    {ins['impact']}
                </span>
            </div>
            <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #334155;">{ins['body']}</p>
        </div>
        """
        cards_html.append(card)

    return f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="margin-bottom: 18px;">
            <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #0f172a;">AI FIELD INSIGHTS & CROP INTELLIGENCE</h3>
            <span style="font-size: 13px; color: #64748b;">Autonomous synthesis of farm-wide microclimate, soil moisture, and crop phenology</span>
        </div>
        {''.join(cards_html)}
    </div>
    """


def render_recommendations_html(pipeline_output: Dict[str, Any]) -> str:
    """
    Render Recommendations page with actionable enterprise cards.
    """
    recs = pipeline_output["farm_recommendations"]
    
    cards_html = []
    for rec in recs:
        urgency = rec["urgency"]
        z_name = rec["zone_name"]
        action = rec["primary_action"]
        rationale = rec["rationale"]
        
        if "CRITICAL" in urgency:
            border_cls = "critical"
            tag_bg = "#fee2e2"
            tag_text = "#b91c1c"
            tag_label = "URGENT ACTION REQUIRED"
        elif "HIGH" in urgency:
            border_cls = "attention"
            tag_bg = "#fef3c7"
            tag_text = "#b45309"
            tag_label = "HIGH PRIORITY"
        else:
            border_cls = "healthy"
            tag_bg = "#dcfce7"
            tag_text = "#15803d"
            tag_label = "ROUTINE"

        water_note = ""
        if rec.get("recommended_irrigation_mm", 0) > 0:
            water_note = f"""
            <div style="margin-top: 10px; font-size: 13px; color: #065f46; background: #f0fdf4; padding: 8px 12px; border-radius: 6px; display: inline-block;">
                💧 <strong>Irrigation Volume:</strong> Apply approx. {int(rec['recommended_irrigation_mm'])} mm through drip lines.
            </div>
            """

        card = f"""
        <div class="action-card {border_cls}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="background: {tag_bg}; color: {tag_text}; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 12px;">
                    {tag_label} • {z_name}
                </span>
                <span style="font-size: 12px; color: #64748b;">Groundnut • Day 50 (Pegging)</span>
            </div>
            <h4 style="margin: 0 0 8px 0; font-size: 17px; font-weight: 700; color: #0f172a;">{action}</h4>
            <p style="margin: 0; font-size: 14px; line-height: 1.5; color: #475569;"><strong>Agronomic Reason:</strong> {rationale}</p>
            {water_note}
            {f'<div style="margin-top: 8px; font-size: 13px; color: #b45309;">☀️ {rec["thermal_mitigation"]}</div>' if rec.get("thermal_mitigation") else ""}
            {f'<div style="margin-top: 8px; font-size: 13px; color: #0369a1;">🧪 {rec["nutrient_advisory"]}</div>' if rec.get("nutrient_advisory") else ""}
        </div>
        """
        cards_html.append(card)

    return f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="margin-bottom: 18px;">
            <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #0f172a;">PRECISION AGRONOMIC RECOMMENDATIONS</h3>
            <span style="font-size: 13px; color: #64748b;">Targeted, zone-specific directives prioritized by agronomic urgency</span>
        </div>
        {''.join(cards_html)}
    </div>
    """


def render_alert_center_html(pipeline_output: Dict[str, Any]) -> str:
    """
    Render Alert Center with farmer alert dispatch cards and WhatsApp message preview.
    """
    farm_summary = pipeline_output["farm_summary"]
    recs = pipeline_output["farm_recommendations"]
    high_zones = farm_summary.get("high_risk_zone_names", [])
    
    # Urgent alerts
    urgent_recs = [r for r in recs if "CRITICAL" in r["urgency"] or "HIGH" in r["urgency"]]
    
    alert_cards = []
    if urgent_recs:
        for r in urgent_recs:
            card = f"""
            <div style="background: #fff5f5; border: 1px solid #fed7d7; border-radius: 10px; padding: 16px 20px; margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="color: #9b2c2c; font-weight: 700; font-size: 14px;">🚨 URGENT FIELD ALERT • {r['zone_name']}</span>
                    <span style="font-size: 12px; color: #718096;">Triggered Today</span>
                </div>
                <div style="font-size: 15px; font-weight: 600; color: #1a202c; margin-bottom: 6px;">
                    {r['primary_action']}
                </div>
                <div style="font-size: 13px; color: #4a5568;">
                    {r['rationale']}
                </div>
            </div>
            """
            alert_cards.append(card)
    else:
        alert_cards.append("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 16px 20px; margin-bottom: 14px;">
            <div style="color: #15803d; font-weight: 700; font-size: 14px;">✅ ALL FIELD ZONES HEALTHY</div>
            <div style="font-size: 13px; color: #166534; margin-top: 4px;">
                No urgent environmental or moisture alerts active. Soil conditions and temperatures are within optimal range.
            </div>
        </div>
        """)

    # Build WhatsApp message preview
    if high_zones:
        zones_str = ", ".join(high_zones)
        wa_text = f"🌱 Seed Sensei Field Advisory\nCrop: Groundnut Field\nStatus: Attention Required\n\nHigh stress detected in {zones_str}.\n"
        for idx, ur in enumerate(urgent_recs[:2], 1):
            wa_text += f"{idx}. {ur['primary_action']}\n"
        wa_text += "\nOther zones are stable. Open Seed Sensei dashboard for full map."
    else:
        wa_text = "🌱 Seed Sensei Field Advisory\nCrop: Groundnut Field\nStatus: Healthy & Optimal\n\nAll 6 zones have adequate moisture and healthy soil conditions. No special action needed today."

    wa_encoded = html.escape(wa_text).replace("\n", "<br>")
    wa_url = "https://wa.me/?text=" + html.escape(wa_text.replace("\n", "%0A"))

    return f"""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="margin-bottom: 18px;">
            <h3 style="margin: 0; font-size: 18px; font-weight: 700; color: #0f172a;">FARMER ALERT CENTER</h3>
            <span style="font-size: 13px; color: #64748b;">Direct grower notifications and mobile messaging integration</span>
        </div>

        <div style="margin-bottom: 24px;">
            {''.join(alert_cards)}
        </div>

        <div style="border-top: 1px solid #e2e8f0; padding-top: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; font-size: 15px; font-weight: 700; color: #0f172a;">📱 WHATSAPP FARMER NOTIFICATION</h4>
                <span style="font-size: 12px; font-weight: 600; color: #047857; background: #ecfdf5; padding: 4px 10px; border-radius: 6px;">
                    ✓ Farmer alert generated • Ready to send
                </span>
            </div>
            <p style="font-size: 13px; color: #64748b; margin: 0 0 12px 0;">
                Preview of the plain-language notification prepared for the grower's phone (Free of technical jargon):
            </p>

            <div class="whatsapp-preview-box">
                <div class="whatsapp-bubble">
                    {wa_encoded}
                    <div class="whatsapp-time">08:45 AM ✓✓</div>
                </div>
            </div>

            <div style="margin-top: 14px;">
                <a href="{wa_url}" target="_blank" style="display: inline-flex; align-items: center; gap: 8px; background: #25d366; color: #ffffff; text-decoration: none; padding: 10px 18px; border-radius: 8px; font-size: 13px; font-weight: 700; box-shadow: 0 2px 4px rgba(37, 211, 102, 0.25);">
                    💬 Send via WhatsApp Web
                </a>
                <span style="font-size: 12px; color: #64748b; margin-left: 12px;">
                    No simulated fake delivery claims. Link opens official WhatsApp dispatcher.
                </span>
            </div>
        </div>
    </div>
    """
