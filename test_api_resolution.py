#!/usr/bin/env python3
"""
Test script for Resolution-Aware Shoulder Distance API
Tests the API with different image resolutions to validate consistent measurements
"""

import requests
import cv2
import numpy as np
import json
import base64
from io import BytesIO
from PIL import Image
import time

def create_test_image(width, height, person_width_cm=40):
    """Create a synthetic test image with a person silhouette"""
    # Create a black background
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Calculate person dimensions based on image size
    person_height = int(height * 0.7)  # Person takes 70% of image height
    person_width = int(width * 0.2)    # Person takes 20% of image width
    
    # Center the person
    start_x = (width - person_width) // 2
    start_y = (height - person_height) // 2
    
    # Draw simple person shape (rectangle with head circle)
    # Body
    cv2.rectangle(img, (start_x, start_y + 50), (start_x + person_width, start_y + person_height), (255, 255, 255), -1)
    
    # Head
    head_radius = person_width // 4
    head_center = (start_x + person_width // 2, start_y + head_radius)
    cv2.circle(img, head_center, head_radius, (255, 255, 255), -1)
    
    # Add some MediaPipe-like landmarks (approximate shoulder positions)
    shoulder_y = start_y + 80
    left_shoulder = (start_x + 10, shoulder_y)
    right_shoulder = (start_x + person_width - 10, shoulder_y)
    
    # Draw shoulder markers
    cv2.circle(img, left_shoulder, 5, (0, 255, 0), -1)
    cv2.circle(img, right_shoulder, 5, (0, 255, 0), -1)
    
    # Calculate expected shoulder width in pixels
    expected_shoulder_pixels = abs(right_shoulder[0] - left_shoulder[0])
    
    return img, expected_shoulder_pixels

def image_to_base64(image):
    """Convert OpenCV image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64

def test_resolution(api_url, width, height):
    """Test API with specific resolution"""
    print(f"\n🧪 Testing resolution: {width}x{height}")
    
    # Create test image
    test_img, expected_pixels = create_test_image(width, height)
    
    # Save test image for reference
    cv2.imwrite(f'test_{width}x{height}.jpg', test_img)
    
    # Convert to format for API
    img_base64 = image_to_base64(test_img)
    
    try:
        # Test via file upload (REST API)
        with open(f'test_{width}x{height}.jpg', 'rb') as f:
            files = {'image': f}
            response = requests.post(f'{api_url}/process_image', files=files, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            measurements = result['measurements']
            
            print(f"   📐 Expected shoulder pixels: {expected_pixels}")
            print(f"   📏 Measured shoulder pixels: {measurements['shoulder_pixels']:.1f}")
            print(f"   📊 Measured shoulder cm: {measurements.get('shoulder_cm', 'N/A')}")
            print(f"   🎯 Resolution info: {measurements.get('resolution', 'N/A')}")
            print(f"   ⚡ Confidence: {measurements['confidence']:.2f}")
            
            # Calculate accuracy
            if measurements['shoulder_pixels'] > 0:
                accuracy = abs(expected_pixels - measurements['shoulder_pixels']) / expected_pixels * 100
                print(f"   ✅ Pixel accuracy: {100-accuracy:.1f}%")
            
            return measurements
        else:
            print(f"   ❌ API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return None

def main():
    """Run resolution tests"""
    api_url = 'http://localhost:5000'
    
    print("🎯 Resolution-Aware Shoulder Distance API Test")
    print("=" * 50)
    
    # Test if API is running
    try:
        health = requests.get(f'{api_url}/health', timeout=5)
        if health.status_code == 200:
            print("✅ API is running and healthy")
        else:
            print("❌ API health check failed")
            return
    except:
        print("❌ Cannot connect to API. Make sure it's running on localhost:5000")
        print("   Run: source venv/bin/activate && python streaming_api.py")
        return
    
    # Test different resolutions
    resolutions = [
        (320, 240),   # Low resolution
        (640, 480),   # Standard resolution (reference)
        (800, 600),   # Higher resolution
        (1280, 720),  # HD resolution
        (1920, 1080), # Full HD resolution
    ]
    
    results = []
    
    for width, height in resolutions:
        result = test_resolution(api_url, width, height)
        if result:
            results.append({
                'resolution': f'{width}x{height}',
                'width': width,
                'height': height,
                'measurements': result
            })
        time.sleep(1)  # Brief pause between tests
    
    # Analysis
    print("\n📊 Resolution Consistency Analysis")
    print("=" * 50)
    
    if len(results) >= 2:
        reference_cm = None
        
        for result in results:
            res = result['resolution']
            measurements = result['measurements']
            
            if measurements.get('shoulder_cm'):
                cm_value = measurements['shoulder_cm']
                
                if reference_cm is None:
                    reference_cm = cm_value
                    print(f"📐 {res}: {cm_value:.1f} cm (reference)")
                else:
                    diff = abs(cm_value - reference_cm)
                    diff_percent = (diff / reference_cm) * 100
                    status = "✅" if diff_percent < 10 else "⚠️" if diff_percent < 20 else "❌"
                    print(f"📐 {res}: {cm_value:.1f} cm (±{diff:.1f}cm, {diff_percent:.1f}%) {status}")
        
        print(f"\n🎯 Resolution-aware calibration is {'✅ WORKING' if all(abs(r['measurements'].get('shoulder_cm', 0) - reference_cm) / reference_cm * 100 < 20 for r in results if r['measurements'].get('shoulder_cm')) else '❌ NEEDS ADJUSTMENT'}")
    
    # Cleanup test images
    print(f"\n🧹 Cleaning up test images...")
    for width, height in resolutions:
        try:
            import os
            os.remove(f'test_{width}x{height}.jpg')
        except:
            pass

if __name__ == "__main__":
    main() 