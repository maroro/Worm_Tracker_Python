import pymmcore_plus
import napari
from qtpy.QtCore import QTimer
import time
import numpy as np
import os
from functools import partial
from binary_tracker import *

"""Normalize images of different bit depths to 8-bit (0-255)."""
def normalize_to_8bit(img):
    img = img.astype(np.float32)  # Convert to float for safe scaling
    img_min, img_max = img.min(), img.max()

    if img_max - img_min > 0:
        img = 255 * ((img - img_min) / (img_max - img_min))
    else:
        img = np.zeros_like(img)  # If all pixels are the same, return black image
    return img.astype(np.uint8)


""" 
This function initiates a live from the tracking camera based on user inputs of exposure and fps.
It returns an image that cna be passed onto the layer_1 of the napari viewer
"""
def tracking_start_live(camera_manager, layer_1):
    print("starting tracking updater")
    while camera_manager.primary_core.getRemainingImageCount() == 0:
        print("no frame loaded")
        time.sleep(0.01)  # Small delay to allow frames to arrive

    if camera_manager.primary_core.getRemainingImageCount() > 0:  # Ensure there's a new frame
        # this generates a tuple where the first element the next frame in
        # the circular buffer, removing it and allowing is to work with it
        while camera_manager.primary_core.getRemainingImageCount() > 1:

            camera_manager.primary_core.popNextImage()

    img_1 = camera_manager.primary_core.popNextImage()

    if img_1 is None or img_1.size == 0:
        print("Error: No image data received from camera.")
        return  # Exit to prevent passing None to Napari

    # since MM produces the image in the form of a fattened array (1D),
    # we need to reshape it to a 2D array that can be "seen" as an image
    img_1 = img_1.reshape((camera_manager.primary_core.getImageHeight(),
                           camera_manager.primary_core.getImageWidth()))
    camera_manager.img_width = camera_manager.primary_core.getImageWidth()
    camera_manager.img_height = camera_manager.primary_core.getImageHeight()
    # Normalize before passing to Napari
    img_1 = normalize_to_8bit(img_1)

    # upload the live feed with the binary image rather than the original img_1
    if camera_manager.tracking_state["prepare"] == "ON":
        binary_frame, current_position = binary_threshold(camera_manager, img_1)
        camera_manager.current_position = current_position
        layer_1.data = binary_frame
        layer_1.refresh()
        if camera_manager.tracking_state["track"] == "ON":
            dx = MovingAvg(2)
            dy = MovingAvg(2)
            x_vector = MovingAvg(2)
            y_vector = MovingAvg(2)
            if camera_manager.last_position is None and current_position is not None:
                camera_manager.last_position = current_position
            else:
                print(f"las position: {camera_manager.last_position}")
                update_vectors(camera_manager, x_vector, y_vector, dx, dy) #dx and dy are MovingAvg class

    else:
        # upload image onto layer
        layer_1.data = img_1
        layer_1.refresh()

    # Calculate actual FPS
    if camera_manager.last_tracking_frame_time is not None:
        tracking_frame_time = time.time() - camera_manager.last_tracking_frame_time  # Time per frame
        if tracking_frame_time > 0:
            real_tracking_fps = 1 / tracking_frame_time
        else:
            real_tracking_fps = 0
    camera_manager.last_tracking_frame_time = time.time()  # Update last frame time

    print(f"Tracking FPS: {real_tracking_fps:.2f}")


def recording_start_live(camera_manager, layer_2):
    print("starting tracking updater")
    while camera_manager.secondary_core.getRemainingImageCount() == 0:
        print("no frame loaded")
        time.sleep(0.01)  # Small delay to allow frames to arrive

    if camera_manager.secondary_core.getRemainingImageCount() > 0:  # Ensure there's a new frame
        # this generates a tuple where the first element the next frame in
        # the circular buffer, removing it and allowing is to work with it
        while camera_manager.secondary_core.getRemainingImageCount() > 1:
            camera_manager.secondary_core.popNextImage()

    img_2 = camera_manager.secondary_core.popNextImage()

    if img_2 is None or img_2.size == 0:
        print("Error: No image data received from camera.")
        return  # Exit to prevent passing None to Napari

    # since MM produces the image in the form of a fattened array (1D),
    # we need to reshape it to a 2D array that can be "seen" as an image
    img_2 = img_2.reshape((camera_manager.secondary_core.getImageHeight(),
                           camera_manager.secondary_core.getImageWidth()))
    print("img_2 reshaped")
    # Normalize before passing to Napari
    img_2 = normalize_to_8bit(img_2)
    print("img_2 normalized")

    print("updating layer_2")
    layer_2.data = img_2
    layer_2.refresh()

    # Calculate actual FPS
    if camera_manager.last_recording_frame_time is not None:
        recording_frame_time = time.time() - camera_manager.last_recording_frame_time  # Time per frame
        if recording_frame_time > 0:
            real_recording_fps = 1 / recording_frame_time
        else:
            real_tracking_fps = 0
    camera_manager.last_recording_frame_time = time.time()  # Update last frame time

    print(f"Recording FPS: {real_recording_fps:.2f}")
