# Quick Start Guide - F722 Flight Controller Software

## Prerequisites
- Windows PC (or Linux/Mac with Python)
- F722 flight controller with Betaflight firmware
- USB cable to connect F722 to PC
- Python 3.7 or higher
- pyserial library

## Step 1: Install Dependencies

Open PowerShell/Command Prompt and run:
```
cd C:\Users\fosna\Desktop\FlightController
pip install -r requirements.txt
```

## Step 2: Connect F722 via USB

1. Connect your F722 flight controller to your PC using a USB cable
2. Wait for Windows to recognize the device
3. Open Device Manager (press Win+X, select Device Manager)
4. Look for "USB Serial Device" or similar under "Ports (COM & LPT)"
5. Note the COM port (e.g., COM3, COM4)

## Step 3: Run the Application

In PowerShell/Command Prompt, run:
```
cd C:\Users\fosna\Desktop\FlightController
python src\gui_main.py
```

The GUI should open. You'll see the connection panel at the top.

## Step 4: Connect to Flight Controller

1. Click "Refresh Ports" button to detect available COM ports
2. Select your F722's COM port from the dropdown (usually the only one detected)
3. Click "Connect" button
4. Wait a moment for the connection to establish
5. You should see:
   - Status: green "Connected" message
   - Device information displayed (type, firmware version)
   - Real-time telemetry data starting to update

## Step 5: Monitor Your Flight Controller

Once connected, you can:

### View Telemetry (Telemetry Tab)
- Motor speeds (should be around 1000 PWM at idle)
- RC channel inputs (move your transmitter sticks to see them change)
- Battery voltage and current
- Power consumption (mAh)

### Monitor Sensors (Sensors Tab)
- Gyroscope readings (should be near 0 when stationary)
- Accelerometer (should show Z ≈ 1.0g when level)
- Magnetometer values

### Calibrate Sensors (Calibration Tab)
- **Accelerometer**: Place on level surface, click "Calibrate Accelerometer"
- **Magnetometer**: Rotate drone slowly in all directions, click "Calibrate Magnetometer"

### Save Configuration (Configure Tab)
Click "Save Configuration" after making any changes to save them to the flight controller's EEPROM.

## Troubleshooting

### No COM ports detected
- Check that F722 is properly connected via USB
- Try a different USB port
- Install CH340 drivers if you're using a clone board
- Restart the application

### Connected but no data
- Check status - should say "Connected" in green
- Click "Refresh Ports" and reconnect
- Power cycle the flight controller
- Check that Betaflight firmware is properly installed

### "Access Denied" error on Windows
- Right-click gui_main.py and run as Administrator
- Or run PowerShell as Administrator before launching

## Custom Features to Add

Here are some custom features you can enable:

1. **PID Tuning Interface** - Adjust P, I, D values for different flight modes
2. **Blackbox Viewer** - Download and analyze flight logs
3. **Custom Flight Modes** - Create and configure custom flight behaviors
4. **Real-time Graphs** - Plot sensor data in real-time
5. **Firmware Flashing** - Update Betaflight firmware directly
6. **Advanced Filters** - Add noise filtering to sensor data
7. **Flight Data Logging** - Continuous logging to local storage
8. **Transmitter Configuration** - Map and configure RC inputs

Let me know which features interest you most, and I can implement them!

## Next Steps

Once you confirm the connection is working:
1. Test all telemetry readings are updating correctly
2. Move RC sticks and confirm channels are changing
3. Verify sensor calibration is working
4. Then we can add custom features like:
   - Real-time data visualization
   - Custom flight modes
   - PID tuning interface
   - And more advanced features

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the source code comments in src/ folder
3. Look at the log output in the terminal for error messages
