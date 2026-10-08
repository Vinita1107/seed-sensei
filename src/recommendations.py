"""
Seed Sensei - AI Recommendation Engine
Translates Central AI predictions and risk analyses into concrete,
actionable agronomic decisions specifically calibrated for groundnut crops.
"""

from typing import Dict, Any, List
from src.config import THRESHOLDS


class AgronomicRecommendationEngine:
    """
    Expert agricultural recommendation system tailored to groundnut (oilseed) farming.
    Synthesizes ML stress predictions, risk scores, and phenological stage requirements.
    """

    @staticmethod
    def generate_zone_recommendation(zone_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate precision recommendations for an individual farm zone.
        """
        zone_name = zone_analysis["zone_name"]
        zone_id = zone_analysis["zone_id"]
        stress_class = zone_analysis["predicted_stress_class"]
        risk_category = zone_analysis["risk_category"]
        risk_score = zone_analysis["risk_score"]
        
        telemetry = zone_analysis["telemetry_used"]
        moisture = telemetry["soil_moisture"]
        air_temp = telemetry["air_temp"]
        nutrient = telemetry["nutrient_index"]
        crop_age = zone_analysis["crop_age_days"]

        # Growth stage context
        is_pegging_stage = (36 <= crop_age <= 65)
        is_pod_filling = (66 <= crop_age <= 90)
        is_maturation = (crop_age > 90)

        # 1. Determine Primary Irrigation Recommendation
        if moisture < THRESHOLDS["moisture_severe_dry"]:
            urgency = "CRITICAL (Immediate Action - Within 6 hrs)"
            action_type = "EMERGENCY_IRRIGATION"
            if is_pegging_stage:
                action = f"Prioritize immediate drip irrigation for {zone_name}."
                rationale = (
                    f"Soil moisture at {moisture:.1f}% is critically below wilting threshold (26%). "
                    f"Crop is at Day {crop_age} (Flowering & Pegging). Dry topsoil prevents peg (gynophore) "
                    "penetration into the soil, risking severe pod loss."
                )
                recommended_water_mm = 30.0
            else:
                action = f"Prioritize urgent irrigation for {zone_name}."
                rationale = (
                    f"Severe soil moisture deficit ({moisture:.1f}%). High risk of irreversible drought stress."
                )
                recommended_water_mm = 25.0

        elif moisture < THRESHOLDS["moisture_moderate_dry"]:
            urgency = "HIGH (Within 24 Hours)"
            action_type = "SCHEDULED_IRRIGATION"
            action = f"Schedule irrigation cycle for {zone_name}."
            rationale = (
                f"Soil moisture has dropped to {moisture:.1f}% (sub-optimal threshold < 36%). "
                "Moisture depletion is progressing toward critical stress."
            )
            recommended_water_mm = 18.0

        elif moisture > THRESHOLDS["moisture_waterlogged"]:
            urgency = "HIGH (Immediate Drainage Check)"
            action_type = "DRAINAGE_MANAGEMENT"
            action = f"Inspect surface drainage and pause irrigation in {zone_name}."
            rationale = (
                f"Soil moisture ({moisture:.1f}%) exceeds saturation capacity. "
                "Prolonged waterlogging induces root hypoxia and groundnut pod rot (stem rot / Sclerotium rolfsii)."
            )
            recommended_water_mm = 0.0

        elif air_temp > THRESHOLDS["air_temp_severe_heat"]:
            urgency = "HIGH (Heat Mitigation Required Today)"
            action_type = "THERMAL_PROTECTION"
            action = f"Apply protective canopy cooling and mulch in {zone_name}."
            rationale = (
                f"Ambient temperature ({air_temp:.1f}°C) exceeds critical groundnut threshold (36°C). "
                "Extreme heat during flowering/pegging risks pollen sterility and gynophore desiccation."
            )
            recommended_water_mm = 8.0

        else:
            urgency = "ROUTINE"
            action_type = "OPTIMAL_MAINTENANCE"
            action = f"Maintain standard soil management for {zone_name}."
            rationale = (
                f"Soil moisture ({moisture:.1f}%) and temperature ({air_temp:.1f}°C) are within healthy agronomic ranges. "
                "Root zone hydration is healthy."
            )
            recommended_water_mm = 0.0

        # 2. Thermal Stress Mitigation
        thermal_action = None
        if air_temp > THRESHOLDS["air_temp_severe_heat"]:
            thermal_action = (
                f"Severe ambient temperature detected ({air_temp:.1f}°C). "
                "Apply micro-sprinkler cooling mist or maintain organic straw mulch between rows to buffer soil temperature."
            )
        elif air_temp > THRESHOLDS["air_temp_moderate_heat"]:
            thermal_action = (
                f"Elevated temperatures ({air_temp:.1f}°C). Monitor for afternoon canopy wilting."
            )

        # 3. Nutrient / Calcium Advisory for Groundnut
        nutrient_action = None
        if is_pegging_stage and nutrient < THRESHOLDS["nutrient_optimal_min"]:
            nutrient_action = (
                "Groundnut flowering/pegging requires abundant calcium in the podding zone. "
                "Apply gypsum (calcium sulfate @ 200-400 kg/ha) to prevent empty pods ('pops')."
            )
        elif nutrient < THRESHOLDS["nutrient_moderate_min"]:
            nutrient_action = (
                "Low overall nutrient index. Consider foliar spray of micronutrients (boron & zinc) with light NPK top dressing."
            )

        # 4. Maturation / Harvest Guidance
        harvest_action = None
        if is_maturation:
            harvest_action = (
                f"Crop age is {crop_age} days (Maturation stage). Conduct pod maturity scrape test "
                "(dark inner pod shell indicates harvest readiness). Avoid excessive late irrigation."
            )

        return {
            "zone_id": zone_id,
            "zone_name": zone_name,
            "urgency": urgency,
            "action_type": action_type,
            "primary_action": action,
            "rationale": rationale,
            "recommended_irrigation_mm": recommended_water_mm,
            "thermal_mitigation": thermal_action,
            "nutrient_advisory": nutrient_action,
            "harvest_advisory": harvest_action,
            "risk_score": risk_score,
            "risk_category": risk_category,
        }

    @classmethod
    def generate_farm_recommendations(cls, zone_analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate recommendations for all zones, prioritized by risk urgency.
        """
        recs = [cls.generate_zone_recommendation(z) for z in zone_analyses]
        # Sort so high-risk critical actions appear first
        recs.sort(key=lambda r: r["risk_score"], reverse=True)
        return recs
