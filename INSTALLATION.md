# F722 Flight Controller - Installation & Setup Guide

## Important: Python Installation Required

Before running the flight controller software, you **must** install Python.

### Step 1: Install Python

1. Go to https://www.python.org/downloads/
2. Download **Python 3.11 or higher** (click the big yellow download button)
3. Run the installer
4. **IMPORTANT**: Check the box that says "Add Python to PATH" (at the bottom of the installer)
5. Click "Install Now"
6. Wait for installation to complete

### Step 2: Verify Python Installation

Open PowerShell or Command Prompt and run:
```
python --version
```

You should see something like: `Python 3.11.0`

If you get "command not found", Python wasn't added to PATH. Reinstall and make sure to check "Add Python to PATH".

### Step 3: Connect F722 to USB

1. Connect your F722 flight controller to your PC via USB cable
2. Wait a moment for Windows to recognize it
3. Check Device Manager (Win+X > Device Manager) under "Ports (COM & LPT)"
4. You should see "USB Serial Device" or "CH340" (note the COM port, e.g., COM3)

### Step 4: Install Drivers (if needed)

If you don't see the device in Device Manager or it shows an error:

**For CH340-based boards** (clone F722):
1. Download CH340 driver: https://www.wch.cn/downloads/CH341SER_EXE.html
2. Run the installer
3. Restart Windows
4. Reconnect F722

**For Genuine STM32 F722**:
- Windows should auto-install drivers
- If not, search for "STM32 Virtual COM Port Driver"

## Running the Software

### Option 1: Simple Launcher (Recommended)

1. Double-click `run.bat` in the FlightController folder
2. It will automatically:
   - Install dependencies
   - Test the connection to F722
   - Launch the GUI if successful

### Option 2: Manual Steps

Open PowerShell in the FlightController folder and run:

```powershell
# Install dependencies
pip install pyserial

# Test connection
python test_connection.py

# Launch GUI
python src\gui_main.py
```

## First Time Usage

1. **Run the connection test first**: `python test_connection.py`
   - This verifies your F722 is communicating properly
   - You'll see device info, sensor readings, and motor speeds
   - If this works, the full GUI will work too

2. **Launch the GUI**: `python src\gui_main.py`
   - Click "Refresh Ports"
   - Select your COM port
   - Click "Connect"
   - You should see green "Connected" status and real-time telemetry

3. **Monitor Telemetry**:
   - **Telemetry Tab**: Motor speeds, RC channels, battery info
   - **Sensors Tab**: Gyro, accelerometer, magnetometer readings
   - Move your RC sticks and rock the drone to see data change

4. **Calibrate Sensors**:
   - Go to Calibration tab
   - Place drone on level surface and calibrate accelerometer
   - Rotate drone in all directions and calibrate magnetometer

## Troubleshooting

### "Python not found" error
- Reinstall Python from https://www.python.org/
- Make sure "Add Python to PATH" is checked
- Restart your PC after installation

### "No serial ports found"
- Check that F722 is connected via USB
- Wait 5 seconds after plugging in (Windows detects it)
- Check Device Manager to see the COM port
- Try a different USB port
- Install CH340 driver if using clone board

### "Connected but no data"
- Check serial monitor - try unplugging/replugging F722
- Verify Betaflight firmware is installed (run Betaflight Configurator to check)
- Restart the application
- Reset flight controller (power cycle)

### "Access Denied" error
- Right-click PowerShell and select "Run as Administrator"
- Then run the command again

## Project Structure

```
FlightController/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── gui_main.py              # Main GUI application ← START HERE
│   ├── flight_controller.py     # Flight controller interface
│   ├── msp_protocol.py          # MSP protocol implementation
│   ├── serial_handler.py        # Serial communication
│   └── custom_features.py       # Custom feature framework
├── config/
│   └── default_config.json      # Configuration file
├── data/                        # Telemetry logs go here
├── test_connection.py           # Connection test script ← TEST FIRST
├── run.bat                      # One-click launcher
├── setup.py                     # Setup script
├── requirements.txt             # Python dependencies
├── README.md                    # Full documentation
├── QUICKSTART.md               # Quick start guide
└── .gitignore                  # Git ignore patterns
```

## Next: Custom Features

Once you have the basic connection working, you can enable custom features:

### Available Custom Features:
1. **DataLogger** - Continuous telemetry logging to CSV
2. **MotorTest** - Individual motor testing
3. **SensorAnalyzer** - Sensor drift detection

The framework is ready for you to add:
- PID tuning interface
- Real-time graphs
- Blackbox viewer
- Firmware updates
- Custom flight modes
- And more!

## Support

For detailed technical documentation, see:
- [README.md](README.md) - Full feature documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- Source code comments in `src/` folder

## What You Now Have

✓ Complete flight controller communication software
✓ Real-time telemetry monitoring
✓ Sensor calibration tools
✓ Extensible architecture for custom features
✓ Professional GUI interface
✓ Betaflight compatible MSP protocol implementation

You can now configure and monitor your F722 flight controller just like Betaflight Configurator, with custom features you can add yourself!
