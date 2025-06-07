import cv2
import numpy as np
import pyautogui
import time
import sys
import os
import pygetwindow as gw
from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
    CGWindowListCreateImage,
    CGRectNull,
    kCGWindowListOptionIncludingWindow,
    CGImageGetDataProvider,
    CGDataProviderCopyData,
    CGImageGetWidth,
    CGImageGetHeight,
    CGImageGetBytesPerRow,
    CGImageGetBitsPerPixel,
    CGMainDisplayID,
    CGDisplayCreateImage,
    CGRectMake
)

# Set PyAutoGUI settings for safety
pyautogui.FAILSAFE = True  # Move mouse to corner to stop
pyautogui.PAUSE = 0.1  # Add small delay between actions

def check_screen_permissions():
    """Check if we have screen recording permissions"""
    try:
        # Try to capture a small portion of the screen
        test_capture = pyautogui.screenshot(region=(0, 0, 100, 100))
        return True
    except Exception as e:
        print("\n⚠️  Screen Recording Permission Required!")
        print("Please follow these steps:")
        print("1. Go to System Preferences > Security & Privacy > Privacy > Screen Recording")
        print("2. Click the lock icon to make changes (you'll need to enter your password)")
        print("3. Find Terminal or your IDE in the list and check the box next to it")
        print("4. Restart Terminal or your IDE after granting permissions")
        print("\nError details:", str(e))
        return False

def get_chrome_window():
    """Get the Chrome window information."""
    window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
    for window in window_list:
        if window.get('kCGWindowOwnerName', '') == 'Google Chrome':
            # Get window bounds
            bounds = window.get('kCGWindowBounds', {})
            if bounds:
                return {
                    'x': int(bounds['X']),
                    'y': int(bounds['Y']),
                    'width': int(bounds['Width']),
                    'height': int(bounds['Height'])
                }
    return None

def capture_window(window_info):
    """Capture the content of the specified window."""
    if window_info is None:
        return None
        
    try:
        # Capture the screen region
        screenshot = pyautogui.screenshot(region=(
            window_info['x'],
            window_info['y'],
            window_info['width'],
            window_info['height']
        ))
        
        # Convert to numpy array
        frame = np.array(screenshot)
        
        # Convert from RGB to BGR (OpenCV format)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        return frame
        
    except Exception as e:
        print(f"\n⚠️  Error capturing window: {str(e)}")
        return None

def move_mouse_to_target(x, y, duration=1.0):
    """Move mouse to target position smoothly, pixel by pixel."""
    try:
        # Get current mouse position
        current_x, current_y = pyautogui.position()
        
        # Calculate total distance
        total_distance = ((x - current_x) ** 2 + (y - current_y) ** 2) ** 0.5
        
        # Calculate number of steps (1 pixel per step)
        steps = int(total_distance)
        
        # Calculate time per step
        time_per_step = duration / steps if steps > 0 else 0
        
        # Move mouse pixel by pixel
        for i in range(steps + 1):
            # Calculate intermediate position
            intermediate_x = current_x + (x - current_x) * (i / steps)
            intermediate_y = current_y + (y - current_y) * (i / steps)
            
            # Move to intermediate position
            pyautogui.moveTo(intermediate_x, intermediate_y)
            time.sleep(time_per_step)
            
        # Double click at the final position
        pyautogui.doubleClick()
        print(f"\rDouble clicked at position ({x}, {y})", end='')
        
    except Exception as e:
        print(f"\n⚠️  Error during mouse movement: {str(e)}")

def detect_red():
    # Define the region of interest
    roi_x1, roi_y1 = 343, 162  # Top-left corner
    roi_x2, roi_y2 = 861, 504  # Bottom-right corner
    roi_width = roi_x2 - roi_x1
    roi_height = roi_y2 - roi_y1

    # Define the lower and upper bounds for red color in HSV
    # Red wraps around in HSV, so we need two ranges
    lower_red1 = np.array([0, 100, 100])  # Lower saturation threshold
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 100])  # Lower saturation threshold
    upper_red2 = np.array([180, 255, 255])

    print("\n🎯 Starting red color detection...")
    print(f"Monitoring region: ({roi_x1}, {roi_y1}) to ({roi_x2}, {roi_y2})")
    print("Press 'q' to stop the program")
    print("Press '1' to move mouse to the largest red object")
    print("The window will show the 2004Scape game window with green boxes around red objects")
    
    last_position = None
    target_position = None
    
    while True:
        try:
            # Capture the screen region
            frame = capture_window({
                'x': roi_x1,
                'y': roi_y1,
                'width': roi_width,
                'height': roi_height
            })
            
            if frame is None:
                print("⚠️  Failed to capture window content")
                break
            
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create masks for both red ranges
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            
            # Combine the masks
            mask = cv2.bitwise_or(mask1, mask2)
            
            # Debug: Show the mask
            cv2.imshow('Red Mask', mask)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest red object
            largest_contour = None
            max_area = 50  # Minimum area threshold
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > max_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    # Get the average HSV value in this region
                    roi_hsv = hsv[y:y+h, x:x+w]
                    avg_hsv = np.mean(roi_hsv, axis=(0,1))
                    # Only consider if it's actually red (high saturation)
                    if avg_hsv[1] > 50:  # Check saturation
                        max_area = area
                        largest_contour = (x, y, w, h, avg_hsv)
            
            # Draw rectangle only for the largest red object
            if largest_contour:
                x, y, w, h, avg_hsv = largest_contour
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Calculate center point of the box
                center_x = x + w//2 + roi_x1
                center_y = y + h//2 + roi_y1
                target_position = (center_x, center_y)
                
                # Only print if position has changed significantly
                current_position = (x + roi_x1, y + roi_y1)
                if last_position is None or abs(current_position[0] - last_position[0]) > 5 or abs(current_position[1] - last_position[1]) > 5:
                    print(f"\rLargest red object: area={max_area:.1f}, position=({x + roi_x1}, {y + roi_y1}), size={w}x{h}", end='')
                    last_position = current_position
            
            # Show the result
            cv2.imshow('2004Scape Game - Red Color Detection', frame)
            
            # Check for key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('1') and target_position:
                print("\n🎯 Moving mouse to target...")
                move_mouse_to_target(target_position[0], target_position[1])
                
        except Exception as e:
            print(f"\n⚠️  Error during screen capture: {str(e)}")
            print("Make sure you have granted screen recording permissions!")
            break
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    print("🔍 2004Scape Game Red Color Detection Tool")
    print("=======================================")
    
    if not check_screen_permissions():
        sys.exit(1)
        
    print("\n⏳ Starting in 3 seconds...")
    time.sleep(3)
    detect_red() 