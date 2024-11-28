import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog
import math
import sys

# Global variables for drawing the ROI and line
pt1, pt2, roi_start, roi_end = (0, 0), (0, 0), (0, 0), (0, 0)
drawing = False
roi_selected = False
line_selected = False
selecting_roi = True

# Calibration variables
calibration_mode = None
x_line_start, x_line_end = None, None
y_line_start, y_line_end = None, None
time_period = None
flow_amount = None
drawing = False

# List to store the calibration data [pixel_length, defined_length]
calibration_data = []
T_factor=None
Flow_factor=None

resolution = [1280,720]

def draw_roi_and_line(event, x, y, flags, param):
    global pt1, pt2, roi_start, roi_end, drawing, roi_selected, line_selected, selecting_roi
    
    if selecting_roi:  # First, select ROI
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            roi_start = (x, y)
            roi_end = (x, y)
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                frame_copy = frame.copy()
                roi_end = (x, y)
                cv2.rectangle(frame_copy, roi_start, roi_end, (255, 0, 0), 2)
                cv2.imshow("Select ROI and Line", frame_copy)
        
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            roi_end = (x, y)
            
            # Ensure ROI is top-left to bottom-right
            x1, y1 = min(roi_start[0], roi_end[0]), min(roi_start[1], roi_end[1])
            x2, y2 = max(roi_start[0], roi_end[0]), max(roi_start[1], roi_end[1])
            roi_start, roi_end = (x1, y1), (x2, y2)
            
            roi_selected = True
            selecting_roi = False
            cv2.rectangle(frame, roi_start, roi_end, (255, 0, 0), 2)  # Final ROI rectangle
            cv2.imshow("Select ROI and Line", frame)
    
    else:  # After ROI is selected, move to line selection
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            pt1 = (x, y)
            pt2 = (x, y)
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                frame_copy = frame.copy()
                cv2.rectangle(frame_copy, roi_start, roi_end, (255, 0, 0), 2)  # Keep ROI visible
                pt2 = (x, y)
                cv2.line(frame_copy, pt1, pt2, (0, 0, 255), 2)  # Draw red line
                cv2.imshow("Select ROI and Line", frame_copy)
        
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            pt2 = (x, y)
            line_selected = True
            cv2.line(frame, pt1, pt2, (0, 0, 255), 2)  # Final line
            cv2.imshow("Select ROI and Line", frame)

# Function to process a given frame and calculate height differences
def process_frame2(frame, roi, scale_factor):
    # Crop the frame to the selected ROI
    roi_frame = frame[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]

    # Convert the ROI frame to grayscale
    gray_input = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)

    # Apply a binary threshold to isolate the curve
    _, binary_image = cv2.threshold(gray_input, 50, 255, cv2.THRESH_BINARY)

    # Apply Canny edge detection to detect edges
    edges = cv2.Canny(binary_image, 50, 150)

    # Create a mask for the selected line within the ROI
    mask = np.ones(gray_input.shape[:2], dtype="uint8") * 255
    line_start = (pt1[0] - roi[0], pt1[1] - roi[1])
    line_end = (pt2[0] - roi[0], pt2[1] - roi[1])
    cv2.line(mask, line_start, line_end, 0, 5)  # Draw the line on the mask

    # Mask out the line in the edges
    edges_masked = cv2.bitwise_and(edges, edges, mask=mask)

    # Find contours on the masked edges
    contours, _ = cv2.findContours(edges_masked, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Baseline (y-coordinate of the drawn line)
    baseline_y = pt1[1] - roi[1]

    # Initialize dictionaries to store topmost and bottommost points for each column
    topmost_points = {}
    bottommost_points = {}

    for contour in contours:
        for point in contour:
            x, y = point[0]
            
            if x not in topmost_points:
                topmost_points[x] = y
            else:
                topmost_points[x] = min(topmost_points[x], y)
            
            if x not in bottommost_points:
                bottommost_points[x] = y
            else:
                bottommost_points[x] = max(bottommost_points[x], y)

    # Calculate the height differences with respect to the baseline (drawn line)
    height_diffs = {}

    for x in topmost_points.keys():
        if x in bottommost_points:
            height_up = (baseline_y - topmost_points[x])
            height_down = -(bottommost_points[x] - baseline_y)
            height_diffs[x] = height_up + height_down

    # Draw contours on the original frame
    output_frame = frame.copy()
    cv2.drawContours(output_frame[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]], contours, -1, (0, 255, 0), 2)  # Green contours
    cv2.rectangle(output_frame, roi_start, roi_end, (255, 0, 0), 2)  # Blue rectangle for ROI
    cv2.line(output_frame, pt1, pt2, (0, 0, 255), 2)  # Red line (excluded from detection but still drawn)

    return output_frame, height_diffs


video_path = sys.argv[1]  # Update with your video file path
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Set video frame size to 720x1280
cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

#if not cap.isOpened():
    #print("Error: Could not open video.")
   # exit()

# Function to calculate the pixel distance between two points
def calculate_pixel_length(start_point, end_point):
    return math.sqrt((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2)

# Function to get user input for time period and flow amount
def get_user_input():
    global time_period, flow_amount
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    # Ask for time period input
    time_period = simpledialog.askfloat("Input", "Enter known time period (in seconds):", minvalue=0.0)
    
    # Ask for flow amount input
    flow_amount = simpledialog.askfloat("Input", "Enter known flow amount (in cm/s):", minvalue=0.0)
    
    root.destroy()

# Mouse callback to handle the drawing of lines
def draw_calibration_line(event, x, y, flags, param):
    global x_line_start, x_line_end, y_line_start, y_line_end, calibration_mode, drawing,T_factor,Flow_factor

    if event == cv2.EVENT_LBUTTONDOWN:  # Start drawing
        drawing = True
        if calibration_mode == 'X-axis':
            x_line_start = (x, y)
        elif calibration_mode == 'Y-axis':
            y_line_start = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:  # Update the end point as mouse moves
        if calibration_mode == 'X-axis' and x_line_start:
            x_line_end = (x, x_line_start[1])  # Constrain Y to draw horizontal line
        elif calibration_mode == 'Y-axis' and y_line_start:
            y_line_end = (y_line_start[0], y)  # Constrain X to draw vertical line

    elif event == cv2.EVENT_LBUTTONUP:  # Finish drawing
        drawing = False
        if calibration_mode == 'X-axis':
            x_line_end = (x, x_line_start[1])
            # Calculate the pixel length of the X-axis
            x_pixel_length = calculate_pixel_length(x_line_start, x_line_end)
            # Store the data: [pixel_length, defined_length (time period)]
            calibration_data.append([x_pixel_length, time_period])
            T_factor=(time_period/x_pixel_length)
            print(f"X-axis Calibration: Pixel Length = {x_pixel_length}, Defined Time = {time_period} sec")

        elif calibration_mode == 'Y-axis':
            y_line_end = (y_line_start[0], y)
            # Calculate the pixel length of the Y-axis
            y_pixel_length = calculate_pixel_length(y_line_start, y_line_end)
            # Store the data: [pixel_length, defined_length (flow amount)]
            calibration_data.append([y_pixel_length, flow_amount])
            Flow_factor=flow_amount/y_pixel_length

            print(f"Y-axis Calibration: Pixel Length = {y_pixel_length}, Defined Flow = {flow_amount} cm/s")

# Function to process each frame
def process_frame(frame):
    frame_height, frame_width, _ = frame.shape

    # Draw X-axis and Y-axis calibration lines
    if x_line_start and x_line_end:
        cv2.line(frame, x_line_start, x_line_end, (255, 0, 0), 2)  # Horizontal line for X-axis
        # Display the exact user input time period on the X-axis
        cv2.putText(frame, f'Time: {time_period:.2f} sec', (x_line_start[0], x_line_start[1] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    if y_line_start and y_line_end:
        cv2.line(frame, y_line_start, y_line_end, (0, 255, 0), 2)  # Vertical line for Y-axis
        # Display the exact user input flow amount on the Y-axis
        cv2.putText(frame, f'Flow: {flow_amount:.2f} cm/s', (y_line_start[0] + 10, y_line_start[1]), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return frame

# Get user inputs for time period and flow amount
get_user_input()

cv2.namedWindow('Doppler Video')
cv2.setMouseCallback('Doppler Video', draw_calibration_line)

ret, first_frame = cap.read()
if ret:

    # Show the first frame for calibration
    while True:
        # Resize the frame to fit into the display
        resized_frame = cv2.resize(first_frame, (resolution[0],resolution[1]))

        # Process frame for calibration
        frame = process_frame(resized_frame.copy())

        # Display the frame
        cv2.imshow('Doppler Video', frame)

        # Handle key inputs
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):  # Quit the video
            break
        elif key == ord('x'):  # Enter X-axis calibration mode
            calibration_mode = 'X-axis'
            print("X-axis Calibration Mode: Click and drag horizontally")
        elif key == ord('y'):  # Enter Y-axis calibration mode
            calibration_mode = 'Y-axis'
            print("Y-axis Calibration Mode: Click and drag vertically")

# Clean up when done
cv2.destroyAllWindows()

# Read the first frame to allow ROI and line selection
ret, frame = cap.read()
if not ret:
    print("Error: Could not read the first frame.")
    cap.release()
    exit()

# Create a window and set the mouse callback for selecting ROI and line
cv2.namedWindow("Select ROI and Line", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Select ROI and Line", draw_roi_and_line)

print("Select ROI, then draw a line and press 'Enter' when done.")

while True:
    # Display the frame
    cv2.imshow("Select ROI and Line", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 13 and roi_selected and line_selected:  # Enter key to finalize ROI and line selection
        break

cv2.destroyAllWindows()

# Get the ROI coordinates
roi = (roi_start[0], roi_start[1], roi_end[0] - roi_start[0], roi_end[1] - roi_start[1])

# Initialize variables for frame processing and time tracking
fps = int(cap.get(cv2.CAP_PROP_FPS))
frames_per_second = fps
frame_count = 0
total_height_diffs = []
start_time = time.time()



# Prepare for real-time plotting
plt.ion()  # Interactive mode
fig, ax = plt.subplots()
line_plot, = ax.plot([], [], label='Average Height Variation', color='blue')
ax.set_xlabel('Horizontal Distance (x)')
ax.set_ylabel('Average Height Difference (pixels)')
ax.set_title('Height Variation with Horizontal Distance (x)')
ax.grid(True)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Skip processing every 5th frame
    #frame_skip = 5  # Process every 5th frame
    #if frame_count % frame_skip != 0:
        #frame_count += 1  # Increment frame count even if skipping
        #continue  # Skip this frame

    # Process the frame to detect contours and calculate height differences
    processed_frame, height_diffs = process_frame2(frame, roi, 1)  # Assuming scale_factor is 1 for simplicity

    # Accumulate height differences across all frames within 1 second
    total_height_diffs.append(height_diffs)
    frame_count += 1

    # Display the processed frame with contours, line, and ROI box
    cv2.imshow("Contours Detection", processed_frame)

    # Update the graph with the current frame's height differences
    avg_height_diffs = {}
    for height_diff in total_height_diffs:
        for x, height in height_diff.items():
            if x not in avg_height_diffs:
                avg_height_diffs[x] = []
            avg_height_diffs[x].append(height)
        
        # Calculate the average for each x-coordinate
        avg_height_diffs = {x: np.mean(heights) for x, heights in avg_height_diffs.items()}

        # Convert average height differences (pixels) to flow rates (cm/s)
        avg_flow_rates = {x: height * Flow_factor for x, height in avg_height_diffs.items()}

 
        # Plot the flow rates instead of pixel height differences
        x_coords = sorted(avg_flow_rates.keys())
        flow_values = [avg_flow_rates[x] for x in x_coords]
        
        line_plot.set_data(x_coords, flow_values)
        ax.set_xlim(min(x_coords), max(x_coords))
        ax.set_ylim(min(flow_values) - 10, max(flow_values) + 10)
        ax.set_ylabel('Flow Rate (cm/s)')  # Update the y-axis label to show flow rates
        plt.pause(0.001)  # Pause for the plot to update

        # Reset the variables for the next second
        total_height_diffs = []
        start_time = time.time()

    # Wait for 25ms between frames, press 'q' to quit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()