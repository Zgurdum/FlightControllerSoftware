# VPython Troubleshooting Guide

## Problem: "vpython not installed" or "No module named 'pkg_resources'"

Your Python environment has an issue with VPython. The 3D visualization feature will be disabled, but the rest of the flight controller software will work normally.

---

## Solution 1: Use Python from Microsoft Store (Recommended)

1. **Uninstall your current Python** (if using pythoncore-3.14)
2. **Install Python from Microsoft Store:**
   - Open Microsoft Store
   - Search for "Python"
   - Download the latest version (3.11 or 3.12)
   - Click "Install"

3. **Run the setup script:**
   ```
   run.bat
   ```

The Microsoft Store Python typically has better setuptools integration and won't have the pkg_resources issue.

---

## Solution 2: Repair Python Installation

If you prefer your current Python installation, try repairing it:

### Option A: Fresh Virtual Environment (Safest)

```powershell
# Create a fresh virtual environment
python -m venv venv_flight_controller

# Activate it
venv_flight_controller\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the GUI
python src/gui_main.py
```

### Option B: Clean Install

```powershell
# Uninstall vpython and setuptools
python -m pip uninstall vpython setuptools wheel -y

# Reinstall everything
python -m pip install --upgrade setuptools wheel
python -m pip install -r requirements.txt
```

---

## Solution 3: Use Python 3.11 or 3.12

If you have multiple Python versions, try a newer version:

```powershell
# List installed Python versions
py --list-paths

# Use a specific version (e.g., Python 3.12)
py -3.12 -m pip install -r requirements.txt
py -3.12 src/gui_main.py
```

---

## Confirming the Fix

After trying a solution, test vpython:

```powershell
python -c "import vpython; print('✓ VPython is working!')"
```

If it shows `✓`, the issue is fixed. Run:

```powershell
run.bat
```

The 3D drone visualization should now be available in the Sensors tab.

---

## FAQ

**Q: Can I use the software without 3D visualization?**
A: Yes! All other features (telemetry, motor control, calibration, etc.) work fine. The 3D visualization is optional.

**Q: Why does this happen?**
A: It's a Python environment configuration issue where `setuptools` is installed but `pkg_resources` (a component of setuptools) isn't properly initialized. This can happen with certain Python distributions or corrupted installations.

**Q: How do I know which solution to try?**
A: Start with Solution 1 (Microsoft Store). If that's inconvenient, try Solution 2 Option A (virtual environment). Solution 2 Option B and Solution 3 are backups if the others don't work.

---

## Still Having Issues?

If none of these work, you can:
1. Open an issue on the project repository
2. Contact the developer with the output of: `python -c "import sys; print(sys.version)"`

Remember: The flight controller software is fully functional without VPython—you just won't have the 3D visualization feature.
