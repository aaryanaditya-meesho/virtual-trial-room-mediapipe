#!/usr/bin/env python3
"""
Simple launcher for the shoulder measurement tool
This can be called from the web interface or run directly
"""

import subprocess
import sys
import os

def launch_measurement_tool():
    """Launch the shoulder distance measurement tool"""
    script_path = os.path.join(os.path.dirname(__file__), 'shoulder_distance.py')
    
    print("🚀 Launching Virtual Tailor Body Measurement Tool...")
    print("📏 This will open your webcam for real-time measurements")
    print("✂️ Perfect for getting accurate measurements for traditional Indian wear!")
    print("-" * 50)
    
    try:
        # Try to run the script
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running measurement tool: {e}")
        print("💡 Make sure you have installed the requirements:")
        print("   pip3 install -r requirements.txt")
    except FileNotFoundError:
        print("❌ shoulder_distance.py not found!")
        print("💡 Make sure you're in the correct directory")
    except KeyboardInterrupt:
        print("\n👋 Measurement tool closed by user")

if __name__ == "__main__":
    launch_measurement_tool() 