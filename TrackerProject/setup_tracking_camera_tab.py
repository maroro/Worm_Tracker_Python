import napari
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import (QGridLayout,
                             QGroupBox, QFormLayout,
                             QLineEdit, QCheckBox, QComboBox, QPushButton)
from PyQt5.QtWidgets import QWidget
import time
from img_handling_functions import *

"""
In the Tracking Camera tab, you can place controls
specific to the tracking camera.
"""
class setup_tracking_camera_tab(QWidget):
    def __init__(self, camera_manager = None):
        super().__init__()
        # Initialize tracking_settings dictionary where
        # for easy access
        print("starting tracking tab")
        self.camera_manager = camera_manager
        if self.camera_manager is None:
            raise ValueError("Error: `camera_manager` must be initialized before creating `setup_tracking_camera_tab`.")
        self.tracking_tab_settings = camera_manager.tracking_tab_settings
        self.recording_tab_settings = camera_manager.recording_tab_settings

        # generate validators for user inputs
        int_validator = QIntValidator()
        double_validator = QDoubleValidator(0.0, 100.0, 2)  # Allows values between 0.0 and 100.0 with 2 decimal places
        double_validator.setNotation(QDoubleValidator.StandardNotation)  # Standard decimal notation

        print("setting layout")
        #set the layout
        layout = QGridLayout()
        self.setLayout(layout)

        ### --- Left Box: Tracking Camera Settings --- ###
        print("creating camera settings")
        tracking_settings_group = QGroupBox("Tracking Camera Settings")
        tracking_settings_layout = QFormLayout()

        # create input boxes
        self.exposure_input = QLineEdit()
        self.fps_input = QLineEdit()
        self.binning_input = QComboBox()

        # Set default values
        self.exposure_input.setText(str(self.tracking_tab_settings["exposure"]))
        self.fps_input.setText(str(self.tracking_tab_settings["fps"]))
        self.binning_input.addItems(["2x2", "4x4"])
        self.binning_input.setCurrentText(self.tracking_tab_settings["binning"])

        # set integer validator so that user can only inout number
        self.exposure_input.setValidator(int_validator)
        self.fps_input.setValidator(int_validator)


        tracking_settings_layout.addRow("Exposure (ms):", self.exposure_input)
        tracking_settings_layout.addRow("FPS:", self.fps_input)
        tracking_settings_layout.addRow("Binning:", self.binning_input)

        #Directly update the dictionary using `connect()`
        self.exposure_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"exposure": int(self.exposure_input.text()) if self.exposure_input.text().isdigit() else 0}))
        self.fps_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"fps": int(self.fps_input.text()) if self.fps_input.text().isdigit() else 0}))
        self.binning_input.currentTextChanged.connect(
            lambda: self.tracking_tab_settings.update({"binning": self.binning_input.currentText()}))

        tracking_settings_group.setLayout(tracking_settings_layout)

        ### --- Right Box: Mean-Shift Tracking Parameters ---
        print("creating tracking settings")
        tracking_params_group = QGroupBox("Mean-Shift Tracking Parameters")
        tracking_params_layout = QFormLayout()

        self.scale_input = QLineEdit()
        self.xx_input = QLineEdit()
        self.xy_input = QLineEdit()
        self.yx_input = QLineEdit()
        self.yy_input = QLineEdit()
        self.gain_input = QLineEdit()
        self.kd_xy_input = QLineEdit()
        self.xy_calibration_input = QLineEdit()
        self.square_size_input = QLineEdit()
        self.threshold_input = QLineEdit()
        self.erode_input = QLineEdit()
        self.dilate_input = QLineEdit()
        self.max_runway_input = QLineEdit()
        self.brightfield_checkbox = QCheckBox("Brightfield?")
        self.save_stage_positions_checkbox = QCheckBox("Save Stage Positions?")

        #populate the boxes we just created
        print("populating tracking settings")
        self.scale_input.setText((str(self.tracking_tab_settings["scale"])))
        self.threshold_input.setText(str(self.tracking_tab_settings["threshold"]))
        self.square_size_input.setText(str(self.tracking_tab_settings["square_size"]))
        self.erode_input.setText(str(self.tracking_tab_settings["erode"]))
        self.dilate_input.setText(str(self.tracking_tab_settings["dilate"]))
        self.max_runway_input.setText(str(self.tracking_tab_settings["max_runway"]))
        self.xx_input.setText(str(self.tracking_tab_settings["xx"]))
        self.xy_input.setText(str(self.tracking_tab_settings["xy"]))
        self.yx_input.setText(str(self.tracking_tab_settings["yx"]))
        self.yy_input.setText(str(self.tracking_tab_settings["yy"]))
        self.gain_input.setText(str(self.tracking_tab_settings["gain"]))

        print("validating tracking settings")
        # apply the integer validator to ensure the user input values are numbers
        self.scale_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"scale": int(self.scale_input.text()) if self.scale_input.text().isdigit() else 0}))
        self.threshold_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"threshold": int(self.threshold_input.text()) if self.threshold_input.text().isdigit() else 0}))
        self.square_size_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"square_size": int(self.square_size_input.text()) if self.square_size_input.text().isdigit() else 0}))
        self.erode_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"erode": int(self.erode_input.text()) if self.erode_input.text().isdigit() else 0}))
        self.dilate_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"dilate": int(self.dilate_input.text()) if self.dilate_input.text().isdigit() else 0}))
        self.max_runway_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"max_runway": int(self.max_runway_input.text()) if self.max_runway_input.text().isdigit() else 0}))
        self.xx_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"xx": int(self.xx_input.text()) if self.xx_input.text().isdigit() else 0}))
        self.xy_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"xy": int(self.xy_input.text()) if self.xy_input.text().isdigit() else 0}))
        self.yx_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"yx": int(self.yx_input.text()) if self.yx_input.text().isdigit() else 0}))
        self.yy_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"yy": int(self.yy_input.text()) if self.yy_input.text().isdigit() else 0}))
        self.gain_input.textChanged.connect(lambda: self.tracking_tab_settings.update(
            {"gain": int(self.gain_input.text()) if self.gain_input.text().isdigit() else 0}))

        print("adding rows onto layout")
        #add all widgets onto the layout. we only add rows since we are using form-layout.
        tracking_params_layout.addRow("XX:", self.xx_input)
        tracking_params_layout.addRow("XY:", self.xy_input)
        tracking_params_layout.addRow("YX:", self.yx_input)
        tracking_params_layout.addRow("YY:", self.yy_input)
        tracking_params_layout.addRow("Scale (um/pixel):", self.scale_input)
        tracking_params_layout.addRow("Gain:", self.gain_input)
        tracking_params_layout.addRow("Kd for XY:", self.kd_xy_input)
        tracking_params_layout.addRow("XY Calibration Setup:", self.xy_calibration_input)
        tracking_params_layout.addRow("Square Size:", self.square_size_input)
        tracking_params_layout.addRow("Threshold:", self.threshold_input)
        tracking_params_layout.addRow("Erode:", self.erode_input)
        tracking_params_layout.addRow("Dilate:", self.dilate_input)
        tracking_params_layout.addRow("Max Runway (µm):", self.max_runway_input)
        tracking_params_layout.addRow(self.brightfield_checkbox)
        tracking_params_layout.addRow(self.save_stage_positions_checkbox)

        print("setting layout")
        # set the layout we designed above
        tracking_params_group.setLayout(tracking_params_layout)

        ### --- ADD BUTTONS FOR TRACKING FUNCTIONALITY --- ###
        print("creating buttons")
        tracking_buttons_group = QGroupBox("Tracking options")
        tracking_buttons_layout = QFormLayout()

        self.live_button = QPushButton("Live")
        self.prepare_button = QPushButton("Prepare")
        self.calibrate_button = QPushButton("Calibrate")
        self.track_button = QPushButton("Track")
        self.record_button = QPushButton("Record")
        self.stop_button = QPushButton("Stop")

        # Enable toggle mode
        self.prepare_button.setCheckable(True)
        self.track_button.setCheckable(True)
        self.record_button.setCheckable(True)
        self.stop_button.setCheckable(True)

        self.live_button.clicked.connect(self.start_live)
        self.prepare_button.clicked.connect(self.update_tracking_state)
        self.calibrate_button.clicked.connect(self.run_calibration)
        self.track_button.clicked.connect(self.update_tracking_state)
        self.record_button.clicked.connect(self.update_tracking_state)
        self.stop_button.clicked.connect(self.update_tracking_state)

        tracking_buttons_layout.addRow(self.live_button)
        tracking_buttons_layout.addRow(self.prepare_button)
        tracking_buttons_layout.addRow(self.track_button)
        tracking_buttons_layout.addRow(self.record_button)
        tracking_buttons_layout.addRow(self.stop_button)

        tracking_buttons_group.setLayout(tracking_buttons_layout)

        #### ---ADD GROUPS TO MAIN LAYOUT --- ###
        print("adding widgets")
        layout.addWidget(tracking_settings_group, 0, 0)  # Left box
        layout.addWidget(tracking_params_group, 0, 1)  # center box
        layout.addWidget(tracking_buttons_group, 0, 2)  # Right box

###############################################################################
###############################################################################

    def set_camera_manager(self, camera_manager):
        """ Updates camera manager after GUI initialization """
        self.camera_manager = camera_manager


    def start_live(self):
        try:
            if self.camera_manager is None:
                print("Camera Manager not initialized!")
                return
            print("Camera Manager exists")  # If we get here, `self.camera_manager` is not None
        except Exception as e:
            print(f"Crash when accessing CameraManager: {e}")

        # Start Napari viewer
        print("starting viewer")
        viewer = napari.Viewer()
        layer_1 = None
        layer_2 = None

        # get the tracking camera settings from CameraManager
        tracking_exposure = self.tracking_tab_settings["exposure"]
        tracking_binning = self.tracking_tab_settings["binning"]
        tracking_fps = self.tracking_tab_settings["fps"]
        tracking_interval_ms = max((1000 / tracking_fps) - tracking_exposure, 0)
        # initiate the acquisition in the tracking camera
        self.camera_manager.primary_core.setExposure(tracking_exposure)
        self.camera_manager.primary_core.setProperty(self.camera_manager.primary_camera, "Binning", tracking_binning)
        print("initiating live sequence")

        # starts sequence acquisition, creates layer_1, passes the first image to layer_1,
        # starts timer to continue to update layer_1
        self.camera_manager.primary_core.startContinuousSequenceAcquisition()

        while self.camera_manager.primary_core.getRemainingImageCount() == 0:
            time.sleep(0.01)  # Small delay to allow frames to arrive

        if self.camera_manager.primary_core.getRemainingImageCount() > 0:  # Ensure there's a new frame
            # this generates a tuple where the first element the next frame in
            # the circular buffer, removing it and allowing is to work with it
            while self.camera_manager.primary_core.getRemainingImageCount() > 1:
                self.camera_manager.primary_core.popNextImage()

        img_1 = self.camera_manager.primary_core.popNextImage()

        if img_1 is None or img_1.size == 0:
            print("Error: No tracking image received.")
            return  # Exit to prevent passing None to Napari


        # since MM produces the image in the form of a fattened array (1D),
        # we need to reshape it to a 2D array that can be "seen" as an image
        img_1 = img_1.reshape((self.camera_manager.primary_core.getImageHeight(),
                               self.camera_manager.primary_core.getImageWidth()))
        print("img_1 reshaped")
        # Normalize before passing to Napari
        img_1 = normalize_to_8bit(img_1)
        print("img_1 normalized")
        # Apply translation to separate images
        if  layer_1 is None:
            layer_1 = viewer.add_image(img_1, name="Tracking Camera", colormap="gray", translate=(0, 0))
        else:
            layer_1.data = img_1

        # Ensure layer_1 is valid
        if layer_1 is None:
            print("Error: Napari layer creation failed.")
            return  # Prevent further execution

        # Adjust Napari's camera view to fit both images
        translate_x = img_1.shape[0] + 50
        viewer.camera.center = (img_1.shape[1] // 2, img_1.shape[0] // 2 + translate_x // 2)  # Center on both images
        viewer.camera.zoom = 0.5  # Zoom out to fit both images
        print("viewer layout setup")

        self.camera_manager.last_tracking_frame_time = time.time()# collect time when first frame is taken
        self.camera_manager.tracking_timer = QTimer()
        self.camera_manager.tracking_timer.timeout.connect(partial(tracking_start_live, self.camera_manager, layer_1))
        self.camera_manager.tracking_timer.start(int(tracking_interval_ms))

        ### --- repeat these same steps for recording camera if there is one --- ###

        if self.camera_manager.secondary_core:
            # get the tracking camera settings from CameraManager
            recording_exposure = self.recording_tab_settings["exposure"]
            recording_binning = self.recording_tab_settings["binning"]
            recording_fps = self.recording_tab_settings["fps"]
            recording_interval_ms = max((1000 / recording_fps) - tracking_exposure, 0)
            # initiate the acquisition in the tracking camera
            self.camera_manager.secondary_core.setExposure(recording_exposure)
            self.camera_manager.secondary_core.setProperty(self.camera_manager.secondary_camera, "Binning", recording_binning)
            print("initiating live sequence")

            # starts sequence acquisition, creates layer_1, passes the first image to layer_1,
            # starts timer to continue to update layer_1
            self.camera_manager.secondary_core.startContinuousSequenceAcquisition()

            while self.camera_manager.secondary_core.getRemainingImageCount() == 0:
                time.sleep(0.01)  # Small delay to allow frames to arrive

            if self.camera_manager.secondary_core.getRemainingImageCount() > 0:  # Ensure there's a new frame
                # this generates a tuple where the first element the next frame in
                # the circular buffer, removing it and allowing is to work with it
                while self.camera_manager.secondary_core.getRemainingImageCount() > 1:
                    self.camera_manager.secondary_core.popNextImage()

            img_2 = self.camera_manager.secondary_core.popNextImage()

            if img_2 is None or img_2.size == 0:
                print("Error: No recording image received.")
                return  # Exit to prevent passing None to Napari

            # since MM produces the image in the form of a fattened array (1D),
            # we need to reshape it to a 2D array that can be "seen" as an image
            img_2 = img_2.reshape((self.camera_manager.secondary_core.getImageHeight(),
                                   self.camera_manager.secondary_core.getImageWidth()))
            print("img_1 reshaped")
            # Normalize before passing to Napari
            img_2 = normalize_to_8bit(img_2)
            print("img_1 normalized")
            # Apply translation to separate images
            if layer_2 is None:
                layer_2 = viewer.add_image(img_2, name="Tracking Camera", colormap="gray", translate=(0, translate_x))
            else:
                layer_2.data = img_2

            # Ensure layer_1 is valid
            if layer_2 is None:
                print("Error: Napari layer creation failed.")
                return  # Prevent further execution

            self.camera_manager.last_recording_frame_time = time.time()  # collect time when first frame is taken
            self.camera_manager.recording_timer = QTimer()
            self.camera_manager.recording_timer.timeout.connect(
                partial(recording_start_live, self.camera_manager, layer_2))
            self.camera_manager.recording_timer.start(int(recording_interval_ms))

        ### --- this function is essential to stop acquisition when napari closes --- ###
        # this function is nested inside the start_live method because it was the only day I could make it work as an
        # event, which is what happens when napari window closes.
        def on_close(event):
            print("Napari viewer closed. Stopping sequence acquisition.")
            self.camera_manager.primary_core.stopSequenceAcquisition()
            self.camera_manager.tracking_timer.stop()

            if self.camera_manager.secondary_core:
                self.camera_manager.secondary_core.stopSequenceAcquisition()
                self.camera_manager.recording_timer.stop()

            print("Live tracking stopped.")

        viewer.window._qt_window.closeEvent = lambda event: on_close(event)

        # get going in napari
        viewer.show()

    def update_tracking_state(self):
        if self.prepare_button.isChecked():
            self.camera_manager.tracking_state["prepare"] = "ON"  # Start prepare mode
        else:
            self.camera_manager.tracking_state["prepare"] = "OFF"  # Stop prepare mode

        if self.track_button.isChecked():
            self.camera_manager.tracking_state["track"] = "ON"
        else:
            self.camera_manager.tracking_state["track"] = "OFF"

        if self.record_button.isChecked():
            self.camera_manager.tracking_state["record"] = "ON"
        else:
            self.camera_manager.tracking_state["record"] = "OFF"


    def prepare_tracking(self):
        if self.camera_manager is None:
            print("Camera Manager not initialized!")
            return
        frame = self.camera_manager.primary_core.snapImage()
        frame = frame.reshape(
            (self.camera_manager.primary_core.getImageHeight(), self.camera_manager.primary_core.getImageWidth()))
        frame = normalize_to_8bit(frame)
        binary_frame, _ = self.tracker.track(frame)
        if self.tracking_layer is None:
            self.tracking_layer = self.viewer.add_image(binary_frame, name="Binary Tracker", colormap="gray")
        else:
            self.tracking_layer.data = binary_frame

    def start_tracking(self):
        if self.camera_manager is None:
            print("Camera Manager not initialized!")
            return
        self.tracking = True
        self.timer.timeout.connect(self.update_tracking)
        self.timer.start(100)

    def update_tracking(self):
        frame = self.camera_manager.primary_core.snapImage()
        frame = frame.reshape(
            (self.camera_manager.primary_core.getImageHeight(), self.camera_manager.primary_core.getImageWidth()))
        frame = normalize_to_8bit(frame)
        binary_frame, position = self.tracker.track(frame)
        if position and self.tracker.prev_position:
            dx = position[0] - self.tracker.prev_position[0]
            dy = position[1] - self.tracker.prev_position[1]
            self.camera_manager.primary_core.setRelativeXYPosition(dx * 0.1, dy * 0.1)
        self.tracking_layer.data = binary_frame

    def stop_tracking(self):
        self.timer.stop()
        self.tracking = False
        self.raw_layer = None
        self.tracking_layer = None
        self.viewer.layers.clear()
        print("Tracking stopped and reset.")