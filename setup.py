"""
Setup script for F722 Flight Controller Software
Run this to install dependencies
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 7):
        print(f"✗ Python 3.7+ required. You have {sys.version}")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_directories():
    """Create necessary directories"""
    dirs = ['data', 'config', 'src']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"✓ Created directory: {d}")

def main():
    print("=" * 50)
    print("F722 Flight Controller Software - Setup")
    print("=" * 50)
    
    if not check_python_version():
        sys.exit(1)
    
    create_directories()
    
    if not install_dependencies():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Setup complete! You can now run:")
    print("  python src/gui_main.py")
    print("=" * 50)

if __name__ == "__main__":
    main()
