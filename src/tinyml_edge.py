"""
Seed Sensei - TinyML Edge Layer Module
Simulates an on-node embedded ML processor (ESP32-class microcontroller)
performing sensor noise filtering, physical validation, and lightweight edge classification.
"""

from typing import Dict, Any, Tuple
import joblib
import numpy as np
from pathlib import Path
from sklearn.tree import DecisionTreeClassifier
from src.config import TINYML_MODEL_PATH, EDGE_CLASSES


class TinyMLEdgeNode:
    """
    Simulates a lightweight TinyML firmware stack running on an ESP32 field node.
    Performs data sanitization and executes a shallow, low-footprint classification tree.
    """

    def __init__(self, node_id: str, zone_id: int):
        self.node_id = node_id
        self.zone_id = zone_id
        self.model = None
        self._load_or_init_model()

    def _load_or_init_model(self):
        """Load trained edge tree if available, otherwise initialize fallback."""
        if TINYML_MODEL_PATH.exists():
            try:
                self.model = joblib.load(TINYML_MODEL_PATH)
            except Exception:
                self.model = None
        
        if self.model is None:
            # Fallback lightweight pre-trained estimator for instant standup
            self.model = self._create_default_lightweight_model()

    @staticmethod
    def _create_default_lightweight_model() -> DecisionTreeClassifier:
        """
        Creates a compact decision tree mimicking an embedded TinyML model.
        Memory footprint: < 2 KB, Depth: 3.
        """
        clf = DecisionTreeClassifier(max_depth=3, random_state=42)
        # Synthetic initialization anchor
        X_dummy = np.array([
            [55.0, 26.0, 65.0],   # Normal
            [35.0, 31.0, 50.0],   # Warning
            [22.0, 31.0, 40.0],   # Moisture stress
            [48.0, 38.0, 35.0],   # Heat stress
            [20.0, 38.0, 30.0],   # Combined stress
        ])
        y_dummy = np.array([
            "NORMAL",
            "WARNING",
            "MOISTURE_STRESS",
            "HEAT_STRESS",
            "COMBINED_STRESS",
        ])
        clf.fit(X_dummy, y_dummy)
        return clf

    def filter_sensor_noise(self, raw_data: Dict[str, float]) -> Tuple[Dict[str, float], bool]:
        """
        Embedded Sanity / Outlier Rejection Filter:
        Rejects physical impossibilities and clips electrical glitches.
        Returns: (sanitized_data, noise_detected_flag)
        """
        noise_detected = False
        sanitized = {}

        # Soil Moisture (%): physically bounded [0.0, 100.0]
        raw_moist = float(raw_data.get("soil_moisture", 50.0))
        if raw_moist < 0.0 or raw_moist > 100.0:
            noise_detected = True
        sanitized["soil_moisture"] = float(np.clip(raw_moist, 0.0, 100.0))

        # Air Temp (°C): reasonable ambient boundary [-10.0, 65.0]
        raw_temp = float(raw_data.get("air_temp", 28.0))
        if raw_temp < -10.0 or raw_temp > 65.0:
            noise_detected = True
        sanitized["air_temp"] = float(np.clip(raw_temp, -10.0, 65.0))

        # Humidity (%): bounded [0.0, 100.0]
        raw_hum = float(raw_data.get("humidity", 60.0))
        if raw_hum < 0.0 or raw_hum > 100.0:
            noise_detected = True
        sanitized["humidity"] = float(np.clip(raw_hum, 0.0, 100.0))

        # Soil Temp
        sanitized["soil_temp"] = float(np.clip(raw_data.get("soil_temp", raw_temp - 2.0), 0.0, 55.0))

        # Crop Age & Nutrients passed through
        sanitized["crop_age_days"] = int(raw_data.get("crop_age_days", 50))
        sanitized["nutrient_index"] = float(raw_data.get("nutrient_index", 0.75))

        return sanitized, noise_detected

    def run_inference(self, sensor_readings: Dict[str, float]) -> Dict[str, Any]:
        """
        Execute on-device TinyML inference:
        1. Sanitize raw readings
        2. Execute lightweight classification model
        3. Emit edge status and telemetry
        """
        clean_readings, noise_flag = self.filter_sensor_noise(sensor_readings)

        # Feature vector for TinyML: [soil_moisture, air_temp, humidity]
        features = np.array([[
            clean_readings["soil_moisture"],
            clean_readings["air_temp"],
            clean_readings["humidity"]
        ]])

        if hasattr(self.model, "predict"):
            pred_class = self.model.predict(features)[0]
            # Get class probabilities if supported
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(features)[0]
                confidence = float(np.max(probs))
            else:
                confidence = 0.90
        else:
            # Deterministic agronomic edge fallback
            m = clean_readings["soil_moisture"]
            t = clean_readings["air_temp"]
            if m < 26.0 and t > 34.0:
                pred_class = "COMBINED_STRESS"
            elif m < 28.0:
                pred_class = "MOISTURE_STRESS"
            elif t > 36.0:
                pred_class = "HEAT_STRESS"
            elif m < 38.0 or t > 33.0:
                pred_class = "WARNING"
            else:
                pred_class = "NORMAL"
            confidence = 0.85

        return {
            "node_id": self.node_id,
            "zone_id": self.zone_id,
            "edge_status": str(pred_class),
            "edge_confidence": round(confidence, 3),
            "sanitized_readings": clean_readings,
            "noise_filtered": noise_flag,
            "mcu_specs": {
                "target_device": "ESP32-S3 (240MHz Xtensa LX7)",
                "est_ram_bytes": 1420,
                "est_latency_ms": 1.4,
            }
        }


def train_tinyml_model(df_synthetic, output_path: Path = TINYML_MODEL_PATH) -> DecisionTreeClassifier:
    """
    Train a shallow decision tree classifier for edge deployment.
    Keeps depth small to represent TinyML memory constraints (< 2KB).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Map stress labels into edge classes
    X = df_synthetic[["soil_moisture", "air_temp", "humidity"]].values
    y = df_synthetic["stress_type"].values
    
    edge_tree = DecisionTreeClassifier(
        max_depth=4,
        min_samples_leaf=20,
        random_state=42
    )
    edge_tree.fit(X, y)
    
    joblib.dump(edge_tree, output_path)
    return edge_tree
