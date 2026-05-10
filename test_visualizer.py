#!/usr/bin/env python3
"""Quick test of drone visualizer module."""

import sys
sys.path.insert(0, '.')

try:
    from src.drone_visualizer import create_visualizer
    print("[OK] Visualizer module imported successfully")
    
    viz = create_visualizer()
    if viz:
        print("[OK] Visualizer instance created")
        print("[OK] 3D visualization is available")
    else:
        print("[WARN] Visualizer creation returned None (vpython may not be available)")
        
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Unexpected error: {e}")
    sys.exit(1)

print("\n[SUCCESS] Visualizer module is ready to use!")
