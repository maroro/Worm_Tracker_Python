"""

*** XYTracker: Abstract Base Class for Object Tracking ***

This class serves as a template for implementing various XY tracking algorithms
in a Micro-Manager plugin. It enforces a structure by defining abstract methods
that subclasses must implement. The tracker identifies high-contrast objects
in images and estimates their movement over time.

Key Features:
- Defines a standard interface for different tracking methods. (i.e. mean_shift for now)
- Ensures subclasses implement essential tracking functions.
- Allows customization of tracking parameters such as threshold,
erosion, dilation, and ROI selection.

Subclasses should implement:
- `initialize()`: To set up tracking with an initial frame.
- `add_feature()`: To specify an object to track.
- `track()`: To process frames and estimate movement.

*** BinaryTracker: Implementation of Object Tracking Using Binary Thresholding ***

This subclass of XYTracker tracks the largest high-contrast object in a frame
by applying binary thresholding and contour detection. It calculates the centroid
of the detected object and estimates its movement between frames.

Key Features:
- Converts the input frame to grayscale and applies a threshold.
- Finds the largest contour to determine the object’s position.
- Computes movement vectors (`delta_x`, `delta_y`) to track displacement.
- Returns the processed binary image, movement vector, and object position.

"""

from abc import ABC, abstractmethod
import numpy as np
import cv2

class XYTracker(ABC):
    def __init__(self):
        self.half_width = 10
        self.threshold = 50
        self.bright_bkg = True
        self.erode = 0
        self.dilate = 0
        self.color_margin = 30
        self.max_corners = 100
        self.roi = None

    # abstract methods that can only be implemented by subclasses (ABC)
    @abstractmethod
    def initialize(self, first_frame, feature_loc):
        pass

    @abstractmethod
    def add_feature(self, pt):
        pass

    @abstractmethod
    def track(self, input_frame):
        pass

    # gettters and setters: these allow you to access
    # and modify tracking parameters
    def get_half_width(self):
        return self.half_width

    def set_half_width(self, width):
        self.half_width = width

    def get_threshold(self):
        return self.threshold

    def set_threshold(self, value):
        self.threshold = value

    def get_bright_bkg(self):
        return self.bright_bkg

    def set_bright_bkg(self, value):
        self.bright_bkg = value

    def get_erode(self):
        return self.erode

    def set_erode(self, value):
        self.erode = value

    def get_dilate(self):
        return self.dilate

    def set_dilate(self, value):
        self.dilate = value

    def get_color_margin(self):
        return self.color_margin

    def set_color_margin(self, value):
        self.color_margin = value

    def get_max_corners(self):
        return self.max_corners

    def set_max_corners(self, value):
        self.max_corners = value


"""
**BinaryTracker: Implementation of Object Tracking Using Binary Thresholding

This subclass of XYTracker tracks the largest high-contrast object in a frame 
by applying binary thresholding and contour detection. It calculates the centroid 
of the detected object and estimates its movement between frames.

Key Features:
- Converts the input frame to grayscale and applies a threshold.
- Finds the largest contour to determine the object’s position.
- Computes movement vectors (`delta_x`, `delta_y`) to track displacement.
- Returns the processed binary image, movement vector, and object position.

"""


class BinaryTracker(XYTracker):
    def __init__(self):
        super().__init__()
        self.curr_point = None
        self.prev_point = None

    def initialize(self, first_frame, feature_loc):
        self.curr_point = feature_loc
        self.prev_point = feature_loc

    def add_feature(self, pt):
        self.curr_point = pt
        self.prev_point = pt

    def track(self, input_frame):
        # convert to grayscale
        gray = cv2.cvtColor(input_frame, cv2.COLOR_BGR2GRAY)
        # threshold the image based on input and apply inverse threshold if
        # background is bright, or regular threshold for dark background.
        _, binary = cv2.threshold(gray, self.threshold, 255,
                                  cv2.THRESH_BINARY_INV if self.bright_bkg else cv2.THRESH_BINARY)
        # Finds contours (connected regions of white pixels) in the thresholded image.
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # select largest contour. In this case we assume the worm's contour is the
            # largest contour (object) in the image.
            largest_contour = max(contours, key=cv2.contourArea)
            # Computes image moments, which help calculate the object's center of mass.
            #https://docs.opencv.org/2.4/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html
            moments = cv2.moments(largest_contour)

            if moments["m00"] != 0:
                # Computes the centroid (center) of the object and Updates
                # the current and previous positions.
                # https://en.wikipedia.org/wiki/Image_moment
                self.prev_point = self.curr_point
                self.curr_point = (int(moments["m10"] / moments["m00"]), int(moments["m01"] / moments["m00"]))
                # computes change in place over time (delta x, delta y)
                delta_x = self.curr_point[0] - self.prev_point[0]
                delta_y = self.curr_point[1] - self.prev_point[1]

                # this is what you expect if everything is correct
                return binary, (delta_x, delta_y), self.curr_point
            else:
                # Object was detected but has no area (e.g., noise)
                return binary, (0, 0), self.curr_point
        else:
            # No contours were detected in the frame
            return binary, (0, 0), self.curr_point
