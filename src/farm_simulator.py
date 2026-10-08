"""
Seed Sensei - Multi-Zone Farm Simulation Engine
Maintains state for logical Zones 1 through 6, orchestrates simulated IoT telemetry,
and triggers dynamic stress scenarios for live demonstrations.
"""

from typing import Dict, Any, List
from src.config import FARM_ZONES, DEFAULT_CROP_AGE_DAYS
from src.tinyml_edge import TinyMLEdgeNode
from src.communication import LoRaTransceiverSimulator, LoRaGatewaySimulator
from src.central_ai import CentralAIEngine
from src.recommendations import AgronomicRecommendationEngine
from src.alerts import FarmerAlertGenerator


class GroundnutFarmSimulator:
    """
    Simulation coordinator for the 6-zone groundnut farm.
    Maintains telemetry state and pipeline execution across edge, LoRa, and AI layers.
    """

    def __init__(self, crop_age_days: int = DEFAULT_CROP_AGE_DAYS):
        self.crop_age_days = crop_age_days
        self.zone_states = {}
        self.edge_nodes = {}
        self.lora_nodes = {}
        self.lora_gateway = LoRaGatewaySimulator()
        self.central_ai = CentralAIEngine()

        # Initialize nodes for Zones 1-6
        for zone_id, zone_info in FARM_ZONES.items():
            node_id = zone_info["node_id"]
            self.edge_nodes[zone_id] = TinyMLEdgeNode(node_id, zone_id)
            self.lora_nodes[zone_id] = LoRaTransceiverSimulator(node_id, zone_id)

        # Start with standard realistic spatial variation preset
        self.set_spatial_variation_preset()

    def set_balanced_normal(self):
        """Set all zones to optimal, healthy groundnut conditions."""
        for zone_id in FARM_ZONES:
            self.zone_states[zone_id] = {
                "zone_id": zone_id,
                "crop_age_days": self.crop_age_days,
                "soil_moisture": 52.0 + (zone_id * 1.5),
                "soil_temp": 25.5 + (zone_id * 0.3),
                "air_temp": 27.5 + (zone_id * 0.4),
                "humidity": 65.0 - (zone_id * 1.0),
                "rainfall_mm": 0.0,
                "nutrient_index": 0.82,
            }

    def set_spatial_variation_preset(self):
        """
        Sets realistic multi-zone spatial diversity matching the project specification:
        - Zone 1: Normal (54% moist, 27.5°C)
        - Zone 2: Moisture Stress (19.4% moist, 35.6°C)
        - Zone 3: Normal (52% moist, 28°C)
        - Zone 4: Moderate Risk (34% moist, 32.5°C)
        - Zone 5: Normal (56% moist, 27°C)
        - Zone 6: Heat Stress (41% moist, 38.5°C)
        """
        self.zone_states = {
            1: {
                "zone_id": 1,
                "crop_age_days": self.crop_age_days,
                "soil_moisture": 54.0,
                "soil_temp": 25.5,
                "air_temp": 27.5,
                "humidity": 68.0,
                "rainfall_mm": 0.0,
                "nutrient_index": 0.85,
            },
            2: {
                "zone_id": 2,
                "crop_age_days": self.crop_age_days,
                "soil_moisture": 19.4,
                "soil_temp": 32.0,
                "air_temp": 35.6,
                "humidity": 38.0,
                "rainfall_mm": 0.0,
                "nutrient_index": 0.72,
            },
            3: {
                "zone_id": 3,
                "crop_age_days": self.crop_age_days,
                "soil_moisture": 52.0,
                "soil_temp": 26.0,
                "air_temp": 28.0,
                "humidity": 64.0,
                "rainfall_mm": 0.0,
                "nutrient_index": 0.80,
            },
            4: {
                "zone_id": 4,
                "crop_age_days": self.crop_age_days,
                "soil_moisture": 34.0,
                "soil_temp": 29.5,
                "air_temp": 32.5,
                "humidity": 48.0,
                "rainfall_mm": 0.0,
                "nutrient_index": 0.65,
            },
            5: {
                "zone_id": 5,
                "crop_age_days": self.crop_age_days,
                "soil_moisture": 56.5,
                "soil_temp": 25.0,
                "air_temp": 27.0,
                "humidity": 66.0,
                "rainfall_mm": 0.0,
                "nutrient_index": 0.88,
            },
            6: {
                "zone_id": 6,
                "crop_age_days": self.crop_age_days,
                "soil_moisture": 41.0,
                "soil_temp": 34.0,
                "air_temp": 38.5,
                "humidity": 34.0,
                "rainfall_mm": 0.0,
                "nutrient_index": 0.76,
            },
        }

    def update_zone_telemetry(self, zone_id: int, **kwargs):
        """Update specific sensor telemetry for a zone."""
        if zone_id in self.zone_states:
            self.zone_states[zone_id].update(kwargs)

    @staticmethod
    def get_dry_stress_scenario_steps() -> List[Dict[str, Any]]:
        """
        Step-by-step drying scenario for Zone 2:
        45% -> 34% -> 26% -> 18% moisture progression.
        """
        return [
            {
                "step": 1,
                "description": "Baseline Optimal Conditions (Moisture: 45.0%, Temp: 28.0°C)",
                "zone_id": 2,
                "soil_moisture": 45.0,
                "air_temp": 28.0,
                "humidity": 62.0,
                "soil_temp": 26.0,
            },
            {
                "step": 2,
                "description": "Mild Drying / Onset of Deficit (Moisture: 34.0%, Temp: 31.0°C)",
                "zone_id": 2,
                "soil_moisture": 34.0,
                "air_temp": 31.0,
                "humidity": 50.0,
                "soil_temp": 28.5,
            },
            {
                "step": 3,
                "description": "Moderate Moisture Stress (Moisture: 26.0%, Temp: 33.5°C)",
                "zone_id": 2,
                "soil_moisture": 26.0,
                "air_temp": 33.5,
                "humidity": 42.0,
                "soil_temp": 30.5,
            },
            {
                "step": 4,
                "description": "Severe Critical Drought Stress (Moisture: 18.0%, Temp: 35.6°C)",
                "zone_id": 2,
                "soil_moisture": 18.0,
                "air_temp": 35.6,
                "humidity": 35.0,
                "soil_temp": 32.5,
            },
        ]

    def execute_zone_pipeline(self, zone_id: int) -> Dict[str, Any]:
        """
        Execute full pipeline for a single zone:
        Sensor -> TinyML -> LoRa TX -> LoRa RX -> Central AI -> Recommendation
        """
        raw_telemetry = self.zone_states[zone_id]

        # 1. Edge Layer (TinyML on node)
        edge_node = self.edge_nodes[zone_id]
        edge_result = edge_node.run_inference(raw_telemetry)

        # 2. Communication Layer (LoRa packet framing)
        lora_node = self.lora_nodes[zone_id]
        raw_bytes, hex_dump, tx_meta = lora_node.encode_packet(edge_result)

        # 3. Gateway Receiving
        rx_frame = self.lora_gateway.decode_packet(raw_bytes)
        # Augment gateway frame with non-LoRa fields (age, nutrient, soil_temp)
        rx_frame["crop_age_days"] = raw_telemetry.get("crop_age_days", self.crop_age_days)
        rx_frame["nutrient_index"] = raw_telemetry.get("nutrient_index", 0.75)
        rx_frame["soil_temp"] = raw_telemetry.get("soil_temp", rx_frame["air_temp"] - 2.0)
        rx_frame["rainfall_mm"] = raw_telemetry.get("rainfall_mm", 0.0)

        # 4. Central AI Engine Inference
        ai_analysis = self.central_ai.analyze_zone(rx_frame)

        # 5. Recommendation
        recommendation = AgronomicRecommendationEngine.generate_zone_recommendation(ai_analysis)

        return {
            "zone_id": zone_id,
            "raw_sensor_data": raw_telemetry,
            "edge_inference": edge_result,
            "lora_transmission": {
                "raw_bytes": raw_bytes,
                "hex_dump": hex_dump,
                "metadata": tx_meta,
                "gateway_decoded": rx_frame,
            },
            "central_ai_analysis": ai_analysis,
            "recommendation": recommendation,
        }

    def execute_farm_pipeline(self) -> Dict[str, Any]:
        """
        Run end-to-end pipeline across all 6 zones and compute farm aggregate intelligence.
        """
        zone_pipeline_results = []
        zone_ai_analyses = []

        for zone_id in sorted(FARM_ZONES.keys()):
            res = self.execute_zone_pipeline(zone_id)
            zone_pipeline_results.append(res)
            zone_ai_analyses.append(res["central_ai_analysis"])

        # Farm-Level Summary
        farm_summary = self.central_ai.aggregate_farm_summary(zone_ai_analyses)
        farm_recommendations = AgronomicRecommendationEngine.generate_farm_recommendations(zone_ai_analyses)
        farmer_alert = FarmerAlertGenerator.generate_farmer_alert(farm_summary, farm_recommendations)

        return {
            "crop": "Groundnut (Arachis hypogaea)",
            "crop_age_days": self.crop_age_days,
            "zone_results": zone_pipeline_results,
            "farm_summary": farm_summary,
            "farm_recommendations": farm_recommendations,
            "farmer_alert": farmer_alert,
        }
