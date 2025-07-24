#!/usr/bin/env python3
"""
Test script for MediaPipe Shoulder Distance Calculator using a sample image
This doesn't require camera permissions and can verify the core functionality
"""

import cv2
import numpy as np
from shoulder_distance import ShoulderDistanceCalculator

def create_test_image():
    """Create a simple test image with a basic figure for testing."""
    # Create a blank image
    img = np.zeros((600, 800, 3), dtype=np.uint8)
    img.fill(50)  # Dark gray background
    
    # Draw a simple stick figure for testing
    # Head
    cv2.circle(img, (400, 100), 30, (255, 255, 255), -1)
    
    # Body
    cv2.line(img, (400, 130), (400, 350), (255, 255, 255), 8)
    
    # Left arm
    cv2.line(img, (400, 200), (300, 180), (255, 255, 255), 6)  # Left shoulder
    cv2.line(img, (300, 180), (250, 250), (255, 255, 255), 6)  # Left forearm
    
    # Right arm  
    cv2.line(img, (400, 200), (500, 180), (255, 255, 255), 6)  # Right shoulder
    cv2.line(img, (500, 180), (550, 250), (255, 255, 255), 6)  # Right forearm
    
    # Legs
    cv2.line(img, (400, 350), (350, 500), (255, 255, 255), 6)  # Left leg
    cv2.line(img, (400, 350), (450, 500), (255, 255, 255), 6)  # Right leg
    
    # Add text
    cv2.putText(img, "Test Image for Pose Detection", (50, 550), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    return img

def test_with_sample_image():
    """Test the shoulder distance calculator with a sample image."""
    print("🔬 Testing MediaPipe Shoulder Distance Calculator")
    print("=" * 50)
    
    # Create test image
    test_image = create_test_image()
    cv2.imwrite("test_pose.jpg", test_image)
    print("✅ Created test image: test_pose.jpg")
    
    # Initialize calculator
    calculator = ShoulderDistanceCalculator()
    print("✅ Initialized MediaPipe Pose Calculator")
    
    # Process the test image
    print("\n📊 Processing test image...")
    processed_image, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, confidence, scale_info, z_info = calculator.process_frame(test_image)
    
    # Add information overlay
    calculator.add_info_overlay(processed_image, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, 0, confidence, scale_info, z_info)
    
    # Save result
    cv2.imwrite("test_result.jpg", processed_image)
    
    # Print results
    print(f"📏 Shoulder 3D Distance: {shoulder_3d:.4f}")
    print(f"📐 Shoulder Pixel Distance: {shoulder_pixels:.1f}")
    if shoulder_cm:
        print(f"📏 Shoulder Real Distance: {shoulder_cm:.1f} cm ({shoulder_pixels:.1f} px)")
    else:
        print("📏 Shoulder Real Distance: Not available (no calibration)")
    
    print(f"📏 Waist 3D Distance: {waist_3d:.4f}")
    print(f"📐 Waist Pixel Distance: {waist_pixels:.1f}")
    if waist_cm:
        print(f"📏 Waist Real Distance: {waist_cm:.1f} cm ({waist_pixels:.1f} px)")
    else:
        print("📏 Waist Real Distance: Not available (no calibration)")
        
    print(f"🎯 Confidence: {confidence:.2f}")
    print(f"📊 Scale Info: {scale_info}")
    if z_info:
        print(f"📍 Shoulder Z: L={z_info['shoulder_left_z']:.3f}, R={z_info['shoulder_right_z']:.3f}, Diff={z_info['shoulder_z_diff']:.3f}")
        print(f"📍 Waist Z: L={z_info['waist_left_z']:.3f}, R={z_info['waist_right_z']:.3f}, Diff={z_info['waist_z_diff']:.3f}")
    print("✅ Saved result as: test_result.jpg")
    
    if distance_3d > 0:
        print("\n🎉 SUCCESS: MediaPipe pose detection is working!")
        print("Your shoulder distance calculator is ready to use!")
        print("\nNext steps:")
        print("1. Run 'python3 shoulder_distance.py' for webcam mode")
        print("2. Press 'c' in webcam mode to calibrate for real measurements")
        print("3. Or use image mode: 'python3 shoulder_distance.py' and choose option 2")
        print("\n💡 Calibration tips:")
        print("- Automatic calibration uses your facial features")
        print("- Manual calibration: use a credit card (8.5cm) or ruler")
        print("- Better lighting = better automatic calibration")
    else:
        print("\n⚠️  No pose detected in test image")
        print("This is normal - MediaPipe works best with real human poses")
        print("Try with a real photo or webcam for better results")

def test_real_image():
    """Test with a real image if available."""
    print("\n📷 Want to test with your own image?")
    image_path = input("Enter path to an image file (or press Enter to skip): ").strip()
    
    if image_path and image_path.lower() != "":
        try:
            calculator = ShoulderDistanceCalculator()
            calculator.process_image(image_path, "your_result.jpg")
            print("\n💡 Note: If no centimeter measurement is shown, try:")
            print("1. Make sure your face is visible (for automatic calibration)")
            print("2. Use manual calibration by pressing 'c' in the image viewer")
        except Exception as e:
            print(f"❌ Error processing image: {e}")

def demo_calibration_info():
    """Show information about calibration options."""
    print("\n🎯 Enhanced Body Measurement Calculator")
    print("=" * 45)
    print("The app now supports:")
    print("✅ Real-world measurements in centimeters!")
    print("✅ Detailed Z-coordinate (depth) information!")
    print("✅ Both shoulder AND waist measurements!")
    print("\n📏 DISTANCE MEASUREMENTS:")
    print("   - Shoulder width (2D & 3D, displays both pixels & cm)")
    print("   - Waist width (2D & 3D, displays both pixels & cm)")
    print("   - Individual Z coordinates for all points")
    print("   - Depth differences for posture analysis")
    print("\n🎨 VISUAL INDICATORS:")
    print("   - Green line: Shoulder measurement")
    print("   - Orange line: Waist measurement")
    print("   - Labels: LS/RS (shoulders), LH/RH (hips)")
    print("\n1. AUTOMATIC CALIBRATION:")
    print("   - Uses facial features (eye distance ≈ 6.3cm)")
    print("   - Works when your face is visible")
    print("   - No manual input needed")
    print("\n2. MANUAL CALIBRATION:")
    print("   - Use any object with known size")
    print("   - Credit card: 8.5cm wide")
    print("   - Ruler: any measurement")
    print("   - Click two points on the object")
    print("\n3. CALIBRATION IS SAVED:")
    print("   - Your calibration is saved to calibration.json")
    print("   - No need to recalibrate each time")
    print("   - Press 'r' to reset if needed")
    print("\n📍 Z COORDINATE INFO:")
    print("   - Shows depth of shoulders & waist")
    print("   - Calculates depth differences")
    print("   - Estimates real depths in cm")
    print("   - Press 'z' to toggle display")

if __name__ == "__main__":
    demo_calibration_info()
    test_with_sample_image()
    test_real_image() 