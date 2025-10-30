# Installation Guide for Python 3.12.6

## Quick Installation

### Step 1: Install basic requirements
```bash
pip install -r requirements.txt
```

### Step 2: Install dlib and face-recognition (Choose one method)

#### Method A: Using conda (Recommended for Python 3.12)
```bash
conda install -c conda-forge dlib
pip install face-recognition
```

#### Method B: Using pre-compiled wheels
```bash
# For Windows
pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.24.0-cp312-cp312-win_amd64.whl
pip install face-recognition
```

#### Method C: Build from source (if other methods fail)
```bash
# Install build dependencies first
pip install cmake
pip install dlib --no-cache-dir
pip install face-recognition
```

## Platform-Specific Notes

### Windows
- Install Visual Studio Build Tools if building from source
- Use conda method for easiest installation

### macOS
```bash
# Install Homebrew dependencies
brew install cmake
brew install dlib
pip install face-recognition
```

### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev

# Then install Python packages
pip install dlib
pip install face-recognition
```

## Verification

Test your installation:
```python
import cv2
import face_recognition
import numpy as np
import flask
import webview
print("All libraries imported successfully!")
```

## Troubleshooting

### If dlib installation fails:
1. Try the conda method first
2. Use pre-compiled wheels for your platform
3. Install Visual Studio Build Tools (Windows) or build-essential (Linux)
4. Consider using Python 3.11 if 3.12 compatibility issues persist

### Alternative: Use face-recognition-models
If face-recognition doesn't work, you can use:
```bash
pip install face-recognition-models
```