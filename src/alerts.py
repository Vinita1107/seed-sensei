"""
Seed Sensei - Farmer Alert Module
Produces plain-language, non-technical advisories for groundnut growers.
Abstracts all engineering complexity (TinyML, LoRa, RF, feature vectors, ML metrics)
into simple, actionable farming decisions.
"""

from typing import Dict, Any, List


class FarmerAlertGenerator:
    """
    Translates complex multi-zone AI analytics into simple, farmer-friendly advisories.
    """

    @staticmethod
    def generate_farmer_alert(farm_summary: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
        """
        Generate a concise farmer alert card.
        """
        status = farm_summary.get("overall_status", "NORMAL")
        high_risk_zones = farm_summary.get("high_risk_zone_names", [])
        mod_risk_zones = farm_summary.get("moderate_risk_zone_names", [])

        # 1. Farmer Status
        if "CRITICAL" in status:
            display_status = "URGENT ACTION NEEDED"
        elif "ATTENTION" in status:
            display_status = "ATTENTION REQUIRED"
        elif "MODERATE" in status:
            display_status = "WATCH CLOSELY"
        else:
            display_status = "HEALTHY & OPTIMAL"

        # 2. What is happening?
        what_is_happening = []
        if high_risk_zones:
            zones_str = ", ".join(high_risk_zones)
            what_is_happening.append(f"Field stress detected in {zones_str}.")
            urgent_types = [r.get("action_type", "") for r in recommendations if r["zone_name"] in high_risk_zones]
            if any("IRRIGATION" in t for t in urgent_types):
                what_is_happening.append("Soil is critically dry during the sensitive flowering/pegging period.")
            if any("THERMAL" in t for t in urgent_types):
                what_is_happening.append("Intense heat wave is stressing groundnut flowers.")
        elif mod_risk_zones:
            zones_str = ", ".join(mod_risk_zones)
            what_is_happening.append(f"Moisture levels in {zones_str} are dropping below ideal levels.")
        else:
            what_is_happening.append("All field zones have adequate moisture and healthy soil conditions.")
            what_is_happening.append("Your groundnut crop is growing well.")

        # 3. What should I do?
        actions = []
        # Look at prioritized recommendations
        urgent_recs = [r for r in recommendations if "CRITICAL" in r["urgency"] or "HIGH" in r["urgency"]]
        
        if urgent_recs:
            for rec in urgent_recs:
                z_name = rec["zone_name"]
                if "IRRIGATION" in rec["action_type"]:
                    mm = rec.get("recommended_irrigation_mm", 25)
                    actions.append(f"Turn on irrigation for {z_name} today (apply approx. {int(mm)} mm of water).")
                elif "THERMAL" in rec["action_type"]:
                    actions.append(f"Protect {z_name} from extreme heat: run cooling mist or inspect row mulch.")
                elif "DRAINAGE" in rec["action_type"]:
                    actions.append(f"Check {z_name} for standing water and ensure drainage channels are clear.")
            
            # Non-urgent zones reassurance
            safe_zones = [r["zone_name"] for r in recommendations if r not in urgent_recs]
            if safe_zones:
                actions.append(f"Other areas ({', '.join(safe_zones)}) are healthy. No special action needed there today.")
        else:
            actions.append("Maintain routine field check. No special watering needed today.")
            actions.append("Next scheduled soil review tomorrow morning.")

        # Format clean card
        lines = [
            "------------------------------------------------------------",
            "SEED SENSEI - FARMER ADVISORY",
            "CROP: GROUNDNUT FIELD",
            "------------------------------------------------------------",
            f"FIELD STATUS : {display_status}",
            "",
            "WHAT IS HAPPENING?",
        ]
        for item in what_is_happening:
            lines.append(f"  * {item}")

        lines.append("")
        lines.append("WHAT SHOULD I DO?")
        for idx, act in enumerate(actions, 1):
            lines.append(f"  {idx}. {act}")
            
        lines.append("------------------------------------------------------------")
        return "\n".join(lines)
