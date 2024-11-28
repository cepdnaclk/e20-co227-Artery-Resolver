import sys
import cv2
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import Tk, Frame, Scrollbar, Canvas, simpledialog, Scrollbar, Label, filedialog, Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Frame, Label, Canvas, Scrollbar, StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

heights_per_second = []  # Stores heights for each second
heights_data = []  # Stores the average height data per second

partiotion_no = 10
pixel_difference_threshold = 20

# Global variables
drawing = False
rectangle_selected = False
ix, iy = -1, -1
points = []
original_dimensions = None
predicted_lines = None

# Global variables for line and height calculation
line_start = None
line_end = None
line_drawn = False
actual_height = None
height_per_pixel = None
is_drawing_mode = False
is_dragging = False

TARGET_HEIGHT = 720
TARGET_WIDTH = 1280

# Function to handle mouse events for drawing a vertical line with dragging
def draw_vertical_line(event, x, y, flags, param):
    global line_start, line_end, line_drawn, is_dragging

    if event == cv2.EVENT_LBUTTONDOWN:
        if not line_drawn:
            # Start drawing the line if not drawn yet
            line_start = (x, y)
            line_end = (x, y)  # Initialize end point to the starting point
            is_dragging = True  # Start dragging the line
        else:
            # If line is already drawn, check if the user clicked near the start or end of the line
            # This will allow dragging either end of the line
            if abs(x - line_start[0]) < 10 and abs(y - line_start[1]) < 10:
                is_dragging = "start"  # Dragging the start point
            elif abs(x - line_end[0]) < 10 and abs(y - line_end[1]) < 10:
                is_dragging = "end"  # Dragging the end point

    elif event == cv2.EVENT_MOUSEMOVE and is_dragging:
        if is_dragging == "start":
            # Update the start point, keeping the x-coordinate fixed
            line_start = (line_start[0], y)
        elif is_dragging == "end":
            # Update the end point, keeping the x-coordinate fixed
            line_end = (line_end[0], y)

    elif event == cv2.EVENT_LBUTTONUP:
        # Finalize the line when the mouse button is released
        if not line_drawn:
            line_end = (line_start[0], y)  # Keep the line vertical
            line_drawn = True  # Set flag to indicate the line is drawn
        is_dragging = False  # Stop dragging

# Drawing function to visualize the line on the frame
def draw_line_on_frame(frame):
    if line_start is not None and line_end is not None:
        cv2.line(frame, line_start, line_end, (255, 0, 0), 2)  # Draw the vertical line

    return frame

# Function to set actual height using a dialog
def set_actual_height():
    global actual_height
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    while True:
        # Ask for actual height input
        actual_height = simpledialog.askfloat("Input", "Enter the actual height (in mm):", minvalue=0.0)
        print(actual_height)
        
        if actual_height is not None:  # Check if user pressed 'Cancel'
            print(f"Actual height set to: {actual_height} mm")
            break  # Exit the loop if input is valid
        else:
            print("Input canceled. Please enter a valid numeric value.")

    root.destroy()  # Destroy the Tkinter root window after use

# Function to process the vertical line and calculate pixel-to-height ratio
def calculate_height_per_pixel():
    global line_start, line_end, actual_height
    
    if line_start and line_end and actual_height is not None:
        pixel_height = abs(line_end[1] - line_start[1])  # y-coordinates
        height_per_pixel = actual_height / pixel_height if pixel_height != 0 else None
        print(f"Height per pixel: {height_per_pixel} mm/pixel")
        return height_per_pixel
    else:
        print("Line not drawn or actual height not set.")
        return None

# Mouse callback function for drawing the rectangle
def rectangle_drawing(event, x, y, flags, param):
    global ix, iy, drawing, points, rectangle_selected, original_dimensions, frame_copy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        points = [(x, y)]  # Start point of the rectangle

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            # Copy the original frame to reset it before drawing
            frame_copy = frame.copy()
            points = [(ix, iy), (x, y)]  # Update rectangle endpoint as mouse moves
            # Draw the rectangle on the frame copy (for visual feedback)
            cv2.rectangle(frame_copy, points[0], points[1], (0, 255, 0), 2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if ix != x and iy != y:  # Ensure the rectangle is not a single point
            rectangle_selected = True
            original_dimensions = (abs(x - ix), abs(y - iy))  # Store original width and height
            print(f"DEBUG: Rectangle points - Top-left: {points[0]}, Bottom-right: {points[1]}")


def process_rectangle_and_draw_lines(frame):
    global predicted_lines

    # Ensure a rectangle has been selected
    if not rectangle_selected:
        print("DEBUG: No rectangle selected, skipping processing.")
        return None

    # Validate points of the rectangle
    print(f"DEBUG: Points of the rectangle: {points}")
    x1, x2 = min(points[0][0], points[1][0]), max(points[0][0], points[1][0])
    y1, y2 = min(points[0][1], points[1][1]), max(points[0][1], points[1][1])

    # Check rectangle boundaries
    if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
        return None

    # Ensure rectangle dimensions are valid
    if (x2 - x1) <= 0 or (y2 - y1) <= 0:
        return None

    # Extract the selected region
    selected_region = frame[y1:y2, x1:x2]

    # Convert the selected region to grayscale
    selected_region = cv2.cvtColor(selected_region, cv2.COLOR_BGR2GRAY)

    # Check for an empty region
    if selected_region.size == 0:
        return None

    # Calculate partition width
    partition_width = (x2 - x1) // partiotion_no
    if partition_width <= 0:
        return None

    # Initialize line coordinates storage
    line_coordinates = []

    # Iterate through each partition
    for i in range(partiotion_no):
        start_x = x1 + i * partition_width
        center_x = start_x + partition_width // 2
        center_y = (y1 + y2) // 2

        # Adjust center_x and center_y for the selected region
        center_x_selected = center_x - x1
        center_y_selected = center_y - y1

        # Validate center points within the selected region's bounds
        if center_x_selected < 0 or center_x_selected >= selected_region.shape[1] or center_y_selected < 0 or center_y_selected >= selected_region.shape[0]:
            continue

        print(f"DEBUG: Processing partition {i+1}: Center ({center_x_selected}, {center_y_selected})")

        # Search upwards
        for y in range(center_y_selected, 0, -1):
            if 0 <= y - 1 < selected_region.shape[0] and 0 <= center_x_selected < selected_region.shape[1]:
                pixel_1 = int(selected_region[y, center_x_selected])  # Using the grayscale region
                pixel_2 = int(selected_region[y - 1, center_x_selected])  # Using the grayscale region
                diff = abs(pixel_1 - pixel_2)
                if diff >= pixel_difference_threshold:
                    upper_y = y - 1
                    break

        # Search downwards
        for y in range(center_y_selected, selected_region.shape[0]):
            if 0 <= y + 1 < selected_region.shape[0] and 0 <= center_x_selected < selected_region.shape[1]:
                pixel_1 = int(selected_region[y, center_x_selected])  # Using the grayscale region
                pixel_2 = int(selected_region[y + 1, center_x_selected])  # Using the grayscale region
                diff = abs(pixel_1 - pixel_2)
                if diff >= pixel_difference_threshold:
                    lower_y = y + 1
                    break

        # Store the line coordinates if valid
        if upper_y is not None and lower_y is not None:
            line_coordinates.append(((center_x, upper_y), (center_x, lower_y)))
            print(f"DEBUG: Line coordinates - Upper: ({center_x}, {upper_y}), Lower: ({center_x}, {lower_y})")
        else:
            print(f"DEBUG: Skipping partition {i+1} due to missing upper or lower points.")

    # Store the predicted lines globally
    predicted_lines = line_coordinates

    # Calculate height of each line (difference between upper and lower y)
    heights = [abs(line[1][1] - line[0][1]) for line in line_coordinates]

    # Compute average height
    average_height = np.mean(heights) if heights else 0
    print(f"DEBUG: Average height: {average_height}")

    # Define a margin (10%) around the average height
    margin_percentage = 0.05
    lower_limit = average_height - (average_height * margin_percentage)
    upper_limit = average_height + (average_height * margin_percentage)

    print(f"DEBUG: Filtering lines with height within {lower_limit} and {upper_limit} pixels.")

    # Filter out lines where the height is outside the defined range (too short or too tall)
    filtered_line_coordinates = [
        line for line in line_coordinates
        if lower_limit <= abs(line[1][1] - line[0][1]) <= upper_limit
    ]

    # Calculate height of each line (difference between upper and lower y) after filtering
    filtered_heights = [abs(line[1][1] - line[0][1]) for line in filtered_line_coordinates]

    # Compute average height for the filtered lines
    average_height2 = np.mean(filtered_heights) if filtered_heights else 0
    print(f"DEBUG: Average height after filtering: {average_height2}")

    # Store the filtered lines
    predicted_lines = filtered_line_coordinates

    # Calculate heights for each filtered line
    num_points = len(filtered_line_coordinates)
    heights = [abs(line[1][1] - line[0][1]) for line in filtered_line_coordinates]

    # Compute average pixel height for filtered lines
    average_pixel_height = np.mean(heights) if heights else 0
    print(f"DEBUG: Total filtered lines: {num_points}")
    print(f"DEBUG: Heights of filtered lines: {heights}")
    print(f"DEBUG: Average pixel height for filtered lines: {average_pixel_height}")

    return average_pixel_height


# Main execution starts here
if __name__ == "__main__":
    print("Starting video processing...")
    if len(sys.argv) < 2:
        print("Please provide the video path as a command-line argument.")
        sys.exit()

    video_path = sys.argv[1]

    # Load and display the video
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Unable to open video.")
        sys.exit()

    # Read the first frame for user input
    ret, first_frame = cap.read()
    if not ret:
        print("Error: Unable to read the first frame.")
        cap.release()
        sys.exit()

    frame = cv2.resize(first_frame, (TARGET_WIDTH, TARGET_HEIGHT))

    # Display the first frame and wait for user to draw the line
    cv2.imshow("First Frame", frame)
    cv2.setMouseCallback("First Frame", draw_vertical_line) 

    # Wait for user input
    while True:
        # Create a copy of the first frame for drawing
        frame_copy = frame.copy()  
        
        if is_drawing_mode:
            draw_line_on_frame(frame_copy)  # Draw the line if in drawing mode

        cv2.imshow("First Frame", frame_copy)  # Show the frame (with line if in drawing mode)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('h'):  # Start drawing the line
            is_drawing_mode = True
            print("Line drawing mode activated. Draw a vertical line and press 'c' to confirm.")
        elif key == ord('c') and is_drawing_mode:  # Confirm the line
            print("Line confirmed.")
            is_drawing_mode = False  # Reset drawing mode
            set_actual_height()  # Prompt for the actual height
            height_per_pixel = calculate_height_per_pixel()  # Calculate height per pixel
            print(height_per_pixel)
            break
        elif key == 27:  # ESC key to exit
            print("Exiting...")
            cv2.destroyAllWindows()
            cap.release()
            sys.exit(0)

    cv2.destroyAllWindows()

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps / 10)  # Process 10 frames per second
    frame_delay = int(1000 / 60)  # Maintain 30fps playback (in milliseconds)

    # Display the first frame and wait for the user to draw the line
    cv2.imshow("Select Rectangle", first_frame)
    cv2.setMouseCallback("Select Rectangle", rectangle_drawing)

    frame = cv2.resize(first_frame, (TARGET_WIDTH, TARGET_HEIGHT))
    print(f"Height per pixel: {height_per_pixel} mm/pixel")

    # Wait for the user to select a rectangle
    while True:
        temp_frame = frame.copy()  # Make a copy of the frame to refresh it each time

        # Draw the selected rectangle only on the temporary frame
        if len(points) == 2:
            cv2.rectangle(temp_frame, points[0], points[1], (0, 255, 0), 2)  # Green rectangle

        # Display the temporary frame with the current rectangle
        cv2.imshow("Select Rectangle", temp_frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
            print("Exiting...")
            cv2.destroyAllWindows()
            cap.release()
            sys.exit(0)

        elif rectangle_selected:
            break

    cv2.destroyAllWindows()
    print(points)

    # After rectangle is selected, process video frames
    frame_count = 0
    second_counter = 1
    # height_per_pixel = calculate_height_per_pixel()
    # print(f"Height per pixel 2: {height_per_pixel} cm/pixel")

    # heights_per_second = []
    # heights_data = []

    # Main loop
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if rectangle_selected:
            frame = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
            
            # Draw the rectangle on each frame
            cv2.rectangle(frame, points[0], points[1], (0, 255, 0), 2)  # Green rectangle

            # Process every 3rd frame (i.e., 10 frames per second from 30fps)
            if frame_count % frame_interval == 0:
                # Process the selected region for height and draw lines
                average_height = process_rectangle_and_draw_lines(frame)
                if average_height is not None:
                    heights_per_second.append(average_height)

                    # After capturing 10 frames, compute the average height for the second
                    if len(heights_per_second) == 10:
                        avg_height_per_second = np.mean(heights_per_second)
                        print(f"Second {second_counter}: Average pixel height = {avg_height_per_second}")

                        # Store the average height data for the second
                        heights_data.append({
                            'Second': second_counter,
                            'Average Height': round(avg_height_per_second * height_per_pixel, 3)
                        })

                        # Reset heights_per_second for the next set of 10 frames
                        heights_per_second = []
                        second_counter += 1

            # Draw blue and green points for upper and lower points separately
            if predicted_lines is not None:
                # Convert points to integer
                line_points = predicted_lines

                # Draw blue points for the upper points
                for point in line_points:
                    upper_point = point[0]  # Get the upper point (x, y)
                    center_x_selected, center_y_selected = upper_point
                    # Adjust coordinates back to the full frame
                    center_x_full = center_x_selected 
                    center_y_full = center_y_selected + iy
                    # Draw a blue circle at each upper point in the full frame
                    cv2.circle(frame, (center_x_full, center_y_full), radius=3, color=(255, 0, 0), thickness=-1)  # Blue for upper point

                # Draw green points for the lower points
                for point in line_points:
                    lower_point = point[1]  # Get the lower point (x, y)
                    center_x_selected, center_y_selected = lower_point
                    # Adjust coordinates back to the full frame
                    center_x_full = center_x_selected
                    center_y_full = center_y_selected + iy
                    # Draw a green circle at each lower point in the full frame
                    cv2.circle(frame, (center_x_full, center_y_full), radius=3, color=(255, 0, 0), thickness=-1)  # Green for lower point

                # Display the current frame with the rectangle and points
                cv2.imshow("Processed Video", frame)

                frame_count += 1

                # Delay to simulate 30fps playback even though only 10 frames are processed
                if cv2.waitKey(frame_delay) & 0xFF == 27:  # ESC key to exit
                    break


    #cv2.destroyAllWindows()
    

    # If heights data is available, show in Tkinter
# Function to save the table data
def save_table_data():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        title="Save Table Data"
    )
    if file_path:
        try:
            with open(file_path, "w") as file:
                # Write table headers
                headers = heights_data[0].keys()
                file.write("\t".join(headers) + "\n")
                # Write table rows
                for row in heights_data:
                    file.write("\t".join(str(row[key]) for key in row.keys()) + "\n")
            print(f"Data saved successfully to {file_path}")
        except Exception as e:
            print(f"Error saving data: {e}")

# If heights data is available, show in Tkinter
if len(heights_data) > 0:
    root = tk.Tk()
    root.title("Heights Information")

    # Table Frame
    table_frame = Frame(root, bg='white')
    table_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

    scrollbar = Scrollbar(table_frame)
    scrollbar.pack(side="right", fill="y")

    canvas = Canvas(table_frame, yscrollcommand=scrollbar.set, bg='white')
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar.config(command=canvas.yview)

    # Create an inner frame for the table
    table_frame_inner = Frame(canvas, bg='white')
    canvas.create_window((0, 0), window=table_frame_inner, anchor="nw")

    # Add table headers
    for i, (key, value) in enumerate(heights_data[0].items()):
        Label(
            table_frame_inner,
            text=f"{key}",
            borderwidth=2,
            relief="groove",
            width=20,
            bg='lightgray',
            font=("Arial", 10, "bold")
        ).grid(row=0, column=i, sticky="nsew")

    # Add table data
    for row, data in enumerate(heights_data):
        for col, key in enumerate(data):
            Label(
                table_frame_inner,
                text=f"{data[key]}",
                borderwidth=2,
                relief="groove",
                width=20,
                bg='white',
                font=("Arial", 10)
            ).grid(row=row + 1, column=col, sticky="nsew")

    # Configure the inner frame to fill the available space
    table_frame_inner.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Set up resizing behavior for the frame and canvas
    table_frame.columnconfigure(0, weight=1)
    table_frame.rowconfigure(0, weight=1)
    canvas.pack(fill="both", expand=True)

    # Add Save Button below the Canvas
    save_button = Button(table_frame, text="Save Data", command=save_table_data, bg="lightblue", font=("Arial", 10, "bold"))
    save_button.pack(pady=10)

    # Graph Frame
    graph_frame = Frame(root, bg='black')
    graph_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

    # Matplotlib figure and plot with black background
    fig, ax = plt.subplots(figsize=(10, 8), dpi=100, facecolor='black')
    seconds = [data['Second'] for data in heights_data]
    avg_heights = [data['Average Height'] for data in heights_data]

    ax.plot(seconds, avg_heights, label='Average Height', marker='o', color='cyan')
    ax.set_xlabel("Second", color='white')
    ax.set_ylabel("Average Diameter (mm)", color='white')
    ax.legend()

    # Set black background for axes
    ax.set_facecolor('black')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    # Embed the plot in Tkinter
    canvas_graph = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas_graph.draw()
    canvas_graph.get_tk_widget().pack(fill="both", expand=True)

    # Function to handle click events on the chart
    selected_value = StringVar(value="Selected Point: None")

    def on_click(event):
        if event.inaxes is not None:
            # Find nearest point on the graph
            x_data, y_data = event.xdata, event.ydata
            nearest_x = min(seconds, key=lambda x: abs(x - x_data))
            nearest_index = seconds.index(nearest_x)
            nearest_y = avg_heights[nearest_index]
            selected_value.set(f"Selected Point: Second = {nearest_x}, Average Height = {nearest_y:.2f} mm")

    # Connect click event to the graph
    canvas_graph.mpl_connect('button_press_event', on_click)

    # Display the selected value on the GUI
    selected_value_label = Label(graph_frame, textvariable=selected_value, bg='black', fg='white', font=("Arial", 12))
    selected_value_label.pack(pady=10)

    # Calculate and display minimum and maximum heights
    min_height = np.min(avg_heights)
    max_height = np.max(avg_heights)
    height_summary = f"Minimum Height: {min_height:.2f} mm, Maximum Height: {max_height:.2f} mm"
    height_summary_label = Label(graph_frame, text=height_summary, bg='black', fg='white', font=("Arial", 12))
    height_summary_label.pack(pady=10)

    root.mainloop()