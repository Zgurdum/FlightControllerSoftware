"""
Serial communication handler for flight controller
Manages USB/Serial connection to F722 flight controller
"""

import serial
import threading
import time
from typing import Callable, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SerialHandler:
    """Handles serial communication with flight controller"""
    
    def __init__(self):
        self.port = None
        self.baudrate = 115200  # Standard Betaflight baudrate
        self.connection = None
        self.is_connected = False
        self.rx_thread = None
        self.stop_event = threading.Event()
        self.rx_callback: Optional[Callable] = None
        self.buffer = bytearray()
        
    def list_ports(self):
        """List available serial ports"""
        import serial.tools.list_ports
        ports = []
        for port, desc, hwid in serial.tools.list_ports.comports():
            ports.append({'port': port, 'description': desc, 'hwid': hwid})
        return ports
    
    def connect(self, port: str, baudrate: int = 115200) -> bool:
        """Connect to flight controller via serial port"""
        try:
            self.port = port
            self.baudrate = baudrate
            self.connection = serial.Serial(port, baudrate, timeout=1)
            self.is_connected = True
            self.stop_event.clear()
            
            # Start RX thread
            self.rx_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.rx_thread.start()
            
            logger.info(f"Connected to {port} at {baudrate} baud")
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from flight controller"""
        try:
            self.stop_event.set()
            if self.connection:
                self.connection.close()
            self.is_connected = False
            logger.info("Disconnected from flight controller")
        except Exception as e:
            logger.error(f"Disconnect error: {e}")
    
    def _receive_loop(self):
        """Continuously read data from serial port"""
        while not self.stop_event.is_set():
            try:
                if self.connection and self.connection.in_waiting:
                    data = self.connection.read(self.connection.in_waiting)
                    if data:
                        self.buffer.extend(data)
                        
                        # Check for complete messages
                        while len(self.buffer) > 0:
                            result = self._parse_msp_message()
                            if result is None:
                                break
                            if self.rx_callback:
                                self.rx_callback(result)
            except Exception as e:
                logger.error(f"RX loop error: {e}")
                break
            time.sleep(0.001)
    
    def _parse_msp_message(self):
        """Parse MSP message from buffer"""
        if len(self.buffer) < 6:
            return None
        
        # MSP message format: $M<direction><length><command><data...><checksum>
        if self.buffer[0:1] != b'$':
            self.buffer.pop(0)
            return None
        
        if self.buffer[1:2] not in [b'M', b'm']:
            self.buffer.pop(0)
            return None
        
        direction = self.buffer[1]
        payload_len = self.buffer[3]
        
        if len(self.buffer) < 6 + payload_len:
            return None
        
        command = self.buffer[4]
        data = bytes(self.buffer[5:5 + payload_len])
        checksum = self.buffer[5 + payload_len]
        
        # Verify checksum
        expected_checksum = payload_len ^ command
        for byte in data:
            expected_checksum ^= byte
        
        if checksum != expected_checksum:
            self.buffer.pop(0)
            return None
        
        # Remove processed message
        del self.buffer[:6 + payload_len]
        
        return {
            'direction': direction,
            'command': command,
            'data': data,
            'payload_len': payload_len
        }
    
    def send_msp(self, command: int, data: bytes = b''):
        """Send MSP command to flight controller"""
        if not self.is_connected:
            logger.warning("Not connected to flight controller")
            return False
        
        payload_len = len(data)
        checksum = payload_len ^ command
        for byte in data:
            checksum ^= byte
        
        message = b'$M<' + bytes([payload_len, command]) + data + bytes([checksum])
        
        try:
            self.connection.write(message)
            logger.debug(f"Sent MSP command {command} with {payload_len} bytes")
            return True
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False
    
    def set_rx_callback(self, callback: Callable):
        """Set callback for received messages"""
        self.rx_callback = callback
