import cv2
import mediapipe as mp
import numpy as np
import math
import time
import json
import os

class ShoulderDistanceCalculator:
    def __init__(self):
        # Initialize MediaPipe pose detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Landmark indices
        self.LEFT_SHOULDER = 11
        self.RIGHT_SHOULDER = 12
        self.LEFT_HIP = 23
        self.RIGHT_HIP = 24
        self.NOSE = 0
        self.LEFT_EAR = 7
        self.RIGHT_EAR = 8
        self.LEFT_EYE = 1
        self.RIGHT_EYE = 4
        
        # For FPS calculation
        self.prev_time = 0
        
        # Calibration settings
        self.calibration_file = "calibration.json"
        
        # User-specific calibration: 650px = 96cm (YOUR DEFAULT)
        self.user_calibration = 650.0 / 96.0  # 6.77 pixels per cm
        
        # Load saved calibration, but use user calibration as default
        loaded_calibration = self.load_calibration()
        self.pixels_per_cm = loaded_calibration if loaded_calibration else self.user_calibration
        
        # Average human measurements for reference (in cm)
        self.avg_shoulder_width = 45.0  # Average shoulder width for adults
        self.avg_head_width = 15.0      # Average head width
        self.avg_eye_distance = 6.3     # Average distance between eyes
        
        # Display settings
        self.show_z_info = True  # Show Z coordinate information by default
        
    def load_calibration(self):
        """Load calibration data from file."""
        if os.path.exists(self.calibration_file):
            try:
                with open(self.calibration_file, 'r') as f:
                    data = json.load(f)
                    return data.get('pixels_per_cm', None)
            except:
                pass
        return None
    
    def save_calibration(self, pixels_per_cm):
        """Save calibration data to file."""
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump({'pixels_per_cm': pixels_per_cm}, f)
            self.pixels_per_cm = pixels_per_cm
        except Exception as e:
            print(f"Warning: Could not save calibration: {e}")
    
    def estimate_scale_from_face(self, landmarks, width, height):
        """
        Estimate pixels per cm using facial features.
        Uses the distance between eyes as reference (average ~6.3cm).
        """
        try:
            left_eye = landmarks.landmark[self.LEFT_EYE]
            right_eye = landmarks.landmark[self.RIGHT_EYE]
            
            # Calculate eye distance in pixels
            eye_distance_pixels = self.calculate_pixel_distance(left_eye, right_eye, width, height)
            
            if eye_distance_pixels > 10:  # Reasonable minimum
                pixels_per_cm = eye_distance_pixels / self.avg_eye_distance
                return pixels_per_cm
        except:
            pass
        return None
    
    def estimate_scale_from_head(self, landmarks, width, height):
        """
        Estimate pixels per cm using head width.
        Uses the distance between ears as reference.
        """
        try:
            left_ear = landmarks.landmark[self.LEFT_EAR]
            right_ear = landmarks.landmark[self.RIGHT_EAR]
            
            # Calculate head width in pixels
            head_width_pixels = self.calculate_pixel_distance(left_ear, right_ear, width, height)
            
            if head_width_pixels > 20:  # Reasonable minimum
                pixels_per_cm = head_width_pixels / self.avg_head_width
                return pixels_per_cm
        except:
            pass
        return None
    
    def get_automatic_scale(self, landmarks, width, height):
        """
        Automatically estimate scale using facial features.
        """
        # Try eye distance first (more reliable)
        scale = self.estimate_scale_from_face(landmarks, width, height)
        if scale:
            return scale
            
        # Fallback to head width
        scale = self.estimate_scale_from_head(landmarks, width, height)
        if scale:
            return scale
            
        return None
    
    def calibrate_with_reference(self, image, landmarks):
        """
        Interactive calibration using a reference object.
        """
        print("\n🔧 Calibration Mode")
        print("=" * 40)
        print("Choose calibration method:")
        print("1. Use preset calibration (650px = 96cm)")
        print("2. Manual calibration with reference object")
        print("3. Cancel")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            # Use preset calibration
            self.save_calibration(self.user_calibration)
            print(f"✅ Using preset calibration: 650px = 96cm")
            print(f"📐 Scale: {self.user_calibration:.2f} pixels per cm")
            return self.user_calibration
        elif choice == "3":
            print("❌ Calibration cancelled")
            return None
        
        # Manual calibration (choice == "2" or invalid choice defaults to manual)
        print("\nYou'll need a reference object with known size.")
        print("Good options: credit card (8.5cm), ruler, coin, etc.")
        
        # Get reference size
        while True:
            try:
                ref_size = float(input("Enter the real size of your reference object (in cm): "))
                if ref_size > 0:
                    break
                print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Show the image for reference selection
        height, width = image.shape[:2]
        display_img = image.copy()
        
        # Draw pose landmarks for reference
        if landmarks:
            self.mp_drawing.draw_landmarks(
                display_img, landmarks, self.mp_pose.POSE_CONNECTIONS
            )
        
        print(f"\nClick two points on the {ref_size}cm object in the image window.")
        print("Press any key after clicking to confirm.")
        
        # Store clicked points
        points = []
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                cv2.circle(display_img, (x, y), 5, (0, 255, 0), -1)
                cv2.putText(display_img, f"Point {len(points)}", (x+10, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.imshow('Calibration', display_img)
                
                if len(points) == 2:
                    # Draw line between points
                    cv2.line(display_img, points[0], points[1], (0, 255, 0), 2)
                    cv2.imshow('Calibration', display_img)
        
        cv2.imshow('Calibration', display_img)
        cv2.setMouseCallback('Calibration', mouse_callback)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        if len(points) == 2:
            # Calculate distance between points
            pixel_distance = math.sqrt(
                (points[1][0] - points[0][0]) ** 2 + 
                (points[1][1] - points[0][1]) ** 2
            )
            
            # Calculate pixels per cm
            pixels_per_cm = pixel_distance / ref_size
            print(f"✅ Calibration complete!")
            print(f"📏 Reference distance: {pixel_distance:.1f} pixels = {ref_size} cm")
            print(f"📐 Scale: {pixels_per_cm:.2f} pixels per cm")
            
            # Save calibration
            self.save_calibration(pixels_per_cm)
            return pixels_per_cm
        else:
            print("❌ Calibration cancelled - need exactly 2 points")
            return None
    
    def calculate_distance(self, point1, point2):
        """
        Calculate 3D Euclidean distance between two landmarks.
        """
        return math.sqrt(
            (point1.x - point2.x) ** 2 +
            (point1.y - point2.y) ** 2 +
            (point1.z - point2.z) ** 2
        )
    
    def calculate_pixel_distance(self, point1, point2, width, height):
        """
        Calculate distance in pixels for display purposes.
        """
        x1, y1 = point1.x * width, point1.y * height
        x2, y2 = point2.x * width, point2.y * height
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    def pixels_to_cm(self, pixel_distance, auto_scale=None):
        """
        Convert pixel distance to centimeters.
        """
        # Always use saved calibration (which defaults to user calibration)
        if self.pixels_per_cm:
            return pixel_distance / self.pixels_per_cm
        
        # Fallback to automatic scale estimation if somehow no calibration is set
        if auto_scale:
            return pixel_distance / auto_scale
        
        # No calibration available (should not happen with default user calibration)
        return None
    
    def draw_landmarks_and_distance(self, image, results, shoulder_distance_cm, waist_distance_cm):
        """
        Draw pose landmarks and distance information on the image.
        """
        height, width = image.shape[:2]
        
        # Draw pose landmarks
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Get shoulder coordinates
            left_shoulder = results.pose_landmarks.landmark[self.LEFT_SHOULDER]
            right_shoulder = results.pose_landmarks.landmark[self.RIGHT_SHOULDER]
            
            # Convert shoulder coordinates to pixels
            left_shoulder_x = int(left_shoulder.x * width)
            left_shoulder_y = int(left_shoulder.y * height)
            right_shoulder_x = int(right_shoulder.x * width)
            right_shoulder_y = int(right_shoulder.y * height)
            
            # Draw line between shoulders
            cv2.line(image, (left_shoulder_x, left_shoulder_y), (right_shoulder_x, right_shoulder_y), (0, 255, 0), 3)
            
            # Draw shoulder points
            cv2.circle(image, (left_shoulder_x, left_shoulder_y), 8, (255, 0, 0), -1)
            cv2.circle(image, (right_shoulder_x, right_shoulder_y), 8, (255, 0, 0), -1)
            
            # Add shoulder labels
            cv2.putText(image, "LS", (left_shoulder_x - 25, left_shoulder_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(image, "RS", (right_shoulder_x + 10, right_shoulder_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Add shoulder distance measurement on the line
            shoulder_mid_x = (left_shoulder_x + right_shoulder_x) // 2
            shoulder_mid_y = (left_shoulder_y + right_shoulder_y) // 2
            
            # Calculate pixel distance for display
            shoulder_pixel_dist = self.calculate_pixel_distance(left_shoulder, right_shoulder, width, height)
            
            if shoulder_distance_cm:
                distance_text = f"S: {shoulder_distance_cm:.1f}cm ({shoulder_pixel_dist:.0f}px)"
            else:
                distance_text = f"S: {shoulder_pixel_dist:.0f} px"
            cv2.putText(image, distance_text, (shoulder_mid_x - 60, shoulder_mid_y - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Get hip coordinates for waist measurement
            left_hip = results.pose_landmarks.landmark[self.LEFT_HIP]
            right_hip = results.pose_landmarks.landmark[self.RIGHT_HIP]
            
            # Convert hip coordinates to pixels
            left_hip_x = int(left_hip.x * width)
            left_hip_y = int(left_hip.y * height)
            right_hip_x = int(right_hip.x * width)
            right_hip_y = int(right_hip.y * height)
            
            # Draw line between hips (waist)
            cv2.line(image, (left_hip_x, left_hip_y), (right_hip_x, right_hip_y), (255, 165, 0), 3)  # Orange color
            
            # Draw hip points
            cv2.circle(image, (left_hip_x, left_hip_y), 8, (255, 100, 0), -1)
            cv2.circle(image, (right_hip_x, right_hip_y), 8, (255, 100, 0), -1)
            
            # Add hip labels
            cv2.putText(image, "LH", (left_hip_x - 25, left_hip_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(image, "RH", (right_hip_x + 10, right_hip_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Add waist distance measurement on the line
            waist_mid_x = (left_hip_x + right_hip_x) // 2
            waist_mid_y = (left_hip_y + right_hip_y) // 2
            
            # Calculate pixel distance for display
            waist_pixel_dist = self.calculate_pixel_distance(left_hip, right_hip, width, height)
            
            if waist_distance_cm:
                waist_text = f"W: {waist_distance_cm:.1f}cm ({waist_pixel_dist:.0f}px)"
            else:
                waist_text = f"W: {waist_pixel_dist:.0f} px"
            cv2.putText(image, waist_text, (waist_mid_x - 60, waist_mid_y + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
    
    def add_info_overlay(self, image, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, fps, confidence, scale_info, z_info=None):
        """
        Add information overlay to the image.
        """
        height, width = image.shape[:2]
        
        # Create info box background (make it taller for both measurements and z coordinate info)
        overlay = image.copy()
        cv2.rectangle(overlay, (10, 10), (520, 320), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        # Add text information
        y_offset = 35
        
        # Shoulder distance measurement
        if shoulder_cm:
            cv2.putText(image, f"Shoulder: {shoulder_cm:.1f} cm ({shoulder_pixels:.1f} px)", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
        else:
            cv2.putText(image, f"Shoulder Distance: {shoulder_pixels:.1f} pixels", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        y_offset += 30
        # Waist distance measurement
        if waist_cm:
            cv2.putText(image, f"Waist: {waist_cm:.1f} cm ({waist_pixels:.1f} px)", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 165, 0), 2)
        else:
            cv2.putText(image, f"Waist Distance: {waist_pixels:.1f} pixels", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 100), 2)
        
        y_offset += 25
        cv2.putText(image, f"Shoulder 3D: {shoulder_3d:.4f}", (20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        cv2.putText(image, f"Waist 3D: {waist_3d:.4f}", (250, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        
        # Z coordinate information
        if z_info:
            y_offset += 25
            cv2.putText(image, "--- Z Coordinates (Depth) ---", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 200, 255), 1)
            
            y_offset += 20
            cv2.putText(image, f"Shoulder Z: L={z_info['shoulder_left_z']:.3f} R={z_info['shoulder_right_z']:.3f}", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 255), 1)
            
            y_offset += 18
            cv2.putText(image, f"Waist Z: L={z_info['waist_left_z']:.3f} R={z_info['waist_right_z']:.3f}", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 165, 0), 1)
            
            y_offset += 18
            cv2.putText(image, f"Shoulder Z Diff: {z_info['shoulder_z_diff']:.4f}", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 255, 200), 1)
            
            y_offset += 18
            cv2.putText(image, f"Waist Z Diff: {z_info['waist_z_diff']:.4f}", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 100), 1)
            
            if z_info['shoulder_depth_cm'] or z_info['waist_depth_cm']:
                y_offset += 18
                shoulder_depth_text = f"{z_info['shoulder_depth_cm']:.1f}" if z_info['shoulder_depth_cm'] else "N/A"
                waist_depth_text = f"{z_info['waist_depth_cm']:.1f}" if z_info['waist_depth_cm'] else "N/A"
                cv2.putText(image, f"Depth (cm): S={shoulder_depth_text} W={waist_depth_text}", (20, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
        
        y_offset += 25
        cv2.putText(image, f"FPS: {fps:.1f}", (20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        y_offset += 20
        cv2.putText(image, f"Confidence: {confidence:.2f}", (20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        y_offset += 20
        cv2.putText(image, scale_info, (20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 255), 1)
        
        y_offset += 25
        if not shoulder_cm and not waist_cm:
            cv2.putText(image, "Press 'c' to calibrate, 'p' for preset (650px=96cm)", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        else:
            cv2.putText(image, "Press 'c' to recalibrate, 'p' preset, 'r' reset", (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        y_offset += 15
        cv2.putText(image, "Press 'q' to quit, 's' to save, 'z' toggle Z info", (20, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    def process_frame(self, image):
        """
        Process a single frame for pose detection and distance calculation.
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.pose.process(rgb_image)
        
        # Initialize return values
        shoulder_3d = 0.0
        shoulder_pixels = 0.0
        shoulder_cm = None
        waist_3d = 0.0
        waist_pixels = 0.0
        waist_cm = None
        confidence = 0.0
        scale_info = "No calibration"
        auto_scale = None
        z_info = None
        
        if results.pose_landmarks:
            # Get shoulder landmarks
            left_shoulder = results.pose_landmarks.landmark[self.LEFT_SHOULDER]
            right_shoulder = results.pose_landmarks.landmark[self.RIGHT_SHOULDER]
            
            # Get hip landmarks for waist measurement
            left_hip = results.pose_landmarks.landmark[self.LEFT_HIP]
            right_hip = results.pose_landmarks.landmark[self.RIGHT_HIP]
            
            # Calculate shoulder distances
            shoulder_3d = self.calculate_distance(left_shoulder, right_shoulder)
            shoulder_pixels = self.calculate_pixel_distance(
                left_shoulder, right_shoulder, image.shape[1], image.shape[0]
            )
            
            # Calculate waist distances
            waist_3d = self.calculate_distance(left_hip, right_hip)
            waist_pixels = self.calculate_pixel_distance(
                left_hip, right_hip, image.shape[1], image.shape[0]
            )
            
            # Calculate Z coordinate information for both shoulder and waist
            shoulder_left_z = left_shoulder.z
            shoulder_right_z = right_shoulder.z
            shoulder_z_diff = abs(shoulder_left_z - shoulder_right_z)
            shoulder_avg_depth = (shoulder_left_z + shoulder_right_z) / 2
            
            waist_left_z = left_hip.z
            waist_right_z = right_hip.z
            waist_z_diff = abs(waist_left_z - waist_right_z)
            waist_avg_depth = (waist_left_z + waist_right_z) / 2
            
            # Try to get automatic scale estimation
            auto_scale = self.get_automatic_scale(results.pose_landmarks, image.shape[1], image.shape[0])
            
            # Convert to centimeters
            shoulder_cm = self.pixels_to_cm(shoulder_pixels, auto_scale)
            waist_cm = self.pixels_to_cm(waist_pixels, auto_scale)
            
            # Convert depth to centimeters if we have calibration
            shoulder_depth_cm = None
            waist_depth_cm = None
            if self.pixels_per_cm:
                # Estimate depth in cm using the same scale factor
                shoulder_depth_cm = abs(shoulder_avg_depth) * self.pixels_per_cm * 100  # Rough estimation
                waist_depth_cm = abs(waist_avg_depth) * self.pixels_per_cm * 100  # Rough estimation
            elif auto_scale:
                shoulder_depth_cm = abs(shoulder_avg_depth) * auto_scale * 100  # Rough estimation
                waist_depth_cm = abs(waist_avg_depth) * auto_scale * 100  # Rough estimation
            
            # Create z coordinate info dictionary
            z_info = {
                'shoulder_left_z': shoulder_left_z,
                'shoulder_right_z': shoulder_right_z,
                'shoulder_z_diff': shoulder_z_diff,
                'shoulder_avg_depth': shoulder_avg_depth,
                'shoulder_depth_cm': shoulder_depth_cm,
                'waist_left_z': waist_left_z,
                'waist_right_z': waist_right_z,
                'waist_z_diff': waist_z_diff,
                'waist_avg_depth': waist_avg_depth,
                'waist_depth_cm': waist_depth_cm
            }
            
            # Update scale info
            if self.pixels_per_cm:
                if abs(self.pixels_per_cm - self.user_calibration) < 0.01:
                    scale_info = f"User calibration: {self.pixels_per_cm:.2f} px/cm (650px=96cm)"
                else:
                    scale_info = f"Manual calibration: {self.pixels_per_cm:.2f} px/cm"
            elif auto_scale:
                scale_info = f"Auto scale (face): {auto_scale:.1f} px/cm"
            else:
                scale_info = "No scale available"
            
            # Calculate average confidence of all landmarks
            confidence = (left_shoulder.visibility + right_shoulder.visibility + 
                         left_hip.visibility + right_hip.visibility) / 4
            
            # Draw landmarks and distance
            self.draw_landmarks_and_distance(image, results, shoulder_cm, waist_cm)
        
        return image, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, confidence, scale_info, z_info
    
    def run_webcam(self):
        """
        Run the shoulder distance calculator with webcam input.
        """
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Starting webcam. Controls:")
        print("- 'q': quit")
        print("- 's': save screenshot")
        print("- 'c': calibrate for real measurements")
        print("- 'p': use preset calibration (650px = 96cm)")
        print("- 'r': reset calibration")
        print("- 'z': toggle Z coordinate display")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            # Calculate FPS
            current_time = time.time()
            fps = 1 / (current_time - self.prev_time) if self.prev_time > 0 else 0
            self.prev_time = current_time
            
            # Process frame
            processed_frame, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, confidence, scale_info, z_info = self.process_frame(frame)
            
            # Add information overlay
            z_display = z_info if self.show_z_info else None
            self.add_info_overlay(processed_frame, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, fps, confidence, scale_info, z_display)
            
            # Display the frame
            cv2.imshow('Shoulder Distance Calculator', processed_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                timestamp = int(time.time())
                filename = f"shoulder_distance_{timestamp}.jpg"
                cv2.imwrite(filename, processed_frame)
                print(f"Screenshot saved as {filename}")
            elif key == ord('c'):
                # Calibration mode
                if confidence > 0.5:  # Only calibrate if pose is detected
                    pixels_per_cm = self.calibrate_with_reference(frame.copy(), 
                                                                processed_frame if confidence > 0 else None)
                else:
                    print("Please position yourself in the camera view before calibrating")
            elif key == ord('p'):
                # Use preset calibration
                self.save_calibration(self.user_calibration)
                print(f"✅ Applied preset calibration: 650px = 96cm ({self.user_calibration:.2f} px/cm)")
            elif key == ord('r'):
                # Reset calibration
                self.pixels_per_cm = None
                if os.path.exists(self.calibration_file):
                    os.remove(self.calibration_file)
                print("Calibration reset")
            elif key == ord('z'):
                # Toggle Z coordinate display
                self.show_z_info = not self.show_z_info
                status = "ON" if self.show_z_info else "OFF"
                print(f"Z coordinate display: {status}")
        
        cap.release()
        cv2.destroyAllWindows()
    
    def process_image(self, image_path, output_path=None):
        """
        Process a single image file.
        """
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load image {image_path}")
            return
        
        processed_image, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, confidence, scale_info, z_info = self.process_frame(image)
        
        # Add information overlay (show Z info by default for images)
        z_display = z_info if self.show_z_info else None
        self.add_info_overlay(processed_image, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, 0, confidence, scale_info, z_display)
        
        print(f"Shoulder distance (3D): {shoulder_3d:.4f}")
        print(f"Shoulder distance (pixels): {shoulder_pixels:.1f}")
        if shoulder_cm:
            print(f"Shoulder distance (cm): {shoulder_cm:.1f} ({shoulder_pixels:.1f} px)")
        
        print(f"Waist distance (3D): {waist_3d:.4f}")
        print(f"Waist distance (pixels): {waist_pixels:.1f}")
        if waist_cm:
            print(f"Waist distance (cm): {waist_cm:.1f} ({waist_pixels:.1f} px)")
            
        print(f"Confidence: {confidence:.2f}")
        print(f"Scale info: {scale_info}")
        
        # Print Z coordinate information
        if z_info:
            print(f"\nZ Coordinate Information:")
            print(f"Shoulder - Left Z: {z_info['shoulder_left_z']:.4f}, Right Z: {z_info['shoulder_right_z']:.4f}")
            print(f"Shoulder Z difference: {z_info['shoulder_z_diff']:.4f}")
            print(f"Waist - Left Z: {z_info['waist_left_z']:.4f}, Right Z: {z_info['waist_right_z']:.4f}")
            print(f"Waist Z difference: {z_info['waist_z_diff']:.4f}")
            if z_info['shoulder_depth_cm'] or z_info['waist_depth_cm']:
                shoulder_depth_text = f"{z_info['shoulder_depth_cm']:.1f}" if z_info['shoulder_depth_cm'] else "N/A"
                waist_depth_text = f"{z_info['waist_depth_cm']:.1f}" if z_info['waist_depth_cm'] else "N/A"
                print(f"Estimated depths (cm): Shoulder={shoulder_depth_text}, Waist={waist_depth_text}")
        
        if output_path:
            cv2.imwrite(output_path, processed_image)
            print(f"Output saved as {output_path}")
        else:
            cv2.imshow('Shoulder Distance Calculator', processed_image)
            print("Press 'c' to calibrate, 'p' for preset (650px=96cm), 'z' to toggle Z info, any other key to close")
            key = cv2.waitKey(0)
            if key == ord('c') and confidence > 0.5:
                self.calibrate_with_reference(image.copy(), processed_image if confidence > 0 else None)
            elif key == ord('p'):
                self.save_calibration(self.user_calibration)
                print(f"✅ Applied preset calibration: 650px = 96cm ({self.user_calibration:.2f} px/cm)")
            elif key == ord('z'):
                self.show_z_info = not self.show_z_info
                status = "ON" if self.show_z_info else "OFF"
                print(f"Z coordinate display: {status}")
                # Reprocess and redisplay
                z_display = z_info if self.show_z_info else None
                self.add_info_overlay(processed_image, shoulder_3d, shoulder_pixels, shoulder_cm, waist_3d, waist_pixels, waist_cm, 0, confidence, scale_info, z_display)
                cv2.imshow('Shoulder Distance Calculator', processed_image)
                cv2.waitKey(0)
            cv2.destroyAllWindows()

def main():
    """
    Main function to run the shoulder distance calculator.
    """
    calculator = ShoulderDistanceCalculator()
    
    print("MediaPipe Body Measurement Calculator")
    print("=====================================")
    print("✅ Real-world measurements in centimeters!")
    print("✅ Detailed Z-coordinate (depth) information!")
    print("✅ Both shoulder AND waist measurements!")
    print("✅ DEFAULT CALIBRATION: 650px = 96cm (active now!)")
    print("\nMeasurement features:")
    print("- 2D & 3D shoulder width")
    print("- 2D & 3D waist width")
    print("- Individual Z coordinates for all points")
    print("- Depth differences for posture analysis")
    print("- Real-world units (cm) with YOUR calibration")
    print("\nCalibration options:")
    print("1. YOUR CALIBRATION (650px = 96cm) - ACTIVE BY DEFAULT")
    print("2. Manual (use reference object) - Press 'c' to override")
    print("3. Reset to default - Press 'r' then 'p'")
    print("\nChoose mode:")
    print("1. Use webcam (default)")
    print("2. Process image file")
    
    choice = input("Enter your choice (1 or 2, default=1): ").strip()
    
    if choice == "2":
        image_path = input("Enter path to image file: ").strip()
        output_path = input("Enter output path (optional, press Enter to skip): ").strip()
        if not output_path:
            output_path = None
        calculator.process_image(image_path, output_path)
    else:
        calculator.run_webcam()

if __name__ == "__main__":
    main() 