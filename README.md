# MediaPipe Shoulder Distance Calculator

A Python project that uses Google's MediaPipe library to detect human pose landmarks in real-time and calculate the distance between shoulders **in centimeters**.

## 🆕 NEW Features

- **Real-world measurements in centimeters/meters**
- **Automatic calibration** using facial features
- **Manual calibration** with reference objects
- **Persistent calibration** (saves your settings)

## Features

- Real-time pose detection using webcam
- Calculates shoulder distance in **centimeters** (not just pixels!)
- Live visualization with distance overlay
- Two calibration methods: automatic (face-based) and manual (reference object)
- Error handling for cases when pose is not detected
- Works with both webcam and static images
- Saves calibration settings for future use

## Requirements

- Python 3.7+
- Webcam or video input device (for real-time mode)

## Installation

1. Clone or download this project
2. Install the required dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

### Quick Test
Run the test script to verify installation:
```bash
python3 test_image.py
```

### Webcam Mode (Real-time)
```bash
python3 shoulder_distance.py
```
**Note:** On macOS/Windows, you'll be prompted to allow camera access the first time.

### Image Processing Mode
```bash
python3 shoulder_distance.py
```
Then choose option 2 and provide an image path.

### Quick Demo
```bash
python3 demo.py
```

## 📏 Calibration for Real Measurements

### Automatic Calibration
- The app automatically estimates scale using your facial features
- Uses average eye distance (≈6.3cm) as reference
- Works when your face is visible to the camera
- No manual input required!

### Manual Calibration
1. Press **'c'** during webcam mode or image viewing
2. Choose a reference object with known size:
   - Credit card: 8.5cm wide
   - Ruler: any measurement
   - Coin, phone, etc.
3. Click two points on the object in the image
4. Enter the real-world distance
5. Calibration is automatically saved!

### Calibration Controls
- **'c'** - Start calibration
- **'r'** - Reset calibration
- Settings are saved in `calibration.json`

## Camera Permissions

### macOS
- The first time you run the webcam mode, macOS will ask for camera permission
- Go to System Preferences > Security & Privacy > Camera if you need to manually grant access
- The app needs to be authorized to access your camera

### Windows
- Windows may show a camera permission dialog
- Make sure your antivirus isn't blocking camera access

## Controls

- **'q'** - Quit the application
- **'s'** - Save screenshot with distance measurement
- **'c'** - Calibrate for real measurements
- **'r'** - Reset calibration
- Make sure you're well-lit and facing the camera for best results

## How it Works

1. **Pose Detection**: Uses MediaPipe's pose estimation model to detect 33 key body landmarks
2. **Shoulder Identification**: Extracts left shoulder (landmark 11) and right shoulder (landmark 12) coordinates
3. **Distance Calculation**: Computes 3D Euclidean distance between shoulder points
4. **Scale Conversion**: Converts pixel measurements to centimeters using:
   - Automatic facial feature calibration (preferred)
   - Manual reference object calibration
5. **Visualization**: Displays the live video feed with pose landmarks and distance measurement overlay

## Shoulder Landmarks

The project specifically uses these MediaPipe pose landmarks:
- Left Shoulder: Index 11
- Right Shoulder: Index 12

Additional landmarks for automatic calibration:
- Eyes: Index 1 (left) and 4 (right) - for scale estimation
- Ears: Index 7 (left) and 8 (right) - backup scale estimation

## Output

The application displays:
- **Shoulder distance in centimeters** (main measurement)
- Live video feed with pose landmarks
- Real-time distance overlay on the shoulder line
- Confidence score for pose detection
- FPS counter (in webcam mode)
- Calibration status

## 💡 Tips for Best Results

### Lighting & Positioning
- Ensure good lighting
- Face the camera directly
- Make sure your full upper body is visible
- Stand at an appropriate distance from the camera

### Calibration Tips
- For automatic calibration: keep your face visible and well-lit
- For manual calibration: use flat objects (credit cards work great)
- Calibrate once - settings are saved automatically
- Recalibrate if you change camera distance significantly

## Troubleshooting

### Camera Issues
- **"Could not open webcam"**: Check camera permissions and make sure no other app is using the camera
- **"Not authorized to capture video"**: Grant camera access in system settings

### Installation Issues
- Make sure you're using Python 3.7+
- Try `python3` instead of `python`
- Use `pip3` instead of `pip` on macOS/Linux

### No Pose Detected
- Ensure good lighting
- Face the camera directly
- Make sure your full upper body is visible
- Stand at an appropriate distance from the camera

### Measurement Issues
- **No centimeter measurements**: Try automatic calibration (show your face) or manual calibration (press 'c')
- **Inaccurate measurements**: Recalibrate or try different reference object
- **Inconsistent results**: Ensure stable lighting and camera position

## File Structure

```
mediapipe body/
├── README.md              # This documentation
├── requirements.txt       # Python dependencies  
├── shoulder_distance.py   # Main application with cm measurements
├── demo.py               # Quick demo script
├── test_image.py         # Test without camera
├── calibration.json      # Saved calibration settings (auto-generated)
└── .gitignore            # Git ignore patterns
```

## Example Results

After calibration, you'll see measurements like:
- **Shoulder Distance: 42.3 cm**
- Scale: Auto calibration (face): 8.2 px/cm
- Confidence: 0.94

This gives you accurate, real-world measurements instead of just pixel distances! 