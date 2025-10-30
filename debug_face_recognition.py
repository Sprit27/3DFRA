#!/usr/bin/env python3
"""
Debug script for face recognition issues
"""
import os
import pickle
import sqlite3
from datetime import datetime

def check_face_encodings():
    """Check if face encodings file exists and is readable"""
    encodings_file = "face_encodings.pkl"
    
    if not os.path.exists(encodings_file):
        print("❌ face_encodings.pkl does not exist")
        return False
    
    try:
        with open(encodings_file, "rb") as f:
            known_faces = pickle.load(f)
        
        print(f"✅ Face encodings file loaded successfully")
        print(f"   - Number of stored faces: {len(known_faces.get('names', []))}")
        print(f"   - Stored names: {known_faces.get('names', [])}")
        print(f"   - Number of encodings: {len(known_faces.get('encodings', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Error loading face encodings: {e}")
        return False

def check_database():
    """Check database tables and data"""
    db_file = "info2.db"
    
    if not os.path.exists(db_file):
        print("❌ Database file info2.db does not exist")
        return False
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check people table
        cursor.execute("SELECT COUNT(*) FROM people")
        people_count = cursor.fetchone()[0]
        print(f"✅ People table has {people_count} records")
        
        if people_count > 0:
            cursor.execute("SELECT name, unique_number FROM people")
            people = cursor.fetchall()
            print("   Registered people:")
            for name, uno in people:
                print(f"     - {name} (ID: {uno})")
        
        # Check monthly attendance table
        monthly_table = datetime.now().strftime("%Y_%m")
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{monthly_table}"')
            monthly_count = cursor.fetchone()[0]
            print(f"✅ Monthly attendance table ({monthly_table}) has {monthly_count} records")
        except sqlite3.OperationalError:
            print(f"⚠️  Monthly attendance table ({monthly_table}) does not exist")
        
        # Check daily attendance table
        daily_table = datetime.now().strftime("%Y_%m_%d")
        try:
            cursor.execute(f'SELECT COUNT(*) FROM "{daily_table}"')
            daily_count = cursor.fetchone()[0]
            print(f"✅ Daily attendance table ({daily_table}) has {daily_count} records")
            
            if daily_count > 0:
                cursor.execute(f'SELECT unique_number, session_date FROM "{daily_table}"')
                records = cursor.fetchall()
                print("   Today's attendance:")
                for uno, date in records:
                    print(f"     - ID {uno} at {date}")
                    
        except sqlite3.OperationalError:
            print(f"⚠️  Daily attendance table ({daily_table}) does not exist")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_webcam():
    """Check if webcam is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Webcam is accessible and working")
                print(f"   Frame size: {frame.shape}")
            else:
                print("❌ Webcam opened but cannot read frames")
            cap.release()
            return ret
        else:
            print("❌ Cannot open webcam")
            return False
            
    except Exception as e:
        print(f"❌ Webcam error: {e}")
        return False

def test_face_recognition():
    """Test face recognition with existing data"""
    try:
        import face_recognition
        import numpy as np
        
        encodings_file = "face_encodings.pkl"
        if not os.path.exists(encodings_file):
            print("❌ No face encodings to test with")
            return False
        
        with open(encodings_file, "rb") as f:
            known_faces = pickle.load(f)
        
        if len(known_faces["encodings"]) == 0:
            print("❌ No face encodings stored")
            return False
        
        print(f"✅ Face recognition library working")
        print(f"   Testing with {len(known_faces['encodings'])} stored faces")
        
        # Test encoding comparison (self-comparison should be very close to 0)
        if len(known_faces["encodings"]) >= 2:
            distance = face_recognition.face_distance([known_faces["encodings"][0]], known_faces["encodings"][1])[0]
            print(f"   Sample distance between different faces: {distance:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Face recognition test error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debugging Face Recognition System")
    print("=" * 50)
    
    print("\n1. Checking face encodings...")
    check_face_encodings()
    
    print("\n2. Checking database...")
    check_database()
    
    print("\n3. Checking webcam...")
    check_webcam()
    
    print("\n4. Testing face recognition...")
    test_face_recognition()
    
    print("\n" + "=" * 50)
    print("Debug complete!")