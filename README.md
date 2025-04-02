# XY motion tracker
This application provides a GUI-based platform for real-time worm tracking using a combination of camera input, image processing, and motion analysis tools. (It is currently under development!)

## Overview
The system is designed to:

- Use Micro-Manager API to interface with camera hardware to stream and capture video frames (CameraManager.py)
- Detect and track C. elegans movement using frame differencing and binary masking (binary_tracker.py)
- Apply filtering and smoothing to motion data to reduce erratic control of motorized stage. (MovingAvg.py)
- Handle image processing: live display, display of transformed image after binarization, and stroage of images upon request (img_handling_functions.py)
- Provide a user-friendly GUI for camera control and data visualization (TrackingGUI.py, setup_tracking_camera_tab.py)
Status

## Status:
- Core components are modular and not well integrated.
- Motion detection and tracking algorithms are functional but need refinement
- Future work includes:
  - Improving detection accuracy and noise filtering
  - Adding data export and session management features
  - Improve the way in which modular components are integrated.
  - add dteailed instructions for python lybrary setup as pymmcore-plus version needs to macth Micro-Manager version.
