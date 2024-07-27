from AppKit import NSApplication, NSWorkspace, NSWindow, NSImage
import AppKit
import Quartz
from Quartz.CoreGraphics import CGWindowListCopyWindowInfo, kCGNullWindowID, kCGWindowListOptionAll
import Quartz.CoreGraphics as CG
import time
import pytesseract
from PIL import Image
import pdb
import cv2
import numpy as np 
import os

REFRESH_FUNC = (380, 1000)
CONFIRM_FUNC = (1050, 700)
BUY_FUNC = (1050, 800)
DRAG_FUNC = (1500, 1000, 1500, 650)
WINDOW_NAME = "Epic Seven"
windowId = None

def image(source_image):
    source_image = np.array(source_image)
    source_image = cv2.cvtColor(source_image, cv2.COLOR_BGR2RGB)
    source_image = cv2.cvtColor(source_image, cv2.COLOR_BGR2GRAY)
    source_image = cv2.threshold(source_image, 127, 255, cv2.THRESH_TOZERO)
    source_image = np.array(source_image[1])
    return source_image

def click_mouse(x, y):
    # Create a CGEvent for mouse down at (x, y)
    mouse_event = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDown, (x, y), Quartz.kCGMouseButtonLeft)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, mouse_event)
    
    # Create a CGEvent for mouse up at (x, y)
    mouse_event = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseUp, (x, y), Quartz.kCGMouseButtonLeft)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, mouse_event)

def drag_mouse(start_x, start_y, end_x, end_y, duration=0.3):
    # Create a CGEvent for mouse down at (start_x, start_y)
    mouse_event = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDown, (start_x, start_y), Quartz.kCGMouseButtonLeft)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, mouse_event)

    # Calculate the number of steps for the drag
    steps = 100
    step_x = (end_x - start_x) / steps
    step_y = (end_y - start_y) / steps
    step_duration = duration / steps

    # Drag the mouse in small steps to the end point
    for i in range(steps):
        new_x = start_x + (step_x * i)
        new_y = start_y + (step_y * i)
        mouse_event = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseDragged, (new_x, new_y), Quartz.kCGMouseButtonLeft)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, mouse_event)
        time.sleep(step_duration)

    # Create a CGEvent for mouse up at (end_x, end_y)
    mouse_event = Quartz.CGEventCreateMouseEvent(None, Quartz.kCGEventLeftMouseUp, (end_x, end_y), Quartz.kCGMouseButtonLeft)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, mouse_event)


def capture_window(window_name):
    window_list = CG.CGWindowListCopyWindowInfo(CG.kCGWindowListOptionOnScreenOnly, CG.kCGNullWindowID)
    for window in window_list:
        if window.get('kCGWindowOwnerName') == window_name:
            window_id = window['kCGWindowNumber']
            bounds = window['kCGWindowBounds']
            image = CG.CGWindowListCreateImage(
                CG.CGRectMake(
                    bounds['X'], 
                    bounds['Y'], 
                    bounds['Width'], 
                    bounds['Height']
                ),
                CG.kCGWindowListOptionIncludingWindow,
                window_id,
                CG.kCGWindowImageDefault
            )
            bitmap = AppKit.NSBitmapImageRep.alloc().initWithCGImage_(image)
            jpeg_data = bitmap.representationUsingType_properties_(AppKit.NSJPEGFileType, None)
            with open('screenshot.jpg', 'wb') as f:
                f.write(jpeg_data)
            print(f'Screenshot saved as screenshot.jpg')
            break
    else:
        print(f'No window found with the name {window_name}') 

def detect_object():
    img = cv2.imread('screenshot.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    specific_texts = ["Covenant", "Mystic"]

    # Perform OCR on the image
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    # Print out the results
    coordinates = []
    for i in range(len(data['text'])):
        detected_text = data['text'][i].strip()
        if detected_text in specific_texts:
            x, y, width, height = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            print(f"Text: {detected_text}\nCoordinates: ({x}, {y}, {width}, {height})\n")
            coordinates.append((x, y, width, height))  
    return coordinates


def buy(coordinates):
    for i in range(len(coordinates)):
        coordinate = coordinates[i]
        click_mouse(coordinate[0]+700, coordinate[1]+50)
        time.sleep(0.5)
        click_mouse(*BUY_FUNC)
        time.sleep(0.5)
while True:
    activeAppName = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
    time.sleep(0.5)
    if activeAppName == WINDOW_NAME:
        capture_window(WINDOW_NAME)
        coordinates = detect_object()
        buy(coordinates)

        drag_mouse(*DRAG_FUNC)
        time.sleep(1)

        capture_window(WINDOW_NAME)
        coordinates = detect_object()
        buy(coordinates)

        click_mouse(*REFRESH_FUNC)
        time.sleep(0.8)
        click_mouse(*CONFIRM_FUNC)
    print(activeAppName)