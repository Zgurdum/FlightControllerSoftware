"""
Flight Controller interface
High-level abstraction for communicating with F722 flight controller
"""

import time
import logging
import struct
from typing import Callable, Dict, Any, Optional

try:
    # Package imports (works with: from src.flight_controller import ...)
    from .serial_handler import SerialHandler
    from .msp_protocol import MSPCommand, MSPProtocol
except ImportError:
    # Script imports (works with: python src/gui_main.py)
    from serial_handler import SerialHandler
    from msp_protocol import MSPCommand, MSPProtocol

logger = logging.getLogger(__name__)


class FlightControllerInterface:
    """Interface for F722 flight controller"""
    
    def __init__(self):
        self.serial = SerialHandler()
        self.connected = False
        self.device_info = {}
        self.sensor_data = {}
        self.status_data = {}
        self.motor_speeds = []
        self.rc_channels = []
        self.callbacks = {}
        
        # Register serial RX callback
        self.serial.set_rx_callback(self._handle_message)

    @staticmethod
    def _port_score(port_info: Dict[str, str]) -> int:
        """Score ports so likely FC USB ports are selected first."""
        port_name = (port_info.get('port') or '').upper()
        description = (port_info.get('description') or '').upper()
        hwid = (port_info.get('hwid') or '').upper()
        text = f"{description} {hwid}"

        score = 0

        # Prefer common USB FC adapters/chipsets.
        preferred_markers = [
            'USB', 'STM', 'STLINK', 'DFU', 'CP210', 'CH340', 'CH341', 'FTDI', 'VIRTUAL COM'
        ]
        if any(marker in text for marker in preferred_markers):
            score += 100

        # Penalize motherboard legacy COM ports.
        if 'COMMUNICATIONS PORT' in description:
            score -= 100

        # COM1 is often legacy and usually not the FC.
        if port_name == 'COM1':
            score -= 50

        return score

    def _select_best_port(self, ports):
        """Choose the most likely flight-controller port."""
        return max(ports, key=self._port_score)
    
    def connect(self, port: str = None) -> bool:
        """Connect to flight controller"""
        if port is None:
            # Auto-detect port
            ports = self.serial.list_ports()
            if not ports:
                logger.error("No serial ports found")
                return False
            best_port = self._select_best_port(ports)
            port = best_port['port']
            logger.info(f"Auto-detected port: {port}")
        
        if not self.serial.connect(port):
            return False
        
        # Wait for device to initialize
        time.sleep(0.5)
        
        # Request device identification using both legacy and modern MSP commands.
        # Some FCs respond after a short delay, so retry briefly.
        for _ in range(3):
            self.request_device_info()
            time.sleep(0.2)
            if self.device_info.get('fc_variant') or self.device_info.get('board_id'):
                break
        
        if not self.device_info:
            logger.warning("Could not get device info, but connection established")
        
        self.connected = True
        logger.info("Flight controller connected and initialized")
        return True
    
    def disconnect(self):
        """Disconnect from flight controller"""
        self.serial.disconnect()
        self.connected = False
    
    def _handle_message(self, msg: Dict):
        """Handle received MSP message"""
        cmd = msg['command']
        data = msg['data']
        
        try:
            if cmd == MSPCommand.MSP_API_VERSION:
                self.device_info.update(MSPProtocol.decode_api_version(data))

            elif cmd == MSPCommand.MSP_FC_VARIANT:
                self.device_info.update(MSPProtocol.decode_fc_variant(data))

            elif cmd == MSPCommand.MSP_FC_VERSION:
                self.device_info.update(MSPProtocol.decode_fc_version(data))

            elif cmd == MSPCommand.MSP_BOARD_INFO:
                self.device_info.update(MSPProtocol.decode_board_info(data))

            elif cmd == MSPCommand.MSP_BUILD_INFO:
                self.device_info.update(MSPProtocol.decode_build_info(data))

            if cmd == MSPCommand.MSP_IDENT:
                self.device_info.update(MSPProtocol.decode_ident(data))
                logger.info(f"Device: {self.device_info}")
            
            elif cmd == MSPCommand.MSP_STATUS:
                self.status_data = MSPProtocol.decode_status(data)
            
            elif cmd == MSPCommand.MSP_RAW_IMU:
                self.sensor_data = MSPProtocol.decode_raw_imu(data)
            
            elif cmd == MSPCommand.MSP_MOTOR:
                motors = MSPProtocol.decode_motor(data)
                self.motor_speeds = motors.get('motors', [])
            
            elif cmd == MSPCommand.MSP_RC:
                rc = MSPProtocol.decode_rc(data)
                self.rc_channels = rc.get('channels', [])
            
            elif cmd == MSPCommand.MSP_ANALOG:
                analog = MSPProtocol.decode_analog(data)
                self.status_data.update(analog)
            
            # Call registered callbacks
            if cmd in self.callbacks:
                self.callbacks[cmd](data)
        
        except Exception as e:
            logger.error(f"Error processing message {cmd}: {e}")
    
    def request_ident(self):
        """Request device identification"""
        self.serial.send_msp(MSPCommand.MSP_IDENT)

    def request_device_info(self):
        """Request modern and legacy FC identity data."""
        self.serial.send_msp(MSPCommand.MSP_API_VERSION)
        self.serial.send_msp(MSPCommand.MSP_FC_VARIANT)
        self.serial.send_msp(MSPCommand.MSP_FC_VERSION)
        self.serial.send_msp(MSPCommand.MSP_BOARD_INFO)
        self.serial.send_msp(MSPCommand.MSP_BUILD_INFO)
        # Keep legacy fallback for older firmwares.
        self.request_ident()
    
    def request_status(self):
        """Request flight controller status"""
        self.serial.send_msp(MSPCommand.MSP_STATUS)
    
    def request_sensors(self):
        """Request raw sensor data (IMU)"""
        self.serial.send_msp(MSPCommand.MSP_RAW_IMU)
    
    def request_motors(self):
        """Request current motor speeds"""
        self.serial.send_msp(MSPCommand.MSP_MOTOR)
    
    def request_rc(self):
        """Request RC channel values"""
        self.serial.send_msp(MSPCommand.MSP_RC)
    
    def request_analog(self):
        """Request analog sensor data (battery, RSSI, etc)"""
        self.serial.send_msp(MSPCommand.MSP_ANALOG)
    
    def get_telemetry(self) -> Dict[str, Any]:
        """Get all telemetry data"""
        self.request_status()
        self.request_sensors()
        self.request_motors()
        self.request_rc()
        self.request_analog()
        
        time.sleep(0.1)  # Allow time to receive responses
        
        return {
            'device': self.device_info,
            'status': self.status_data,
            'sensors': self.sensor_data,
            'motors': self.motor_speeds,
            'rc_channels': self.rc_channels,
        }
    
    def register_callback(self, command: int, callback: Callable):
        """Register callback for specific MSP command"""
        self.callbacks[command] = callback
    
    def calibrate_accelerometer(self) -> bool:
        """Calibrate accelerometer"""
        logger.info("Starting accelerometer calibration...")
        self.serial.send_msp(MSPCommand.MSP_ACC_CALIBRATION)
        time.sleep(2)  # Wait for calibration
        logger.info("Accelerometer calibration complete")
        return True
    
    def calibrate_magnetometer(self) -> bool:
        """Calibrate magnetometer"""
        logger.info("Starting magnetometer calibration...")
        self.serial.send_msp(MSPCommand.MSP_MAG_CALIBRATION)
        time.sleep(3)  # Wait for calibration
        logger.info("Magnetometer calibration complete")
        return True
    
    def save_configuration(self) -> bool:
        """Save configuration to EEPROM"""
        logger.info("Saving configuration...")
        self.serial.send_msp(MSPCommand.MSP_EEPROM_WRITE)
        time.sleep(1)
        logger.info("Configuration saved")
        return True

    def set_motor_test_values(self, motor_values) -> bool:
        """Set motor PWM values for bench testing via MSP_SET_MOTOR.

        Expects list of up to 8 PWM values (1000-2000). Missing motors are padded
        with 1000 so they stay stopped on typical ESC ranges.
        """
        if not self.connected:
            logger.warning("Cannot set motor values while disconnected")
            return False

        normalized = []
        for value in list(motor_values)[:8]:
            try:
                pwm = int(value)
            except (TypeError, ValueError):
                pwm = 1000
            pwm = max(1000, min(2000, pwm))
            normalized.append(pwm)

        while len(normalized) < 8:
            normalized.append(1000)

        payload = struct.pack('<8H', *normalized)
        return self.serial.send_msp(MSPCommand.MSP_SET_MOTOR, payload)
