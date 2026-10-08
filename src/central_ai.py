"""
Seed Sensei - Central AI Engine
The primary intelligence core of Seed Sensei.
Executes:
1. Crop Stress Classification with probability distributions (RandomForestClassifier)
2. Groundnut Harvest Yield Prediction in kg/ha (RandomForestRegressor)
3. Zone-level and Farm-wide Multi-Factor Risk Assessment
"""

from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error, r2_score

from src.config import (
    CENTRAL_STRESS_MODEL_PATH,
    CENTRAL_YIELD_MODEL_PATH,
    STRESS_CLASSES,
    FARM_ZONES,
    POTENTIAL_MAX_YIELD_KG_HA,
)


FEATURE_COLUMNS = [
    "soil_moisture",
    "soil_temp",
    "air_temp",
    "humidity",
    "rainfall_mm",
    "nutrient_index",
    "crop_age_days",
]


class CentralAIEngine:
    """
    Central AI Intelligence Engine responsible for farm-wide analytics.
    Evaluates stress states, projects harvest yields, and computes risk indices.
    """

    def __init__(self):
        self.stress_model = None
        self.yield_model = None
        self._load_or_train_models()

    def _load_or_train_models(self):
        """Loads pre-trained models from disk; if absent, initial default models are prepared."""
        if CENTRAL_STRESS_MODEL_PATH.exists() and CENTRAL_YIELD_MODEL_PATH.exists():
            try:
                self.stress_model = joblib.load(CENTRAL_STRESS_MODEL_PATH)
                self.yield_model = joblib.load(CENTRAL_YIELD_MODEL_PATH)
                return
            except Exception:
                pass
        
        # If models do not exist yet, import generator and train automatically
        from src.data_generator import ensure_dataset_exists
        df = ensure_dataset_exists()
        train_central_models(df)
        self.stress_model = joblib.load(CENTRAL_STRESS_MODEL_PATH)
        self.yield_model = joblib.load(CENTRAL_YIELD_MODEL_PATH)

    def analyze_zone(self, zone_telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run multi-model AI analysis on a single zone's telemetry frame.
        """
        # Prepare feature vector
        soil_moist = float(zone_telemetry.get("soil_moisture", 50.0))
        air_temp = float(zone_telemetry.get("air_temp", 28.0))
        soil_temp = float(zone_telemetry.get("soil_temp", air_temp - 2.0))
        humidity = float(zone_telemetry.get("humidity", 60.0))
        rainfall = float(zone_telemetry.get("rainfall_mm", 0.0))
        nutrient = float(zone_telemetry.get("nutrient_index", 0.75))
        crop_age = int(zone_telemetry.get("crop_age_days", 50))
        zone_id = int(zone_telemetry.get("zone_id", 1))

        X = pd.DataFrame([{
            "soil_moisture": soil_moist,
            "soil_temp": soil_temp,
            "air_temp": air_temp,
            "humidity": humidity,
            "rainfall_mm": rainfall,
            "nutrient_index": nutrient,
            "crop_age_days": crop_age,
        }])[FEATURE_COLUMNS]

        # 1. Stress Prediction
        stress_class = self.stress_model.predict(X)[0]
        stress_probs_raw = self.stress_model.predict_proba(X)[0]
        classes = list(self.stress_model.classes_)
        
        prob_dict = {cls_name: round(float(stress_probs_raw[classes.index(cls_name)]), 3) 
                     for cls_name in STRESS_CLASSES if cls_name in classes}
        
        p_high = prob_dict.get("High Stress", 0.0)
        p_mod = prob_dict.get("Moderate Stress", 0.0)
        p_norm = prob_dict.get("Normal", 1.0)

        # 2. Yield Prediction (kg/ha)
        predicted_yield = float(self.yield_model.predict(X)[0])
        predicted_yield = round(np.clip(predicted_yield, 600.0, POTENTIAL_MAX_YIELD_KG_HA), 1)
        yield_loss_pct = round(max(0.0, (1.0 - (predicted_yield / POTENTIAL_MAX_YIELD_KG_HA)) * 100.0), 1)

        # 3. Zone Risk Calculation (0 - 100)
        # Agronomic weighting:
        # Flowering & Pegging stage (days 36-65) has heightened susceptibility
        stage_factor = 1.35 if (36 <= crop_age <= 65) else 1.0
        
        # Base probability risk
        base_prob_risk = (p_high * 70.0) + (p_mod * 35.0)
        
        # Physiological penalty for moisture deficit
        moisture_penalty = 0.0
        if soil_moist < 26.0:
            moisture_penalty = (26.0 - soil_moist) * 1.8
        elif soil_moist < 36.0:
            moisture_penalty = (36.0 - soil_moist) * 0.8

        # Thermal penalty
        heat_penalty = 0.0
        if air_temp > 35.0:
            heat_penalty = (air_temp - 35.0) * 2.2

        raw_risk = (base_prob_risk * stage_factor) + moisture_penalty + heat_penalty
        zone_risk_score = round(float(np.clip(raw_risk, 0.0, 100.0)), 1)

        if zone_risk_score >= 68.0:
            risk_category = "HIGH RISK"
        elif zone_risk_score >= 38.0:
            risk_category = "MODERATE RISK"
        else:
            risk_category = "LOW RISK"

        return {
            "zone_id": zone_id,
            "zone_name": FARM_ZONES.get(zone_id, {}).get("name", f"Zone {zone_id}"),
            "predicted_stress_class": stress_class,
            "stress_probabilities": prob_dict,
            "predicted_yield_kg_ha": predicted_yield,
            "yield_loss_pct": yield_loss_pct,
            "risk_score": zone_risk_score,
            "risk_category": risk_category,
            "crop_age_days": crop_age,
            "telemetry_used": {
                "soil_moisture": soil_moist,
                "air_temp": air_temp,
                "soil_temp": soil_temp,
                "humidity": humidity,
                "rainfall_mm": rainfall,
                "nutrient_index": nutrient,
            }
        }

    def aggregate_farm_summary(self, zone_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate all zone evaluations into a comprehensive farm-level intelligence summary.
        """
        if not zone_analyses:
            return {}

        total_zones = len(zone_analyses)
        high_risk_zones = [z for z in zone_analyses if z["risk_category"] == "HIGH RISK"]
        mod_risk_zones = [z for z in zone_analyses if z["risk_category"] == "MODERATE RISK"]
        low_risk_zones = [z for z in zone_analyses if z["risk_category"] == "LOW RISK"]

        avg_yield = round(float(np.mean([z["predicted_yield_kg_ha"] for z in zone_analyses])), 1)
        mean_risk = float(np.mean([z["risk_score"] for z in zone_analyses]))
        max_risk = float(np.max([z["risk_score"] for z in zone_analyses]))

        # Farm risk is weighted between mean and worst-case zone
        overall_risk_score = round(0.45 * mean_risk + 0.55 * max_risk, 1)

        # Farm status categorization
        if len(high_risk_zones) >= 2 or overall_risk_score >= 65.0:
            overall_status = "CRITICAL ACTION REQUIRED"
        elif len(high_risk_zones) == 1 or len(mod_risk_zones) >= 2 or overall_risk_score >= 40.0:
            overall_status = "ATTENTION REQUIRED"
        elif len(mod_risk_zones) == 1:
            overall_status = "MODERATE WATCH"
        else:
            overall_status = "NORMAL / HEALTHY"

        return {
            "overall_status": overall_status,
            "total_zones": total_zones,
            "high_risk_count": len(high_risk_zones),
            "moderate_risk_count": len(mod_risk_zones),
            "normal_risk_count": len(low_risk_zones),
            "high_risk_zone_names": [z["zone_name"] for z in high_risk_zones],
            "moderate_risk_zone_names": [z["zone_name"] for z in mod_risk_zones],
            "average_predicted_yield_kg_ha": avg_yield,
            "overall_farm_risk_score": overall_risk_score,
            "zone_details": zone_analyses,
        }


def train_central_models(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Train genuine Random Forest models for Stress Classification and Harvest Yield Regression.
    Evaluates on test split and reports actual metrics.
    """
    CENTRAL_STRESS_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    X = df[FEATURE_COLUMNS]
    y_stress = df["stress_label"]
    y_yield = df["yield_kg_per_ha"]

    # Split
    X_train, X_test, y_s_train, y_s_test, y_y_train, y_y_test = train_test_split(
        X, y_stress, y_yield, test_size=0.20, random_state=42, stratify=y_stress
    )

    # 1. Stress Classifier
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=5,
        random_state=42
    )
    clf.fit(X_train, y_s_train)
    y_s_pred = clf.predict(X_test)
    stress_rep = classification_report(y_s_test, y_s_pred, output_dict=True)

    # 2. Yield Regressor
    reg = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=4,
        random_state=42
    )
    reg.fit(X_train, y_y_train)
    y_y_pred = reg.predict(X_test)
    mse = mean_squared_error(y_y_test, y_y_pred)
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_y_test, y_y_pred))

    joblib.dump(clf, CENTRAL_STRESS_MODEL_PATH)
    joblib.dump(reg, CENTRAL_YIELD_MODEL_PATH)

    return {
        "stress_accuracy": round(stress_rep["accuracy"], 4),
        "yield_rmse": round(rmse, 2),
        "yield_r2": round(r2, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }
