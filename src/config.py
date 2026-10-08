"""
Seed Sensei - Configuration & Agronomic Constants
Target Crop: Groundnut (Arachis hypogaea)
"""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
SYNTHETIC_DATA_PATH = DATA_DIR / "synthetic_groundnut_data.csv"

TINYML_MODEL_PATH = MODELS_DIR / "tinyml_edge_model.pkl"
CENTRAL_STRESS_MODEL_PATH = MODELS_DIR / "central_stress_model.pkl"
CENTRAL_YIELD_MODEL_PATH = MODELS_DIR / "central_yield_model.pkl"

# Crop Agronomy: Groundnut
CROP_NAME = "Groundnut (Arachis hypogaea)"
CROP_TYPE = "Oilseed / Legume"
DEFAULT_CROP_AGE_DAYS = 50  # Flowering / Pegging Stage

# Logical Zones
FARM_ZONES = {
    1: {"node_id": "N01", "name": "Zone 1", "soil_type": "Sandy Loam", "area_ha": 1.2},
    2: {"node_id": "N02", "name": "Zone 2", "soil_type": "Red Sandy Loam", "area_ha": 1.5},
    3: {"node_id": "N03", "name": "Zone 3", "soil_type": "Sandy Loam", "area_ha": 1.0},
    4: {"node_id": "N04", "name": "Zone 4", "soil_type": "Loamy Sand", "area_ha": 1.4},
    5: {"node_id": "N05", "name": "Zone 5", "soil_type": "Sandy Loam", "area_ha": 1.1},
    6: {"node_id": "N06", "name": "Zone 6", "soil_type": "Red Loam", "area_ha": 1.3},
}

# Agronomic Baseline Thresholds for Groundnut
THRESHOLDS = {
    "moisture_severe_dry": 26.0,    # % soil moisture
    "moisture_moderate_dry": 36.0,  # % soil moisture
    "moisture_optimal_min": 45.0,   # % soil moisture
    "moisture_optimal_max": 68.0,   # % soil moisture
    "moisture_waterlogged": 82.0,   # % soil moisture
    
    "air_temp_optimal_min": 24.0,   # °C
    "air_temp_optimal_max": 31.0,   # °C
    "air_temp_moderate_heat": 34.0, # °C
    "air_temp_severe_heat": 38.0,   # °C
    
    "humidity_optimal_min": 50.0,   # %
    "humidity_optimal_max": 75.0,   # %
    
    "nutrient_optimal_min": 0.70,   # Normalized index (0.0 - 1.0)
    "nutrient_moderate_min": 0.45,  # Normalized index
}

# Growth Stages & Water Sensitivity Multipliers
GROWTH_STAGES = [
    {"name": "Vegetative", "min_age": 0, "max_age": 35, "stress_multiplier": 1.0},
    {"name": "Flowering & Pegging", "min_age": 36, "max_age": 65, "stress_multiplier": 1.5},
    {"name": "Pod Development", "min_age": 66, "max_age": 90, "stress_multiplier": 1.3},
    {"name": "Maturation & Ripening", "min_age": 91, "max_age": 120, "stress_multiplier": 0.8},
]

# Benchmark Yield (kg/ha)
POTENTIAL_MAX_YIELD_KG_HA = 3400.0
TYPICAL_AVERAGE_YIELD_KG_HA = 2300.0
MIN_SURVIVAL_YIELD_KG_HA = 700.0

# LoRa Simulation Parameters
LORA_CONFIG = {
    "frequency_mhz": 865.5,     # Indian ISM band (IN865) / EU868 compatible
    "bandwidth_khz": 125,
    "spreading_factor": 7,
    "coding_rate": "4/5",
    "preamble_length": 8,
    "nominal_rssi_dbm": -92.0,
    "nominal_snr_db": 8.5,
}

# Edge ML Classification Classes
EDGE_CLASSES = ["NORMAL", "WARNING", "MOISTURE_STRESS", "HEAT_STRESS", "COMBINED_STRESS"]

# Central AI Stress Classes
STRESS_CLASSES = ["Normal", "Moderate Stress", "High Stress"]
