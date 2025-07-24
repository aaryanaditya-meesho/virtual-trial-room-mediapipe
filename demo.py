#!/usr/bin/env python3
"""
Demo script for MediaPipe Shoulder Distance Calculator
Simple example showing how to use the ShoulderDistanceCalculator class
"""

from shoulder_distance import ShoulderDistanceCalculator
import cv2
import sys

def test_mediapipe_installation():
    """Test if MediaPipe and other dependencies are properly installed."""
    try:
        import mediapipe as mp
        import cv2
        import numpy as np
        print("✅ All dependencies are installed correctly!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip3 install -r requirements.txt")
        return False

def quick_demo():
    """Run a quick demo with webcam."""
    if not test_mediapipe_installation():
        return
    
    print("\n🎯 MediaPipe Shoulder Distance Calculator Demo")
    print("=" * 50)
    print("This demo will:")
    print("1. Access your webcam")
    print("2. Detect your pose using MediaPipe")
    print("3. Calculate distance between your shoulders")
    print("4. Display real-time measurements")
    print("\nControls:")
    print("- Press 'q' to quit")
    print("- Press 's' to save a screenshot")
    print("- Make sure you're well-lit and visible to the camera")
    
    input("\nPress Enter to start the demo...")
    
    try:
        calculator = ShoulderDistanceCalculator()
        calculator.run_webcam()
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        print("Make sure your webcam is connected and accessible.")

if __name__ == "__main__":
    quick_demo() 