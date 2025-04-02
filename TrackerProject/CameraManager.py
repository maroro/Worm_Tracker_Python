
"""
CameraManager: Interface for Controlling Multiple Cameras in Micro-Manager

This class handles camera initialization, configuration, and image acquisition
in the Micro-Manager environment. It supports multiple camera cores to allow
simultaneous image capture, enabling synchronized recording during tracking.

Key Features:
- Initializes and configures multiple cameras.
- Captures images for object tracking from multiple sources.
- Handles different camera models and their settings.
- Supports synchronized capture between primary and secondary cameras.

"""

import pymmcore_plus
import os
import ctypes


# Set the correct Micro-Manager path before creating CMMCore()
MM_PATH = r"C:\Program Files\Micro-Manager-2.0"  # Change to your correct path
os.environ["MICROMANAGER_PATH"] = MM_PATH
print(f"Using Micro-Manager from: {MM_PATH}")

class CameraManager:
    """
    Manages one or two Micro-Manager camera cores (primary and optional secondary).
    Loads configuration files, applies camera-specific settings, and handles cleanup.
    """
    def __init__(self, primary_config=None, secondary_config=None):
        print("Initializing Camera Manager")
        # create timer instances for the live and recording commands
        self.img_width = None
        self.img_height = None
        self.tracking_timer = None
        self.recording_timer = None
        self.last_tracking_frame_time = None
        self.last_recording_frame_time = None
        self.last_position = None
        self.current_position = None
        self.tracking_state = {"prepare": "OFF",
                               "track": "OFF",
                               "record": "OFF"}
        self.tracking_tab_settings = {
            "exposure": 10,
            "fps": 20,
            "binning": "4x4",
            "scale":0.1,
            "xx": -20,
            "xy": 5,
            "yx": 5,
            "yy": -20,
            "gain": 10,
            "kd_xy": None,
            "square_size": 100,
            "threshold": 100,
            "erode": 1,
            "dilate": 1,
            "max_runway": 10000,
            "brightfield": True,
            "Save_stage_positions": False
        }

        self.recording_tab_settings = {
            "exposure": 10,
            "fps": 20,
            "binning": "2x2",
            "Save_stage_positions": False
        }

        # Ensure primary_config is provided
        if primary_config is None:
            raise ValueError("Error: primary_config cannot be None.")
        if not os.path.isfile(primary_config):
            raise FileNotFoundError(f"Primary configuration file not found: {primary_config}")

        try:
            print("Initializing tracking core")
            self.primary_core = pymmcore_plus.CMMCorePlus()
            print("Tracking core created")
            self.primary_core.loadSystemConfiguration(primary_config)
            print("Primary configuration loaded successfully.")

            self.primary_camera = self.primary_core.getCameraDevice()
            if self.primary_camera:
                self._setup_camera(self.primary_core, self.primary_camera)
            else:
                print("Warning: No primary camera detected!")
        except Exception as e:
            error_msg = self.primary_core.getLastError() if hasattr(self, "primary_core") else "Micro-Manager core failed before initialization."
            print(f"Micro-Manager Error: {error_msg}")
            print(f"Error loading primary configuration: {str(e)}")
            raise

        # Load secondary camera if a path was selected
        self.secondary_core = None
        self.secondary_camera = None
        if secondary_config:
            if not os.path.isfile(secondary_config):
                raise FileNotFoundError(f"Secondary configuration file not found: {secondary_config}")
            try:
                print("creating recording core")
                self.secondary_core = pymmcore_plus.CMMCorePlus()
                print("loading recording configuration file")
                self.secondary_core.loadSystemConfiguration(secondary_config)
                self.secondary_camera = self.secondary_core.getCameraDevice()
                if self.secondary_camera:
                    self._setup_camera(self.secondary_core, self.secondary_camera)
                else:
                    print("Warning: No secondary camera detected!")
            except Exception as e:
                print(f"Error loading secondary configuration: {str(e)}")
                raise

    def _setup_camera(self, core, camera):
        """Detects camera type and applies necessary settings."""
        cam_id = core.getDeviceLibrary(camera)

        if "Point Grey" in cam_id:
            core.setProperty(camera, "TriggerMode", "External")
        elif "PCO" in cam_id:
            core.setProperty(camera, "Binning", "1x1")
            core.setProperty(camera, "ExternalTrigger", "On")
        elif "TIS" in cam_id:
            core.setProperty(camera, "Gain", "0")
            core.setProperty(camera, "Denoise", "On")
            core.setProperty(camera, "Trigger", "External")
        else:
            # If unknown camera, check for standard trigger properties
            if core.hasProperty(camera, "TriggerMode"):
                core.setProperty(camera, "TriggerMode", "External")
            elif core.hasProperty(camera, "Triggermode"):
                core.setProperty(camera, "Triggermode", "External")

