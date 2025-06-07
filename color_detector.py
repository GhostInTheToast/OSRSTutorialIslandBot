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
from pynput import keyboard

# Set PyAutoGUI settings for safety
pyautogui.FAILSAFE = True  # Move mouse to corner to stop
pyautogui.PAUSE = 0.1  # Add small delay between actions

# Global variables for keyboard control
target_position = None
should_quit = False

def on_press(key):
    global target_position, should_quit
    try:
        if key.char == '1' and target_position:
            print("\n🎯 Moving mouse to target...")
            move_mouse_to_target(target_position[0], target_position[1], duration=0)
        elif key.char == 'q':
            should_quit = True
    except AttributeError:
        pass

def on_release(key):
    pass

# Start keyboard listener
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

def check_screen_permissions():
    """Check if we have screen recording permissions."""
    try:
        # Try to capture a small region of the screen
        pyautogui.screenshot(region=(0, 0, 1, 1))
        return True
    except Exception as e:
        print("\n❌ Screen recording permission not granted!")
        print("Please grant screen recording permission to your terminal/Python environment:")
        print("1. Open System Preferences")
        print("2. Go to Security & Privacy > Privacy > Screen Recording")
        print("3. Add your terminal application (Terminal.app or iTerm2)")
        print("4. Restart your terminal and try again")
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
    try:
        print("\n🔍 Starting window capture process...")
        
        # Define the region of interest
        roi_x1, roi_y1 = 343, 162  # Top-left corner
        roi_x2, roi_y2 = 861, 504  # Bottom-right corner
        roi_width = roi_x2 - roi_x1
        roi_height = roi_y2 - roi_y1
        print(f"🎯 ROI defined: ({roi_x1}, {roi_y1}) to ({roi_x2}, {roi_y2})")
        
        # Get screen size
        screen_width, screen_height = pyautogui.size()
        print(f"📐 Screen dimensions: {screen_width}x{screen_height}")
        
        # Check if ROI is within screen bounds
        if (roi_x1 < 0 or roi_y1 < 0 or 
            roi_x2 > screen_width or roi_y2 > screen_height):
            print(f"❌ ROI is outside screen bounds!")
            return None
            
        # Capture the region using PyAutoGUI
        print("📸 Capturing screen region...")
        screenshot = pyautogui.screenshot(region=(roi_x1, roi_y1, roi_width, roi_height))
        
        # Convert to numpy array and then to BGR format
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        print(f"✅ Successfully captured region, shape: {frame.shape}")
        
        return frame
        
    except Exception as e:
        print(f"\n⚠️  Unexpected error in capture_window: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def move_mouse_to_target(x, y, duration=0):
    """Move mouse instantly to target position."""
    try:
        # Move directly to target position
        pyautogui.moveTo(x, y, duration=0)
        # Double click at the position
        pyautogui.doubleClick()
        print(f"\rDouble clicked at position ({x}, {y})", end='')
        
    except Exception as e:
        print(f"\n⚠️  Error during mouse movement: {str(e)}")

def detect_red():
    global target_position, should_quit
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
    
    while not should_quit:
        try:
            # Capture the screen region
            frame = capture_window(None)
            
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
            max_area = 2  # Minimum area threshold
            
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
                center_x = x + w//2 + 343  # Add ROI offset
                center_y = y + h//2 + 162  # Add ROI offset
                target_position = (center_x, center_y)
                
                # Only print if position has changed significantly
                current_position = (x + 343, y + 162)  # Add ROI offset
                if last_position is None or abs(current_position[0] - last_position[0]) > 5 or abs(current_position[1] - last_position[1]) > 5:
                    print(f"\rLargest red object: area={max_area:.1f}, position=({current_position[0]}, {current_position[1]}), size={w}x{h}", end='')
                    last_position = current_position
            
            # Show the result
            cv2.imshow('2004Scape Game - Red Color Detection', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        except Exception as e:
            print(f"\n⚠️  Error during screen capture: {str(e)}")
            print("Make sure you have granted screen recording permissions!")
            break
    
    cv2.destroyAllWindows()
    listener.stop()

if __name__ == "__main__":
    print("🔍 2004Scape Game Red Color Detection Tool")
    print("=======================================")
    
    if not check_screen_permissions():
        exit(1)
        
    print("\n⏳ Starting in 3 seconds...")
    time.sleep(3)
    detect_red() 