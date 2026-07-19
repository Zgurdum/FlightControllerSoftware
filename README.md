# F722 Flight Controller Software

Drone programming software for F722 flight controllers running Betaflight firmware, similar to Betaflight Configurator.

## Features

- **Serial Communication**: Direct USB connection to F722 flight controller
- **MSP Protocol Support**: Full MultiWii Serial Protocol implementation (Betaflight compatible)
- **Real-time Telemetry**: Live streaming of sensor data, motor speeds, RC channels
- **Sensor Monitoring**:
  - Gyroscope (°/s)
  - Accelerometer (g)
  - Magnetometer
  - Battery voltage & current
  - RSSI signal strength
- **Calibration Tools**: Accelerometer and magnetometer calibration
- **Configuration Management**: Save/load flight controller settings
- **User-Friendly GUI**: Clean tkinter-based interface with tabs

## Requirements

- Python 3.7+
- USB connection to F722 flight controller
- Betaflight firmware installed on flight controller

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Connect F722 to USB

3. Run the application:
```bash
python src/gui_main.py
```

## Usage

### Connect to Flight Controller
1. Launch the application
2. Click "Refresh Ports" to detect available serial ports
3. Select the appropriate COM port (usually appears as "USB Serial Device")
4. Click "Connect"

### Monitor Telemetry
- **Telemetry Tab**: View real-time motor speeds, RC channels, and battery info
- **Sensors Tab**: View raw IMU (gyro, accel, mag) sensor data

### Calibrate Sensors
1. Go to "Calibration" tab
2. **Accelerometer**: Place drone on level surface, click calibrate
3. **Magnetometer**: Rotate drone in all directions, click calibrate

### Configuration
- Settings will be added in the Configure tab
- Click "Save Configuration" to save changes to flight controller EEPROM

## Protocol Implementation

The software uses the **MSP (MultiWii Serial Protocol)** which is the standard protocol for communicating with Betaflight and compatible flight controllers.

### Supported Commands
- MSP_IDENT (100): Device identification
- MSP_STATUS (101): Flight controller status
- MSP_RAW_IMU (102): Raw sensor data (gyro, accel, mag)
- MSP_MOTOR (104): Motor PWM values
- MSP_RC (105): RC channel input
- MSP_ANALOG (110): Battery voltage, current, RSSI
- MSP_ACC_CALIBRATION (205): Calibrate accelerometer
- MSP_MAG_CALIBRATION (207): Calibrate magnetometer
- MSP_EEPROM_WRITE (250): Save configuration

## Architecture

```
src/
├── gui_main.py           - Main GUI application
├── flight_controller.py  - Flight controller interface
├── msp_protocol.py       - MSP protocol encoder/decoder
└── serial_handler.py     - Serial communication handler
config/                    - Configuration files
data/                      - Data logging directory
```

## Custom Features (Roadmap)

Upcoming features to extend functionality:
- PID tuning interface
- Blackbox flight data viewer
- Custom flight modes
- Advanced filtering options
- Flight data logging and playback
- Firmware flashing capability

## Troubleshooting

### Can't detect COM port
- Ensure F722 is connected via USB
- Install CH340 drivers if using clone boards
- Check Windows Device Manager for "USB Serial Device"

### No data received
- Verify Betaflight is properly flashed on F722
- Check connection status (should be green when connected)
- Reset flight controller (power cycle)

### MSP checksum errors
- Update to latest Betaflight firmware
- Check USB cable quality
- Reduce baudrate if communication is unstable


