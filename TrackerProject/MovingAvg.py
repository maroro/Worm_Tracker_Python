"""
The class MovingAvg can be used to create a sliding window of a certain "length". this window
will be constantly updated such that the latest item added is the latest data point and the
oldest value added represent the oldest data point.you can update the sliding window each
time the timer goes off for image acquisition.
"""

class MovingAvg:
    def __init__(self, length=2):
        self.avg_length = max(2, length)
        #create a list of zeros the specified "length"
        self.avg_buffer = [0] * self.avg_length
        self.avg_buffer_index = 0
        self.sum = 0
        self.last = 0
        self.result = 0
        self.raw = 0

    def update(self, new_value):
        if new_value is None or not isinstance(new_value, (int, float)):
            return self.result

        self.raw = new_value
        self.last = self.avg_buffer[self.avg_buffer_index]
        self.avg_buffer[self.avg_buffer_index] = new_value

        # add the difference between current and last c
        self.sum += (self.raw - self.last)
        # if the buffer index = 0, then move on to next index (1).
        # % self.avg_length makes it so that it calculates the remainder
        # this makes it so that each time self.avg_buffer_index =3 self.avg_length
        # the index will reset to 0
        self.avg_buffer_index = (self.avg_buffer_index + 1) % self.avg_length

        self.result = self.sum / self.avg_length
        return self.result

    def get_average(self):
        return self.result

    def get_raw(self):
        return self.raw

    def clear(self):
        self.avg_buffer = [0] * self.avg_length
        self.avg_buffer_index = 0
        self.sum = 0
        self.last = 0
        self.result = 0
        self.raw = 0
