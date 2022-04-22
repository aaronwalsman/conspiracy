import time

default_capacity = 2048
class CompressedLog:
    def __init__(self, capacity=default_capacity):
        self.capacity = capacity
        self.step = 0
        self.data = numpy.zeros((capacity, 3))
        self.compression = 1

    def get_state(self):
        return {
            'capacity' : self.capacity,
            'step' : self.step,
            'data' : self.data,
            'compression' : self.compression,
        }

    def set_state(self, state):
        self.capacity = state['capacity']
        self.step = state['step']
        self.data = state['data']
        self.compression = state['compression']

    def log(self, value):
        row = self.step // self.compression
        if row >= self.capacity:
            self.compression = self.compression * 2
            compressed_log = (self.data[0::2] + self.data[1::2]) / 2.
            empty = numpy.zeros((self.capacity//2, self.dims))
            self.data = numpy.concatenate((compressed_log, empty), axis=0)
            row = self.step // self.compression
        n = self.step % self.compression
        item = [value, float(self.step), time.time()]
        self.data[row] = (self.data[row] * n + item)/(n+1)

        self.step += 1

    def contents(self):
        row = math.ceil(self.step / self.compression)
        return self.data[:row]
