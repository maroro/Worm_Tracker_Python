import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIntValidator

from CameraManager import CameraManager
from setup_tracking_camera_tab import setup_tracking_camera_tab
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QWidget, QTabWidget, QGridLayout, QLabel, QLineEdit,
                             QPushButton, QFileDialog
                             )

class CameraGUI(QMainWindow):
    """
    Main window class containing three tabs:
    1) Core Info
    2) Tracking Camera
    3) Recording Camera
    """
    def __init__(self):
        super().__init__()
        self.tracking_path_edit = None
        self.recording_path_edit = None
        self.camera_manager = None

        self.setWindowTitle("Camera Control GUI")

        # Create a QTabWidget and make it the central widget of the main window
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create three tab widgets
        self.core_info_tab = QWidget()
        self.recording_camera_tab = QWidget()

        # Add the tab widgets to the QTabWidget
        self.tab_widget.addTab(self.core_info_tab, "Core Info")
        # Set up the UI for each tab
        self.setup_core_info_tab()


    """
    In the Core Info tab:
    - Three input fields for specifying paths to config files
    - Each input has a 'Browse' button to open a file dialog
    - A 'Load cores' button that initializes the CameraManager
    - Several labels to display camera and stage details
    """
    def setup_core_info_tab(self):
        layout = QGridLayout()
        self.core_info_tab.setLayout(layout)

        # 1) tracking camera config file
        tracking_label = QLabel("Tracking camera config file:")
        self.tracking_path_edit = QLineEdit()
        tracking_browse_btn = QPushButton("Browse")
        tracking_browse_btn.clicked.connect(lambda: self.browse_file(self.tracking_path_edit))

        # 2) Recording camera config file
        recording_label = QLabel("Recording camera config file:")
        self.recording_path_edit = QLineEdit()
        recording_browse_btn = QPushButton("Browse")
        recording_browse_btn.clicked.connect(lambda: self.browse_file(self.recording_path_edit))

        # Place labels, line edits, and buttons in a grid layout
        layout.addWidget(tracking_label,          0, 0)
        layout.addWidget(self.tracking_path_edit, 0, 1)
        layout.addWidget(tracking_browse_btn,     0, 2)

        layout.addWidget(recording_label,         1, 0)
        layout.addWidget(self.recording_path_edit,1, 1)
        layout.addWidget(recording_browse_btn,    1, 2)

        # Single button to load/initialize camera cores
        self.load_cores_button = QPushButton("Load cores")
        layout.addWidget(self.load_cores_button, 2, 0, 1, 3, alignment=Qt.AlignCenter)
        self.load_cores_button.clicked.connect(self.load_cores)

        # Labels to display camera/stage information
        self.tracking_camera_name_label   = QLabel("Tracking camera name: (not loaded)")
        self.tracking_light_source_label  = QLabel("Tracking light source: (none)")
        self.xy_stage_name_label          = QLabel("XY-stage name: (none)")
        self.recording_camera_name_label  = QLabel("Recording camera name: (not loaded)")
        self.recording_camera_light_label = QLabel("Recording camera light source: (none)")

        layout.addWidget(self.tracking_camera_name_label,   3, 0, 1, 3)
        layout.addWidget(self.tracking_light_source_label,  4, 0, 1, 3)
        layout.addWidget(self.xy_stage_name_label,          5, 0, 1, 3)
        layout.addWidget(self.recording_camera_name_label,  6, 0, 1, 3)
        layout.addWidget(self.recording_camera_light_label, 7, 0, 1, 3)

    def setup_recording_camera_tab(self):
        layout = QGridLayout()
        self.recording_camera_tab.setLayout(layout)

    def browse_file(self, line_edit):
        """
        Opens a file dialog to select a file and sets the selected file path
        into the provided QLineEdit widget.

        Parameters:
        line_edit (QLineEdit): The QLineEdit widget where the selected file path is set.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(None, "Select Configuration File", "",
                                                   "Config Files (*.cfg)", options=options)

        if file_path:
            line_edit.setText(file_path)

    """
    Reads the config paths from the line edits and uses them to
    create and initialize a CameraManager instance. Then updates
    the labels with names of devices (cameras, stages, etc.) if found.
    """
    def load_cores(self):
        # Read paths
        tracking_config = self.tracking_path_edit.text().strip()
        recording_config = self.recording_path_edit.text().strip()

        # For demonstration, treat the Micro-Manager config as the "primary" core
        # and the tracking camera config as "secondary". You can adapt as needed.
        # If you want the third config as well, you can rearrange the logic.
        if tracking_config and recording_config:
            print("calling camera manager")
            self.camera_manager = CameraManager(tracking_config, recording_config)
            print("Tracking and recording cores initialized successfully")

            self.tracking_camera_tab = setup_tracking_camera_tab(self.camera_manager)
            self.tab_widget.addTab(self.tracking_camera_tab, "Tracking Camera")

            self.setup_recording_camera_tab()
            self.tab_widget.addTab(self.recording_camera_tab, "Recording Camera")
        else:
            # If you only have one config, just pass the primary
            print("calling camera manager")
            self.camera_manager = CameraManager(primary_config = tracking_config)
            print("Tracking core initialized successfully")
            self.tracking_camera_tab = setup_tracking_camera_tab(self.camera_manager)
            self.tab_widget.addTab(self.tracking_camera_tab, "Tracking Camera")


        # Update existing tracking tab instead of creating a new one
        self.tracking_camera_tab.set_camera_manager(self.camera_manager)
        # Update labels for devices
        self.update_device_labels()

    """Updates the GUI labels with device names from CameraManager."""
    def update_device_labels(self):
        print("updating labels")
        if not self.camera_manager:
            print("Camera Manager is not initialized!")
            return

        # 1) Get the active camera name
        self.tracking_camera_name_label.setText(
            f"Tracking camera name: {self.camera_manager.primary_camera or '(not loaded)'}"
        )

        # 2) Get XY-stage name (if available)
        stage_name = self.camera_manager.primary_core.getXYStageDevice()
        self.xy_stage_name_label.setText(f"XY-stage name: {stage_name or '(none)'}")

        # 3) Get tracking light source (shutter)
        light_source = None
        for dev in self.camera_manager.primary_core.getLoadedDevices():
            if self.camera_manager.primary_core.getDeviceType(dev) == "Shutter":
                light_source = dev
        self.tracking_light_source_label.setText(f"Tracking light source: {light_source or '(none)'}")

        # 4) Get recording camera name
        self.recording_camera_name_label.setText(
            f"Recording camera name: {self.camera_manager.secondary_camera or '(not loaded)'}"
        )

        # 5) Get recording light source (shutter)
        light_source_2 = None
        if self.camera_manager.secondary_core:
            for dev in self.camera_manager.secondary_core.getLoadedDevices():
                if self.camera_manager.secondary_core.getDeviceType(dev) == "Shutter":
                    light_source_2 = dev
            self.recording_camera_light_label.setText(f"Recording camera light source: {light_source_2 or '(none)'}")
        else:
            self.recording_camera_light_label.setText("Recording camera light source: (none)")

def main():
    app = QApplication(sys.argv)
    window = CameraGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()