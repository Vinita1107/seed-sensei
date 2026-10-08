# SEED SENSEI: AI-Driven Precision Agriculture System for Oilseed Farming

**Seed Sensei** is a portable, end-to-end software proof-of-concept for precision oilseed agriculture, demonstrated on **groundnut (*Arachis hypogaea*)**. 

The system continuously evaluates multi-zone field telemetry, performs embedded edge filtering and classification (TinyML), transmits compact binary payloads across a simulated long-range radio link (LoRa), and executes central machine learning to predict crop stress, forecast harvest yield, quantify multi-factor agricultural risk, and dispatch plain-language advisories to farmers.

---

## 1. Core Architecture

```
[Simulated IoT Sensors]
       │
       ▼
[TinyML Edge Layer]  ──► Rejects noise, clips outliers, executes compact ML tree (<2 KB RAM)
       │
       ▼
[Simulated LoRa Link] ──► Packs 14-byte compact binary frame, CRC16, computes RF airtime
       │
       ▼
[Central AI Engine]   ──► Random Forest Stress Classifier & Harvest Yield Regressor (kg/ha)
       │
       ├─────────────────────────┐
       ▼                         ▼
[Agronomic Decision Engine]  [Multi-Factor Farm Risk Engine]
       │                         │
       └────────────┬────────────┘
                    ▼
          [Dual-Mode Output]
          ├── Presenter / Technical Mode (Full engineering pipeline)
          └── Farmer Mode (Plain-language actionable advisory)
```

---

## 2. Important Architectural Distinction: Simulated vs. Implemented

This prototype is a software proof-of-concept designed for portability and zero hardware dependencies.

| Component | Physical vs. Simulated | What is Actually Implemented in Software |
| :--- | :--- | :--- |
| **Field & Soil** | **Simulated** | Synthetic data generator modeling groundnut physiology (moisture depletion, thermal stress, pegging sensitivity, soil drainage). |
| **IoT Sensors** | **Simulated** | Synthetic sensor generators producing moisture, soil/air temperature, humidity, rainfall, and nutrient indices across 6 zones. |
| **Edge Hardware** | **Simulated (ESP32-S3 class)** | **Actual Lightweight ML Model**: A real scikit-learn `DecisionTreeClassifier` (depth 4, leaves 8, <3.5 KB) executes inference on-node with actual noise rejection routines. |
| **LoRa Hardware** | **Simulated (SX1262 PHY)** | **Actual Protocol Framing**: Real 14-byte struct binary packing, CRC16-CCITT checksum calculation/verification, and physical airtime calculation based on SF7/125kHz. |
| **Central AI** | **Fully Implemented** | **Actual Trained Machine Learning Models**: Multi-class `RandomForestClassifier` (100 trees) and continuous `RandomForestRegressor` (100 trees), saved to disk and loaded for real inference. |
| **Agronomic Logic**| **Fully Implemented** | Groundnut phenology rules (vegetative, flowering & pegging, pod filling, maturation) driving risk weighting and recommendations. |
| **Farmer Alerts** | **Fully Implemented** | Plain-language advisory generation translating ML probabilities into direct operational directives. |

> **Transparency Note**: Synthetic data is used because no physical farm, ESP32 nodes, or LoRa hardware are present. All reported model metrics are measured on holdout test splits of the synthetic groundnut dataset. No fake field trials or unmeasured accuracies are claimed.

---

## 3. Farm Zoning & Spatial Variation

The prototype divides a groundnut farm into 6 logical spatial management zones:

* **Zone 1 (N01)**: Sandy Loam (1.2 ha) – Baseline optimal conditions.
* **Zone 2 (N02)**: Red Sandy Loam (1.5 ha) – Rapidly draining; target for moisture stress demonstration.
* **Zone 3 (N03)**: Sandy Loam (1.0 ha) – Stable healthy zone.
* **Zone 4 (N04)**: Loamy Sand (1.4 ha) – High drainage; demonstrates sub-optimal moderate deficit.
* **Zone 5 (N05)**: Sandy Loam (1.1 ha) – Stable healthy zone.
* **Zone 6 (N06)**: Red Loam (1.3 ha) – Target for thermal spike / heat wave demonstration.

---

## 4. Quick Start & Setup

### Prerequisites
* Python 3.9 or higher (tested on Python 3.11 / 3.13)
* Windows, Linux, or macOS

### 1. Installation
Clone or navigate to the project directory:
```bash
cd d:\oilseed
```

Install the lightweight dependencies:
```bash
pip install -r requirements.txt
```

### 2. Single-Click Launch (Windows)
Double-click:
```cmd
START.bat
```

### 3. Command Line Launch
Run the interactive console:
```bash
python main.py
```

---

## 5. Demonstration Commands

### Interactive Console
```bash
python main.py
```
Presents a numbered menu to switch between Technical Mode, Farmer Mode, live stress scenarios, manual sensor overrides, and model retraining.

### Technical Mode (Presenter CLI)
Displays the complete engineering pipeline:
```bash
python main.py --mode technical
```

### Farmer Mode (Plain-Language Advisory)
Displays the clean, distraction-free card for growers:
```bash
python main.py --mode farmer
```

### Live Demonstration 1: Progressive Soil Moisture Depletion
Demonstrates Zone 2 drying out over 4 distinct stages (`45.0% -> 34.0% -> 26.0% -> 18.0%`):
```bash
# Step-by-step interactive (press ENTER between steps):
python main.py --simulate-stress

# Non-interactive automated pass:
python main.py --simulate-stress --non-interactive
```

At each step, you will observe:
1. Sensor telemetry updates in Zone 2.
2. TinyML detects the transition: `NORMAL` -> `MOISTURE_STRESS` -> `COMBINED_STRESS`.
3. LoRa binary frame is packed (14 bytes) and transmitted with RF metrics.
4. Central AI stress prediction escalates: `Normal` -> `Moderate Stress` -> `High Stress`.
5. Projected harvest yield drops (e.g., from ~2,900 kg/ha to 700 kg/ha).
6. Risk score rises to 100/100 (`HIGH RISK`).
7. Agronomic recommendation shifts to `CRITICAL: Prioritize immediate drip irrigation`.
8. Farmer alert automatically updates to `URGENT ACTION NEEDED`.

### Live Demonstration 2: Heat Wave Simulation
Demonstrates thermal spike in Zone 6 (`29.0°C -> 33.5°C -> 37.0°C -> 40.5°C`):
```bash
python main.py --simulate-heat
```

### Model Retraining Pipeline
Retrain all ML models on newly synthesized groundnut data and view actual computed evaluation metrics:
```bash
python train_models.py
```

---

## 6. Project Structure

```
SeedSensei/
├── data/
│   └── synthetic_groundnut_data.csv    # 3,600 synthetic agricultural records
├── models/
│   ├── tinyml_edge_model.pkl           # Lightweight DecisionTree for node (<3.5 KB)
│   ├── central_stress_model.pkl        # RandomForestClassifier for central stress
│   └── central_yield_model.pkl         # RandomForestRegressor for harvest yield
├── src/
│   ├── __init__.py
│   ├── config.py                       # Groundnut agronomic thresholds & LoRa config
│   ├── data_generator.py               # Synthetic groundnut dataset generator
│   ├── tinyml_edge.py                  # On-node noise filter & lightweight classifier
│   ├── communication.py                # LoRa binary frame packing & gateway decoding
│   ├── central_ai.py                   # Central AI stress, yield, & farm risk models
│   ├── recommendations.py              # Agronomic decision engine for groundnut
│   ├── alerts.py                       # Farmer-friendly plain-language alert builder
│   ├── farm_simulator.py               # 6-zone state manager & demonstration scenarios
│   └── cli_views.py                    # Technical & Farmer CLI view renderers
├── main.py                             # Main application entry point & CLI parser
├── train_models.py                     # Standalone training & evaluation pipeline
├── requirements.txt                    # Project dependencies
├── START.bat                           # Windows 1-click batch launcher
└── README.md                           # System documentation
```

---

## 7. Machine Learning Pipeline & Measured Performance

All models are genuinely trained and evaluated using standard 80/20 train/test splits.

* **TinyML Edge Model**:
  * Architecture: Scikit-learn `DecisionTreeClassifier` (Depth: 4, Leaves: 8)
  * Serialized Footprint: ~3.2 KB
  * Target Device: ESP32-S3 microcontroller
  * Inputs: `[soil_moisture, air_temp, humidity]`
  * Output: Edge Status (`NORMAL`, `MOISTURE_STRESS`, `HEAT_STRESS`, `COMBINED_STRESS`)

* **Central Stress Classifier**:
  * Architecture: `RandomForestClassifier` (100 estimators, max depth 8)
  * Inputs: `[soil_moisture, soil_temp, air_temp, humidity, rainfall_mm, nutrient_index, crop_age_days]`
  * Classes: `Normal`, `Moderate Stress`, `High Stress`
  * Measured Holdout Test Accuracy: **99.44%**

* **Central Harvest Yield Regressor**:
  * Architecture: `RandomForestRegressor` (100 estimators, max depth 10)
  * Inputs: Multi-zone microclimate and crop age features
  * Target: Dry pod harvest yield in kg/ha (potential range: 700 - 3,400 kg/ha)
  * Measured Holdout Test RMSE: **92.3 kg/ha**
  * Measured Holdout Test R² Score: **0.9927**

---

## 8. Dual Output Modes

### Technical Mode Sample
```
==================================================================================
SEED SENSEI :: AI-DRIVEN OILSEED PRECISION AGRICULTURE SYSTEM
----------------------------------------------------------------------------------
CROP TARGET        : Groundnut (Arachis hypogaea) | Age: 50 Days (Flowering & Pegging)
SYSTEM STATUS      : ACTIVE MONITORING (6 Spatial Logical Zones)
DATA NOTICE        : Software proof-of-concept operating on synthetic farm data
==================================================================================

[1. FIELD SENSOR TELEMETRY (SYNTHETIC)]
ZONE     NODE   SOIL MOIST   SOIL TEMP   AIR TEMP   HUMIDITY   NUTRIENT  
Zone 1   N01      54.0%        25.5°C      27.5°C     68.0%      0.85 (Index)
Zone 2   N02      19.4%        32.0°C      35.6°C     38.0%      0.72 (Index)
...

[2. EDGE INTELLIGENCE (TINYML ON-NODE INFERENCE)]
  * Node N01 (Zone 1): NORMAL             [Confidence: 100.0% | Outlier Check: OK]
  * Node N02 (Zone 2): COMBINED_STRESS    [Confidence: 100.0% | Outlier Check: OK]

[3. COMMUNICATION LAYER (SIMULATED LORA LINK)]
  Frame Origin      : Node N02 -> Gateway (Logical Zone 2)
  Payload Hex Dump  : 0x530202000107930DE80ED804ACC4 (14 bytes binary frame)
  Decoded Payload   : MOISTURE=19.39% | TEMP=35.6°C | HUM=38.0% | EDGE_STATUS=COMBINED_STRESS
  Link Quality      : RSSI: -95.4 dBm | SNR: +8.7 dB | Airtime: 41.22 ms

[4. CENTRAL AI ENGINE (HIGHER-LEVEL INFERENCE)]
ZONE     STRESS CLASS     PROB (HIGH/MOD/NORM)     YIELD EST      RISK SCORE  
Zone 2   High Stress      0.98 / 0.02 / 0.00        700.0 kg/ha   100.0 (HIGH RISK)
...

[5. FARM-LEVEL AI SUMMARY]
  Overall Status            : CRITICAL ACTION REQUIRED
  High Risk Zones           : 2 ['Zone 2', 'Zone 6']
  Farm Mean Projected Yield : 2027.3 kg/ha (Potential Max: 3400.0 kg/ha)
  Overall Farm Risk Score   : 73.3 / 100
```

### Farmer Mode Sample
```
------------------------------------------------------------
SEED SENSEI - FARMER ADVISORY
CROP: GROUNDNUT FIELD
------------------------------------------------------------
FIELD STATUS : URGENT ACTION NEEDED

WHAT IS HAPPENING?
  * Field stress detected in Zone 2, Zone 6.
  * Soil is critically dry during the sensitive flowering/pegging period.
  * Intense heat wave is stressing groundnut flowers.

WHAT SHOULD I DO?
  1. Turn on irrigation for Zone 2 today (apply approx. 30 mm of water).
  2. Protect Zone 6 from extreme heat: run cooling mist or inspect row mulch.
  3. Turn on irrigation for Zone 4 today (apply approx. 18 mm of water).
  4. Other areas (Zone 1, Zone 3, Zone 5) are healthy. No special action needed there today.
------------------------------------------------------------
```
