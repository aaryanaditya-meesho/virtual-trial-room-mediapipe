#!/usr/bin/env python3
"""
Quick test to verify resolution-aware calibration is working
"""

import cv2
import numpy as np
import requests
import json
import time

def create_simple_test_image(width, height):
    """Create a simple test image with known shoulder width"""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Draw a simple stick figure with known proportions
    center_x = width // 2
    center_y = height // 2
    
    # Head (circle)
    cv2.circle(img, (center_x, center_y - 100), 30, (255, 255, 255), -1)
    
    # Body (line)
    cv2.line(img, (center_x, center_y - 70), (center_x, center_y + 100), (255, 255, 255), 5)
    
    # Arms (horizontal line) - this represents shoulders
    shoulder_width_pixels = width // 4  # Quarter of image width
    left_shoulder = (center_x - shoulder_width_pixels//2, center_y - 50)
    right_shoulder = (center_x + shoulder_width_pixels//2, center_y - 50)
    
    cv2.line(img, left_shoulder, right_shoulder, (255, 255, 255), 5)
    
    # Mark shoulder points clearly
    cv2.circle(img, left_shoulder, 8, (0, 255, 0), -1)
    cv2.circle(img, right_shoulder, 8, (0, 255, 0), -1)
    
    print(f"Created test image {width}x{height} with shoulder width: {shoulder_width_pixels}px")
    return img, shoulder_width_pixels

def test_calibration():
    """Test the calibration with different resolutions"""
    api_url = 'http://localhost:5000'
    
    # Test resolutions
    resolutions = [
        (320, 240),
        (640, 480),
        (960, 720),
        (1280, 960)
    ]
    
    print("🧪 Testing Resolution-Aware Calibration")
    print("=" * 50)
    
    for width, height in resolutions:
        print(f"\n📏 Testing {width}x{height}...")
        
        # Create test image
        img, expected_shoulder_px = create_simple_test_image(width, height)
        
        # Save and send to API
        filename = f'test_cal_{width}x{height}.jpg'
        cv2.imwrite(filename, img)
        
        try:
            with open(filename, 'rb') as f:
                response = requests.post(f'{api_url}/process_image', files={'image': f}, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                measurements = result['measurements']
                
                print(f"   Expected: {expected_shoulder_px}px")
                print(f"   Measured: {measurements['shoulder_pixels']:.1f}px")
                print(f"   Shoulder: {measurements.get('shoulder_cm', 'N/A')} cm")
                print(f"   Resolution: {measurements.get('resolution', {}).get('width', 'N/A')}x{measurements.get('resolution', {}).get('height', 'N/A')}")
                print(f"   Multiplier: {measurements.get('resolution', {}).get('multiplier', 'N/A')}")
                print(f"   Calibration: {measurements.get('resolution', {}).get('dynamic_calibration', 'N/A')} px/cm")
                
                # Check accuracy
                if measurements['shoulder_pixels'] > 0:
                    accuracy = abs(expected_shoulder_px - measurements['shoulder_pixels']) / expected_shoulder_px * 100
                    status = "✅" if accuracy < 10 else "⚠️" if accuracy < 25 else "❌"
                    print(f"   Accuracy: {100-accuracy:.1f}% {status}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        
        # Clean up
        try:
            import os
            os.remove(filename)
        except:
            pass
            
        time.sleep(0.5)

if __name__ == "__main__":
    test_calibration() 