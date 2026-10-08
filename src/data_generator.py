"""
Seed Sensei - Synthetic Agricultural Data Generator for Groundnut
Generates realistic multi-zone agronomic time-series and tabular data with
authentic physiological relationships for groundnut (Arachis hypogaea).
"""

import numpy as np
import pandas as pd
from pathlib import Path
from src.config import (
    SYNTHETIC_DATA_PATH,
    FARM_ZONES,
    POTENTIAL_MAX_YIELD_KG_HA,
    MIN_SURVIVAL_YIELD_KG_HA,
)


def generate_groundnut_dataset(n_samples: int = 3600, random_seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic groundnut farm dataset with coherent agronomic relationships.
    Simulates diverse conditions across 6 farm zones over multiple crop stages.
    """
    np.random.seed(random_seed)
    
    records = []
    
    # Define weather regime distributions to create realistic climate patterns
    regimes = ["normal_monsoon", "dry_spell", "heat_wave", "optimal_irrigated", "erratic_rain"]
    regime_probs = [0.35, 0.25, 0.15, 0.20, 0.05]
    
    for i in range(n_samples):
        zone_id = int(np.random.choice(list(FARM_ZONES.keys())))
        regime = np.random.choice(regimes, p=regime_probs)
        
        # Crop age across growing cycle (15 to 110 days)
        crop_age = int(np.random.randint(15, 111))
        
        # Environmental base values depending on regime
        if regime == "normal_monsoon":
            air_temp = np.random.normal(28.0, 2.5)
            humidity = np.random.normal(68.0, 6.0)
            rainfall = np.random.choice([0.0, 0.0, 4.0, 12.0, 22.0], p=[0.5, 0.2, 0.15, 0.1, 0.05])
            base_moisture = 52.0 + (rainfall * 0.4)
            nutrient_index = np.random.normal(0.78, 0.08)
            
        elif regime == "dry_spell":
            air_temp = np.random.normal(33.5, 2.0)
            humidity = np.random.normal(42.0, 7.0)
            rainfall = 0.0
            base_moisture = np.random.normal(25.0, 5.0)
            nutrient_index = np.random.normal(0.68, 0.10)
            
        elif regime == "heat_wave":
            air_temp = np.random.normal(38.0, 1.8)
            humidity = np.random.normal(35.0, 5.0)
            rainfall = 0.0
            base_moisture = np.random.normal(22.0, 4.5)
            nutrient_index = np.random.normal(0.65, 0.12)
            
        elif regime == "optimal_irrigated":
            air_temp = np.random.normal(27.0, 2.0)
            humidity = np.random.normal(62.0, 5.0)
            rainfall = np.random.choice([0.0, 2.0, 6.0], p=[0.7, 0.2, 0.1])
            base_moisture = np.random.normal(55.0, 4.0)
            nutrient_index = np.random.normal(0.85, 0.06)
            
        else:  # erratic_rain / waterlogging
            air_temp = np.random.normal(26.0, 2.5)
            humidity = np.random.normal(82.0, 5.0)
            rainfall = np.random.normal(45.0, 12.0)
            base_moisture = np.random.normal(83.0, 4.0)
            nutrient_index = np.random.normal(0.60, 0.10)

        # Soil type drainage adjustments based on zone
        soil_type = FARM_ZONES[zone_id]["soil_type"]
        if "Loamy Sand" in soil_type:
            soil_moisture = base_moisture * 0.88
        elif "Red Loam" in soil_type:
            soil_moisture = base_moisture * 1.05
        else:
            soil_moisture = base_moisture
            
        # Add realistic sensor jitter
        soil_moisture = float(np.clip(soil_moisture + np.random.normal(0, 1.2), 10.0, 95.0))
        air_temp = float(np.clip(air_temp + np.random.normal(0, 0.8), 16.0, 44.0))
        humidity = float(np.clip(humidity + np.random.normal(0, 2.0), 18.0, 98.0))
        rainfall = float(np.clip(rainfall, 0.0, 120.0))
        nutrient_index = float(np.clip(nutrient_index, 0.20, 0.98))
        
        # Soil temperature tracks air temperature buffered by soil moisture
        # High moisture = higher thermal inertia = cooler soil during hot days
        soil_temp = float(np.clip(air_temp * 0.82 + (60.0 - soil_moisture) * 0.15 + np.random.normal(0, 0.9), 18.0, 40.0))
        
        # Derived Agronomic Relationships
        # 1. Growth Stage Sensitivity Multiplier
        # Flowering & Pegging (36-65 days) is the most drought-sensitive stage for groundnut
        if 36 <= crop_age <= 65:
            stage_name = "Flowering & Pegging"
            stage_multiplier = 1.5
        elif 66 <= crop_age <= 90:
            stage_name = "Pod Development"
            stage_multiplier = 1.3
        elif crop_age > 90:
            stage_name = "Maturation"
            stage_multiplier = 0.85
        else:
            stage_name = "Vegetative"
            stage_multiplier = 1.0

        # 2. Moisture Stress Factor (0.0 = total deficit/saturation, 1.0 = optimal)
        if 42.0 <= soil_moisture <= 68.0:
            moisture_factor = 1.0
        elif 32.0 <= soil_moisture < 42.0:
            moisture_factor = 0.78 - (42.0 - soil_moisture) * 0.025
        elif soil_moisture < 32.0:
            moisture_factor = max(0.20, 0.55 - (32.0 - soil_moisture) * 0.022)
        elif 68.0 < soil_moisture <= 80.0:
            moisture_factor = 0.88
        else:  # waterlogging > 80%
            moisture_factor = max(0.35, 0.88 - (soil_moisture - 80.0) * 0.035)

        # 3. Thermal Stress Factor
        if 23.0 <= air_temp <= 31.0:
            temp_factor = 1.0
        elif 31.0 < air_temp <= 35.0:
            temp_factor = 0.85 - (air_temp - 31.0) * 0.04
        elif air_temp > 35.0:
            temp_factor = max(0.30, 0.69 - (air_temp - 35.0) * 0.065)
        else:  # cool temperatures
            temp_factor = max(0.40, 1.0 - (23.0 - air_temp) * 0.07)

        # 4. Stress Classification
        # Groundnut agronomic thresholds:
        # Optimal: 42% - 68% moisture, 24°C - 31°C temp
        # Moderate deficit: 26% - 40% moisture, or 32°C - 35°C temp
        # Severe deficit / heat: < 26% moisture, or > 35°C temp
        is_severe_dry = soil_moisture < 26.0
        is_mod_dry = 26.0 <= soil_moisture < 38.0
        is_severe_heat = air_temp > 35.5
        is_mod_heat = 32.5 <= air_temp <= 35.5
        is_waterlogged = soil_moisture > 80.0
        is_nutrient_poor = nutrient_index < 0.45

        if is_severe_dry and is_severe_heat:
            stress_label = "High Stress"
            stress_type = "COMBINED_STRESS"
        elif is_severe_dry:
            stress_label = "High Stress"
            stress_type = "MOISTURE_STRESS"
        elif is_severe_heat:
            stress_label = "High Stress"
            stress_type = "HEAT_STRESS"
        elif is_mod_dry or is_mod_heat or is_waterlogged or is_nutrient_poor:
            stress_label = "Moderate Stress"
            if is_waterlogged:
                stress_type = "WATERLOGGING_STRESS"
            elif is_mod_dry:
                stress_type = "MOISTURE_STRESS"
            elif is_mod_heat:
                stress_type = "HEAT_STRESS"
            else:
                stress_type = "NUTRIENT_DEFICIT"
        else:
            stress_label = "Normal"
            stress_type = "NORMAL"

        # 5. Realistic Groundnut Yield Target (kg/ha)
        # Combines physiological factors with stage vulnerability
        stress_damage = (1.0 - (moisture_factor * temp_factor)) * stage_multiplier
        effective_health = max(0.18, 1.0 - min(0.85, stress_damage))
        
        # Nutrients modulate yield potential
        nutrient_mult = 0.50 + (0.50 * nutrient_index)
        
        base_yield = POTENTIAL_MAX_YIELD_KG_HA * effective_health * nutrient_mult
        
        # Add realistic biological variability (+/- 4%)
        actual_yield = base_yield + np.random.normal(0, 50.0)
        actual_yield = float(np.clip(actual_yield, MIN_SURVIVAL_YIELD_KG_HA, POTENTIAL_MAX_YIELD_KG_HA))

        records.append({
            "zone_id": zone_id,
            "crop_age_days": crop_age,
            "growth_stage": stage_name,
            "soil_moisture": round(soil_moisture, 2),
            "soil_temp": round(soil_temp, 2),
            "air_temp": round(air_temp, 2),
            "humidity": round(humidity, 2),
            "rainfall_mm": round(rainfall, 2),
            "nutrient_index": round(nutrient_index, 3),
            "stress_type": stress_type,
            "stress_label": stress_label,
            "yield_kg_per_ha": round(actual_yield, 1),
        })

    df = pd.DataFrame(records)
    return df


def ensure_dataset_exists(n_samples: int = 3600, force_regenerate: bool = False) -> pd.DataFrame:
    """Check if synthetic data exists; if not, generate and save it."""
    SYNTHETIC_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    if SYNTHETIC_DATA_PATH.exists() and not force_regenerate:
        df = pd.read_csv(SYNTHETIC_DATA_PATH)
        return df
    
    df = generate_groundnut_dataset(n_samples=n_samples)
    df.to_csv(SYNTHETIC_DATA_PATH, index=False)
    return df


if __name__ == "__main__":
    df = ensure_dataset_exists(force_regenerate=True)
    print(f"Generated synthetic groundnut dataset with {len(df)} samples.")
    print("Stress distribution:\n", df["stress_label"].value_counts())
    print("\nSample records:")
    print(df.head())
