"""
Seed Sensei - Simulated LoRa Communication Layer
Simulates compact binary packet encoding, transmission over LoRa physical layer,
and gateway packet reception/decoding.
NOTE: This is a software simulation of LoRa packetization; no physical radio hardware is attached.
"""

import struct
from typing import Dict, Any, Tuple
import numpy as np
from src.config import LORA_CONFIG

# Edge status numeric mapping for binary serialization
STATUS_MAP = {
    "NORMAL": 0,
    "WARNING": 1,
    "MOISTURE_STRESS": 2,
    "HEAT_STRESS": 3,
    "COMBINED_STRESS": 4,
    "WATERLOGGING_STRESS": 5,
    "NUTRIENT_DEFICIT": 6,
}
STATUS_REVERSE_MAP = {v: k for k, v in STATUS_MAP.items()}


def compute_crc16(data: bytes) -> int:
    """Standard CRC-16-CCITT for packet integrity verification."""
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


class LoRaTransceiverSimulator:
    """
    Simulates on-node LoRa frame construction and transmission.
    Packets are compressed into a compact 14-byte binary structure.
    """

    def __init__(self, node_id: str, zone_id: int):
        self.node_id = node_id
        self.zone_id = zone_id
        self.seq_num = 0

    def encode_packet(self, edge_inference: Dict[str, Any]) -> Tuple[bytes, str, Dict[str, Any]]:
        """
        Compress sensor readings and edge status into a 14-byte binary frame.
        Structure:
          - Byte 0: Header 'S' (0x53)
          - Byte 1: Node Number (1-6)
          - Byte 2: Zone Number (1-6)
          - Byte 3-4: uint16 Sequence Number
          - Byte 5-6: uint16 Soil Moisture * 100
          - Byte 7-8: int16  Air Temp * 100
          - Byte 9-10: uint16 Humidity * 100
          - Byte 11: uint8  Edge Status Code
          - Byte 12-13: uint16 CRC-16
        """
        self.seq_num = (self.seq_num + 1) & 0xFFFF
        readings = edge_inference["sanitized_readings"]
        
        node_num = int(self.node_id.replace("N", "")) if "N" in self.node_id else self.zone_id
        moist_raw = int(np.clip(readings["soil_moisture"] * 100, 0, 10000))
        temp_raw = int(np.clip(readings["air_temp"] * 100, -2000, 7000))
        hum_raw = int(np.clip(readings["humidity"] * 100, 0, 10000))
        status_code = STATUS_MAP.get(edge_inference["edge_status"], 1)

        payload_without_crc = struct.pack(
            ">BBBHHhHB",
            0x53,          # Header 'S'
            node_num,      # Node ID
            self.zone_id,  # Zone ID
            self.seq_num,  # Seq counter
            moist_raw,     # Moisture x100
            temp_raw,      # Temp x100
            hum_raw,       # Humidity x100
            status_code,   # Edge status
        )

        crc = compute_crc16(payload_without_crc)
        full_packet = payload_without_crc + struct.pack(">H", crc)
        hex_repr = full_packet.hex().upper()

        # Simulated Physical Layer RF Metrics (SX1262 model)
        # SF7, BW 125kHz, CR 4/5 airtime calculation
        symbol_duration_ms = (1 << LORA_CONFIG["spreading_factor"]) / (LORA_CONFIG["bandwidth_khz"] * 1000) * 1000
        n_preamble = LORA_CONFIG["preamble_length"] + 4.25
        n_payload_symbols = 8 + max(0, int(np.ceil((8 * len(full_packet) - 4 * 7 + 28) / (4 * 7)) * 5))
        airtime_ms = round((n_preamble + n_payload_symbols) * symbol_duration_ms, 2)
        
        simulated_rssi = round(float(LORA_CONFIG["nominal_rssi_dbm"] + np.random.normal(0, 2.5)), 1)
        simulated_snr = round(float(LORA_CONFIG["nominal_snr_db"] + np.random.normal(0, 0.8)), 1)

        metadata = {
            "packet_bytes_len": len(full_packet),
            "hex_dump": hex_repr,
            "airtime_ms": airtime_ms,
            "simulated_rssi_dbm": simulated_rssi,
            "simulated_snr_db": simulated_snr,
            "frequency_mhz": LORA_CONFIG["frequency_mhz"],
            "spreading_factor": LORA_CONFIG["spreading_factor"],
            "bandwidth_khz": LORA_CONFIG["bandwidth_khz"],
            "status": "SIMULATED_TRANSMISSION_SUCCESS",
        }

        return full_packet, hex_repr, metadata


class LoRaGatewaySimulator:
    """
    Simulates central field gateway receiving and validating LoRa packets.
    """

    @staticmethod
    def decode_packet(raw_bytes: bytes) -> Dict[str, Any]:
        """
        Unpack 14-byte binary frame and verify CRC integrity.
        """
        if len(raw_bytes) != 14:
            raise ValueError(f"Invalid packet length: {len(raw_bytes)} bytes. Expected 14 bytes.")

        payload = raw_bytes[:12]
        received_crc = struct.unpack(">H", raw_bytes[12:14])[0]
        calc_crc = compute_crc16(payload)

        if received_crc != calc_crc:
            return {"crc_valid": False, "error": "CRC_CHECK_FAILED"}

        header, node_num, zone_id, seq_num, moist_raw, temp_raw, hum_raw, status_code = struct.unpack(
            ">BBBHHhHB", payload
        )

        return {
            "crc_valid": True,
            "header": chr(header),
            "node_id": f"N0{node_num}" if node_num < 10 else f"N{node_num}",
            "zone_id": zone_id,
            "zone_name": f"Zone {zone_id}",
            "seq_num": seq_num,
            "soil_moisture": round(moist_raw / 100.0, 2),
            "air_temp": round(temp_raw / 100.0, 2),
            "humidity": round(hum_raw / 100.0, 2),
            "edge_status": STATUS_REVERSE_MAP.get(status_code, "UNKNOWN"),
        }
