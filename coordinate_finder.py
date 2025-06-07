import cv2
import numpy as np
import pyautogui
import time

def find_coordinates():
    print("\n🎯 Coordinate Finder Tool")
    print("=========================")
    print("1. Move your mouse to the area you want to capture")
    print("2. Press 'c' to capture the coordinates")
    print("3. Press 'q' to quit")
    
    # Create a window to show the coordinates
    cv2.namedWindow('Coordinate Finder')
    
    while True:
        # Get current mouse position
        x, y = pyautogui.position()
        
        # Create a blank image
        img = np.zeros((100, 300, 3), dtype=np.uint8)
        
        # Add text with coordinates
        cv2.putText(img, f'X: {x}, Y: {y}', (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show the image
        cv2.imshow('Coordinate Finder', img)
        
        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            print(f"\n✅ Captured coordinates: X={x}, Y={y}")
        elif key == ord('q'):
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("⏳ Starting in 3 seconds...")
    time.sleep(3)
    find_coordinates() 