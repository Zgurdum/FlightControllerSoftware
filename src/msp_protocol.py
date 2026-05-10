"""
MSP (MultiWii Serial Protocol) implementation
Protocol for communicating with Betaflight flight controllers
"""

import struct
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class MSPCommand:
    """MSP Command definitions"""
    # Modern FC information (Betaflight/Cleanflight)
    MSP_API_VERSION = 1
    MSP_FC_VARIANT = 2
    MSP_FC_VERSION = 3
    MSP_BOARD_INFO = 4
    MSP_BUILD_INFO = 5

    # Status and info
    MSP_IDENT = 100
    MSP_STATUS = 101
    MSP_RAW_IMU = 102
    MSP_SERVO = 103
    MSP_MOTOR = 104
    MSP_RC = 105
    MSP_ANALOG = 110
    MSP_RC_TUNING = 111
    MSP_PID = 112
    MSP_SET_MOTOR = 214
    
    # Configuration
    MSP_ACC_CALIBRATION = 205
    MSP_MAG_CALIBRATION = 207
    MSP_EEPROM_WRITE = 250
    
    # Commands for V2
    MSP2_COMMON_SERIAL_CONFIG = 0x1008
    MSP2_SENSOR_COMPASS_DATA = 0x2017


class MSPProtocol:
    """Handle MSP protocol encoding/decoding"""

    @staticmethod
    def decode_api_version(data: bytes) -> Dict[str, Any]:
        """Decode MSP_API_VERSION response."""
        if len(data) < 3:
            return {}

        protocol_version, api_major, api_minor = struct.unpack('<BBB', data[:3])
        return {
            'protocol_version': protocol_version,
            'api_major': api_major,
            'api_minor': api_minor,
            'api_version': f"{api_major}.{api_minor}",
        }

    @staticmethod
    def decode_fc_variant(data: bytes) -> Dict[str, Any]:
        """Decode MSP_FC_VARIANT response."""
        if len(data) < 4:
            return {}

        variant = data[:4].decode('ascii', errors='ignore').strip('\x00 ').upper()
        return {'fc_variant': variant or 'UNKNOWN'}

    @staticmethod
    def decode_fc_version(data: bytes) -> Dict[str, Any]:
        """Decode MSP_FC_VERSION response."""
        if len(data) < 3:
            return {}

        major, minor, patch = struct.unpack('<BBB', data[:3])
        return {
            'fc_version_major': major,
            'fc_version_minor': minor,
            'fc_version_patch': patch,
            'fc_version': f"{major}.{minor}.{patch}",
        }

    @staticmethod
    def decode_board_info(data: bytes) -> Dict[str, Any]:
        """Decode MSP_BOARD_INFO response (best-effort, variable payload by firmware)."""
        if len(data) < 4:
            return {}

        board_id = data[:4].decode('ascii', errors='ignore').strip('\x00 ').upper()
        decoded = {'board_id': board_id or 'UNKNOWN'}

        # Many implementations include board hardware revision in bytes 4..5.
        if len(data) >= 6:
            decoded['board_version'] = struct.unpack('<H', data[4:6])[0]

        return decoded

    @staticmethod
    def decode_build_info(data: bytes) -> Dict[str, Any]:
        """Decode MSP_BUILD_INFO response (ASCII payload)."""
        if not data:
            return {}

        build_info = data.decode('ascii', errors='ignore').replace('\x00', ' ').strip()
        return {'build_info': build_info}
    
    @staticmethod
    def decode_status(data: bytes) -> Dict[str, Any]:
        """Decode MSP_STATUS response"""
        # Betaflight MSP_STATUS is typically 11 bytes in v1 payloads.
        if len(data) < 11:
            return {}

        cycle_time, i2c_errors, sensor_status, config_profile, system_load = struct.unpack('<HHIHB', data[:11])
        
        return {
            'cycle_time': cycle_time,
            'i2c_errors': i2c_errors,
            'sensor_status': {
                'gyro': (sensor_status & 0x01) != 0,
                'acc': (sensor_status & 0x02) != 0,
                'mag': (sensor_status & 0x04) != 0,
                'baro': (sensor_status & 0x08) != 0,
                'gps': (sensor_status & 0x10) != 0,
            },
            'config_profile': config_profile,
            'system_load': system_load,
        }
    
    @staticmethod
    def decode_raw_imu(data: bytes) -> Dict[str, Any]:
        """Decode MSP_RAW_IMU response (gyro, accel, mag)"""
        if len(data) < 18:
            return {}
        
        gyro_x, gyro_y, gyro_z, acc_x, acc_y, acc_z, mag_x, mag_y, mag_z = struct.unpack('<hhhhhhhhh', data[:18])
        
        return {
            'gyro': {
                'x': gyro_x / 4.096,  # LSB per deg/s
                'y': gyro_y / 4.096,
                'z': gyro_z / 4.096,
            },
            'accelerometer': {
                'x': acc_x / 512.0,  # LSB per g
                'y': acc_y / 512.0,
                'z': acc_z / 512.0,
            },
            'magnetometer': {
                'x': mag_x,
                'y': mag_y,
                'z': mag_z,
            }
        }
    
    @staticmethod
    def decode_motor(data: bytes) -> Dict[str, list]:
        """Decode MSP_MOTOR response (motor speeds)"""
        if len(data) < 8:
            return {}
        
        motors = struct.unpack('<HHHH', data[:8])
        return {'motors': list(motors)}
    
    @staticmethod
    def decode_rc(data: bytes) -> Dict[str, list]:
        """Decode MSP_RC response (RC channels)"""
        if len(data) % 2 != 0:
            return {}
        
        num_channels = len(data) // 2
        channels = struct.unpack(f'<{num_channels}H', data)
        return {'channels': list(channels)}
    
    @staticmethod
    def decode_analog(data: bytes) -> Dict[str, Any]:
        """Decode MSP_ANALOG response"""
        # Common Betaflight payload is 7 bytes: vbat,u16 mAh,u16 rssi,u16 amperage.
        if len(data) < 7:
            return {}

        vbat, mah, rssi, amperage_raw = struct.unpack('<BHHH', data[:7])

        # Optional extra field on some variants.
        last_mah = None
        if len(data) >= 9:
            last_mah = struct.unpack('<H', data[7:9])[0]
        
        return {
            'vbat': vbat / 10.0,  # Voltage in volts
            'mah': mah,
            'rssi': rssi,
            'amperage': amperage_raw / 100.0,  # Current in amps
            'last_mah': last_mah,
        }
    
    @staticmethod
    def decode_ident(data: bytes) -> Dict[str, Any]:
        """Decode MSP_IDENT response"""
        if len(data) < 7:
            return {}
        
        version, multitype, msp_version, capability = struct.unpack('<BBBBI', data[:7])
        
        msp_types = {
            1: 'TRI',
            2: 'QUADX',
            3: 'QUAD+',
            4: 'QUAD H',
            5: 'Y4',
            6: 'HEX6',
            7: 'FLYING_WING',
            8: 'Y6',
            9: 'HEX6H',
            10: 'OCTOX8',
            11: 'OCTOFLATP',
            12: 'OCTOFLATH',
            13: 'AIRPLANE',
            14: 'HELI_120_CCPM',
            15: 'HELI_90_CCPM',
            16: 'VTAIL4',
            17: 'HEX6X',
            18: 'PPM_TO_SERVO',
            19: 'TRICOPTER',
            20: 'GIMBAL',
            21: 'DUALCOPTER',
            22: 'SINGLECOPTER',
            23: 'QUADX1200',
            24: 'HELI_GGT',
            25: 'OCTOX4_CINELIFTER',
            26: 'QUADX_CW_X',
            27: 'QUADX_CW_V',
            28: 'QUADX_CW_A',
            29: 'QUADX_CW_B'
        }
        
        return {
            'version': version,
            'type': msp_types.get(multitype, f'Unknown({multitype})'),
            'msp_version': msp_version,
            'capability': capability,
        }
    
    @staticmethod
    def encode_pid(profile: int, pids: list) -> bytes:
        """Encode PID tuning values"""
        data = bytes([profile])
        for p, i, d in pids[:10]:  # Max 10 PID sets
            data += struct.pack('<BBB', int(p), int(i), int(d))
        return data
