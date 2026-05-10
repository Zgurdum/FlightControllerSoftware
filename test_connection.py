"""
Test script to verify F722 flight controller connection
Run this to test basic communication before running the full GUI
"""

import sys
import time
import argparse
from src.serial_handler import SerialHandler
from src.flight_controller import FlightControllerInterface
from src.msp_protocol import MSPCommand


def select_best_port(ports):
    """Prefer likely USB flight controller ports over legacy COM ports."""
    def port_score(port_info):
        port_name = (port_info.get('port') or '').upper()
        description = (port_info.get('description') or '').upper()
        hwid = (port_info.get('hwid') or '').upper()
        text = f"{description} {hwid}"

        score = 0
        preferred_markers = ['USB', 'STM', 'DFU', 'CP210', 'CH340', 'CH341', 'FTDI', 'VIRTUAL COM']
        if any(marker in text for marker in preferred_markers):
            score += 100
        if 'COMMUNICATIONS PORT' in description:
            score -= 100
        if port_name == 'COM1':
            score -= 50
        return score

    return max(ports, key=port_score)

def test_connection(port_override=None):
    """Test flight controller connection"""
    print("=" * 60)
    print("F722 Flight Controller - Connection Test")
    print("=" * 60)
    
    # Initialize
    fc = FlightControllerInterface()
    
    print("\n[1/4] Scanning for serial ports...")
    ports = fc.serial.list_ports()
    
    if not ports:
        print("✗ No serial ports found!")
        print("Please check:")
        print("  - F722 is connected via USB")
        print("  - Drivers are installed (CH340 if using clone board)")
        print("  - Windows recognizes it in Device Manager")
        return False
    
    print(f"✓ Found {len(ports)} port(s):")
    for port in ports:
        print(f"  - {port['port']}: {port['description']}")
    
    # Try to connect
    if port_override:
        target_port = port_override
    else:
        target_port = select_best_port(ports)['port']

    print(f"\n[2/4] Attempting connection to {target_port}...")
    if not fc.connect(target_port):
        print("✗ Connection failed!")
        return False
    
    print("✓ Connected successfully")
    
    # Request device info
    print("\n[3/4] Requesting device information...")
    for i in range(5):
        if fc.device_info:
            break
        time.sleep(0.2)
    
    if not fc.device_info:
        print("⚠ No device info received (firmware might not be Betaflight)")
        print("But connection established - continuing tests...")
    else:
        device_type = fc.device_info.get('fc_variant') or fc.device_info.get('type', 'Unknown')
        firmware_version = fc.device_info.get('fc_version') or fc.device_info.get('version', 'Unknown')
        msp_version = fc.device_info.get('api_version') or fc.device_info.get('msp_version', 'Unknown')
        board_id = fc.device_info.get('board_id', 'Unknown')

        print(f"✓ Device Info:")
        print(f"  Type: {device_type}")
        print(f"  Firmware: {firmware_version}")
        print(f"  MSP/API Version: {msp_version}")
        print(f"  Board ID: {board_id}")
    
    # Test telemetry
    print("\n[4/4] Testing telemetry stream...")
    print("Requesting status and sensor data...")
    
    telemetry = fc.get_telemetry()
    
    if telemetry['status']:
        print("✓ Status received:")
        print(f"  Cycle Time: {telemetry['status'].get('cycle_time', 'N/A')} µs")
        print(f"  System Load: {telemetry['status'].get('system_load', 'N/A')}%")
    
    if telemetry['sensors']:
        print("✓ Sensor data received:")
        sensors = telemetry['sensors']
        gyro = sensors.get('gyro', {})
        acc = sensors.get('accelerometer', {})
        print(f"  Gyro: X={gyro.get('x', 0):.2f} Y={gyro.get('y', 0):.2f} Z={gyro.get('z', 0):.2f} °/s")
        print(f"  Accel: X={acc.get('x', 0):.2f} Y={acc.get('y', 0):.2f} Z={acc.get('z', 0):.2f} g")
    else:
        print("⚠ No sensor data received")
    
    if telemetry['motors']:
        print(f"✓ Motor speeds: {telemetry['motors']}")
    else:
        print("⚠ No motor data (may not be armed)")
    
    if telemetry['rc_channels']:
        print(f"✓ RC Channels: {telemetry['rc_channels'][:4]} (showing first 4)")
    
    # Success
    print("\n" + "=" * 60)
    print("✓ Connection test SUCCESSFUL!")
    print("=" * 60)
    print("\nYour F722 is properly connected and communicating.")
    print("You can now run: python src/gui_main.py")
    print("\nTips:")
    print("  - Move your RC sticks to see channel values change")
    print("  - Rock the drone to see gyro/accelerometer data change")
    print("  - Run the test again to verify stability")
    
    fc.disconnect()
    return True


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Test F722 flight controller connection")
        parser.add_argument("--port", help="Optional COM port override, e.g. COM3")
        args = parser.parse_args()

        success = test_connection(args.port)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
