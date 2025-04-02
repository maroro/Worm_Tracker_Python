import sys
import time
import numpy as np
from MovingAvg import MovingAvg
import cv2


def binary_threshold(camera_manager, frame):
    tracking_tab_settings = camera_manager.tracking_tab_settings
    threshold = tracking_tab_settings["threshold"]
    square_size = tracking_tab_settings["square_size"]
    bright_bkg = tracking_tab_settings["brightfield"]
    erode_iter = tracking_tab_settings["erode"]
    dilate_iter = tracking_tab_settings["dilate"]
    current_position = None

    # define the type of binary threshold based on the type of imaging
    if bright_bkg:
        threshold_type = cv2.THRESH_BINARY_INV
    else:
        threshold_type = cv2.THRESH_BINARY

    # convert to grayscale if the frame is in RGB. this is necessary to binarize
    if len(frame.shape) > 2:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # binarize image and find the biggest "contours" i.e. the worm in the image
    _, binary_frame = cv2.threshold(frame, threshold, 255, threshold_type)

    # create a kernel (small matrix) that will be used to scan image and erode or dilate white objects
    # bigger kernels allows the transformation to be more dramatic
    kernel = np.ones((3, 3), np.uint8)  # Define a 3x3 kernel for morphology operation
    # Apply erosion
    if erode_iter > 0:
        binary_frame = cv2.erode(binary_frame, kernel, iterations=erode_iter)
    # Apply dilation
    if dilate_iter > 0:
        binary_frame = cv2.dilate(binary_frame, kernel, iterations=dilate_iter)

    contours, _ = cv2.findContours(binary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)  # Get bounding box

        # Define square ROI using sqr_half_width
        cx, cy = x + w // 2, y + h // 2  # Compute object center
        x1, y1 = max(0, cx - square_size), max(0, cy - square_size)
        x2, y2 = min(frame.shape[1], cx + square_size), min(frame.shape[0], cy + square_size)

        # Update position tracking
        current_position = (cx, cy)

        # Draw rectangle around detected object
        cv2.rectangle(binary_frame, (x1, y1), (x2, y2), 255, 2)
        cv2.circle(binary_frame, (cx, cy), 5, 255, -1)  # Mark the center

    return binary_frame, current_position

def run_calibration(camera_manager):
    # Stage moves 10 microns in each direction
    stage_moves = [
        (10, 0),  # Right
        (0, 10),  # Up
        (-10, 0),  # Left
        (0, -10),  # Down
    ]

    real_world = []
    pixel_shifts = []

    # Get initial object position
    init_pos = camera_manager.current_position
    if init_pos is None:
        print("Error: could not find object for calibration.")
        return

    print(f"Initial position: {init_pos}")

    for dx_um, dy_um in stage_moves:
        # Move stage
        camera_manager.primary_core.setRelativeXYPosition(dx_um, dy_um)
        time.sleep(0.3)  # Allow time (300ms) for movement and image to update
        #get the latest image
        img = camera_manager.primary_core.popNextImage()
        _, new_pos = binary_threshold(camera_manager, img)
        # Get new position
        if new_pos is None:
            print("Warning: object lost during calibration step.")
            continue

        shift_x = new_pos[0] - init_pos[0]
        shift_y = new_pos[1] - init_pos[1]

        print(f"Stage moved: ({dx_um}, {dy_um}) → pixel shift: ({shift_x:.2f}, {shift_y:.2f})")

        real_world.append([dx_um, dy_um])
        pixel_shifts.append([shift_x, shift_y])

        # Move stage back before next step
        core.setRelativeXYPosition(-dx_um, -dy_um)
        time.sleep(0.3)

    # Solve linear system: R = P × C → C = (P^T P)^-1 P^T R
    if len(real_world) < 2:
        print("Calibration failed — not enough valid points.")
        return

    R = np.array(real_world)  # shape (N, 2)
    P = np.array(pixel_shifts)  # shape (N, 2)

    # Solve for correction matrix: C = np.linalg.lstsq(P, R)
    C, _, _, _ = np.linalg.lstsq(P, R, rcond=None)

    # Unpack matrix into settings
    XXcorr, XYcorr = C[0]
    YXcorr, YYcorr = C[1]

    tracking_settings["xx"] = XXcorr
    tracking_settings["xy"] = XYcorr
    tracking_settings["yx"] = YXcorr
    tracking_settings["yy"] = YYcorr

"""
This functions take in the current and previous positions which are calculated position as inputs. In addition,
we inout values that can be used to correct the speed of the motorized stage. since the calculations are done based on 
the movement of the worm in pixels, but the stage receives inputs in the form of um/s, then we need to convert movement
from pixel to um and then add corrections in cases the orientation of the camera does not match the orientation 
of the stage movement.
"""
def update_vectors(camera_manager, x_vector, y_vector, dx, dy):
    current_position = camera_manager.current_position
    last_position = camera_manager.last_position
    scale = camera_manager.tracking_tab_settings["scale"]
    if current_position is not None and last_position is not None:
        # Compute displacement from th center of our image
        new_dx = (camera_manager.img_width/2) - current_position[0]
        new_dy = (camera_manager.img_height/2) - current_position[1]
        dx.update(new_dx)
        dy.update(new_dy)

        # Convert pixel shift to stage movement using calibration factors
        xx = camera_manager.tracking_tab_settings.get("xx")
        xy = camera_manager.tracking_tab_settings.get("xy")
        yx = camera_manager.tracking_tab_settings.get("yx")
        yy = camera_manager.tracking_tab_settings.get("yy")
        gain = camera_manager.tracking_tab_settings.get("gain")

        #calculate movement vectors and scale them based on gain
        # we multiply by scale to adjust the movement as the displacement is calculated inn pixels,
        # but the vector to the stage is assumed to be microns.
        new_x_vector = (dx.get_average() * xx + dy.get_average() * xy) * gain * scale
        new_y_vector = (dx.get_average() * yx + dy.get_average() * yy) * gain * scale
        x_vector.update(new_x_vector)
        y_vector.update(new_y_vector)

        # we use the calculated object displacement to define the relative x, y coordinates.
        # this is different than setXYPosition because it doesn't move the stage to a fixed point.
        # instead, it only tells the stage to move in a given direction
        #camera_manager.primary_core.setRelativeXYPosition(x_move, y_move)
""" 
the goal of this function is to take the x and y velocity vectors and use them them to 
move the motorized staged based on object position
"""
def move_stage(self, x_vector, y_vector):
    """Moves the motorized stage based on computed XY velocity vectors."""
    try:
        # Ensure motion is within speed limits
        max_speed = 7 #Adjust based on hardware limits
        x_vector = max(-max_speed, min(max_speed, x_vector))
        y_vector = max(-max_speed, min(max_speed, y_vector))

        # Apply stage movement
        self.primary_core.setRelativeXYPosition(x_vector, y_vector)
        print(f"Moving stage: X={x_vector}, Y={y_vector}")

    except Exception as e:
        print(f"Stage movement failed: {e}")