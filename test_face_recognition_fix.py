#!/usr/bin/env python3
"""
Test script to verify face recognition data type fix
"""
import cv2
import numpy as np
import face_recognition

def test_webcam_face_recognition():
    """Test if webcam face recognition works without errors"""
    print("Testing webcam face recognition...")
    
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        return False
    
    # Set properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("✅ Webcam opened successfully")
    
    # Test frame capture and processing
    for i in range(5):  # Test 5 frames
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Failed to read frame {i+1}")
            continue
        
        print(f"Frame {i+1}: shape={frame.shape}, dtype={frame.dtype}")
        
        # Process frame like in the main application
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        rgb_small_frame = np.ascontiguousarray(rgb_small_frame, dtype=np.uint8)
        
        print(f"  Processed: shape={rgb_small_frame.shape}, dtype={rgb_small_frame.dtype}")
        
        try:
            # Test face detection
            face_locations = face_recognition.face_locations(rgb_small_frame)
            print(f"  Found {len(face_locations)} faces")
            
            # Test face encoding (only if faces found)
            if face_locations:
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                print(f"  Generated {len(face_encodings)} encodings")
                print("✅ Face recognition working correctly")
            else:
                print("  No faces detected (normal if no one in frame)")
                
        except Exception as e:
            print(f"❌ Face recognition error: {e}")
            cap.release()
            return False
    
    cap.release()
    print("✅ All tests passed!")
    return True

def test_image_face_recognition():
    """Test face recognition with a test image"""
    print("\nTesting image face recognition...")
    
    # Create a simple test image (black with white rectangle - not a real face)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(test_image, (200, 150), (440, 330), (255, 255, 255), -1)
    
    # Convert to RGB
    rgb_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB)
    rgb_image = np.ascontiguousarray(rgb_image, dtype=np.uint8)
    
    try:
        face_locations = face_recognition.face_locations(rgb_image)
        print(f"✅ Face detection on test image: {len(face_locations)} faces")
        
        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            print(f"✅ Face encoding on test image: {len(face_encodings)} encodings")
        
        return True
    except Exception as e:
        print(f"❌ Image face recognition error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Face Recognition Fixes")
    print("=" * 50)
    
    # Test image processing first (safer)
    test_image_face_recognition()
    
    # Test webcam (requires camera)
    test_webcam_face_recognition()
    
    print("\n" + "=" * 50)
    print("Test complete!")