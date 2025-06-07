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
    CGImageGetBitsPerPixel
)

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
    """Get the position and size of the Chrome window"""
    try:
        print("\n🔍 Searching for windows...")
        # Get window information using Quartz
        window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
        
        print(f"Found {len(window_list)} windows:")
        for window in window_list:
            if 'kCGWindowName' in window:
                print(f"- {window['kCGWindowName']}")
        
        # Find the 2004Scape window (not the detection window)
        for window in window_list:
            if 'kCGWindowName' in window and '2004Scape Game' in window['kCGWindowName'] and 'Red Color Detection' not in window['kCGWindowName']:
                print(f"\n✅ Found matching window: {window['kCGWindowName']}")
                try:
                    # Get window bounds and window ID
                    bounds = window.get('kCGWindowBounds', {})
                    window_id = window.get('kCGWindowNumber', 0)
                    if bounds:
                        x = int(bounds.get('X', 0))
                        y = int(bounds.get('Y', 0))
                        width = int(bounds.get('Width', 0))
                        height = int(bounds.get('Height', 0))
                        print(f"Window details: left={x}, top={y}, width={width}, height={height}, id={window_id}")
                        return {
                            'left': x, 
                            'top': y, 
                            'width': width, 
                            'height': height,
                            'id': window_id
                        }
                            
                except Exception as e:
                    print(f"⚠️  Error getting window object: {str(e)}")
                    return None
        
        print("\n⚠️  Chrome window not found!")
        print("Please make sure the 2004Scape game window is open and visible.")
        return None
            
    except Exception as e:
        print(f"\n⚠️  Error finding Chrome window: {str(e)}")
        return None

def capture_window(window_info):
    """Capture only the specific window's content"""
    try:
        # Create a CGRect for the window
        rect = CGRectNull
        
        # Calculate aspect ratio
        aspect_ratio = window_info['width'] / window_info['height']
        print(f"Target aspect ratio: {aspect_ratio:.2f}")
        
        # Capture the window content using its ID
        image = CGWindowListCreateImage(
            rect,
            kCGWindowListOptionIncludingWindow,
            window_info['id'],
            kCGWindowListOptionOnScreenOnly
        )
        
        if image:
            # Get image properties
            width = CGImageGetWidth(image)
            height = CGImageGetHeight(image)
            bytes_per_row = CGImageGetBytesPerRow(image)
            bits_per_pixel = CGImageGetBitsPerPixel(image)
            
            print(f"Raw capture dimensions: {width}x{height}")
            
            # Get the image data
            data_provider = CGImageGetDataProvider(image)
            data = CGDataProviderCopyData(data_provider)
            
            # Convert to numpy array
            frame = np.frombuffer(data, dtype=np.uint8).reshape(height, bytes_per_row // 4, 4)
            # Crop to actual width (remove padding)
            frame = frame[:, :width, :]
            
            # Calculate new height based on aspect ratio
            new_height = int(window_info['width'] / aspect_ratio)
            print(f"Calculated new height: {new_height}")
            
            # Resize to match the window's original dimensions while maintaining aspect ratio
            frame = cv2.resize(frame, (window_info['width'], new_height), 
                             interpolation=cv2.INTER_LINEAR)
            
            print(f"Final dimensions: {frame.shape[1]}x{frame.shape[0]}")
            
            # Convert from RGBA to BGR (fix color channels)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            return frame
    except Exception as e:
        print(f"⚠️  Error capturing window: {str(e)}")
        print("Debug info:")
        print(f"Window info: {window_info}")
        print(f"Captured dimensions: {width}x{height}")
        print(f"Expected dimensions: {window_info['width']}x{window_info['height']}")
    return None

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
    print("The window will show the 2004Scape game window with green boxes around red objects")
    
    last_position = None
    
    while True:
        try:
            # Get Chrome window
            window_info = get_chrome_window()
            if window_info is None:
                break
                
            # Capture only the window content
            frame = capture_window(window_info)
            if frame is None:
                print("⚠️  Failed to capture window content")
                break
            
            # Extract the region of interest
            roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
            
            # Convert to HSV
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
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
                cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Only print if position has changed significantly
                current_position = (x + roi_x1, y + roi_y1)
                if last_position is None or abs(current_position[0] - last_position[0]) > 5 or abs(current_position[1] - last_position[1]) > 5:
                    print(f"\rLargest red object: area={max_area:.1f}, position=({x + roi_x1}, {y + roi_y1}), size={w}x{h}", end='')
                    last_position = current_position
            
            # Show the result
            cv2.imshow('2004Scape Game - Red Color Detection', frame)
            
            # Check for 'q' key press to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
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