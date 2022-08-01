import math
import time

import numpy

from conspiracy.plot import plot_poly_lines, grid #, default_colors

default_capacity = 2048
class Log:
    def __init__(self, capacity=default_capacity, state=None):
        self.capacity = capacity
        self.step = 0
        if capacity == 'adaptive':
            c = 1
        else:
            c = capacity
        self.data = numpy.zeros((c, 3))
        self.compression = 1
        
        if state is not None:
            self.set_state(state)

    def get_state(self):
        return {
            'capacity' : self.capacity,
            'step' : self.step,
            'data' : self.data.tolist(),
            'compression' : self.compression,
        }

    def set_state(self, state):
        self.capacity = state['capacity']
        self.step = state['step']
        self.data = numpy.array(state['data'])
        self.compression = state['compression']

    def log(self, value):
        row = self.step // self.compression
        #if row >= self.capacity:
        if row >= self.data.shape[0]:
            if self.capacity == 'adaptive':
                self.data = numpy.concatenate(
                    (self.data, numpy.zeros_like(self.data)), axis=0)
            else:
                self.compression = self.compression * 2
                compressed_log = (self.data[0::2] + self.data[1::2]) / 2.
                empty = numpy.zeros((self.capacity//2, 3))
                self.data = numpy.concatenate((compressed_log, empty), axis=0)
                row = self.step // self.compression
        n = self.step % self.compression
        item = [value, float(self.step), time.time()]
        self.data[row] = (self.data[row] * n + item)/(n+1)

        self.step += 1
    
    def contents(self):
        row = math.ceil(self.step / self.compression)
        return self.data[:row]
    
    def to_poly_line(self, x_coord, x_range=(0.,1.)):
        if x_coord == 'step':
            xy = self.contents()[:,[1,0]]
        elif x_coord == 'time':
            xy = self.contents()[:,[2,0]]
        elif x_coord == 'relative_time':
            xy = self.contents()[:,[2,0]].copy()
            xy[:,0] -= xy[0,0]
        
        n = xy.shape[0]
        start = round(x_range[0] * n)
        end = round(x_range[1] * n)
        return xy[start:end]

class Log2:
    def __init__(self, capacity=default_capacity, state=None):
        self.capacity = capacity
        self.step = 0
        if capacity == 'adaptive':
            c = 1
        else:
            c = capacity
        self.x = []
        self.y = []
        self.t = []
        self.compression = 1
        
        if state is not None:
            self.set_state(state)

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
        #row = self.step // self.compression
        
        if self.capacity is not None and len(self.x) >= self.capacity:
            self.compression = self.compression * 2
            self.x = [(x0 + x1)/2 for x0, x1 in zip(self.x[::2], self.x[1::2])]
            #compressed_log = (self.data[0::2] + self.data[1::2]) / 2.
            #empty = numpy.zeros((self.capacity//2, 3))
            #self.data = numpy.concatenate((compressed_log, empty), axis=0)
            
            row = self.step // self.compression
        
        n = self.step % self.compression
        #item = [value, float(self.step), time.time()]
        #self.data[row] = (self.data[row] * n + item)/(n+1)
        self.x.append(float(self.step))
        self.y.append(value)
        self.t.append(time.time())
        
        self.step += 1
    
    def contents(self):
        row = math.ceil(self.step / self.compression)
        return self.data[:row]
    
    def to_poly_line(self, x_coord, x_range=(0.,1.)):
        if x_coord == 'step':
            xy = self.contents()[:,[1,0]]
        elif x_coord == 'time':
            xy = self.contents()[:,[2,0]]
        elif x_coord == 'relative_time':
            xy = self.contents()[:,[2,0]].copy()
            xy[:,0] -= xy[0,0]
        
        n = xy.shape[0]
        start = round(x_range[0] * n)
        end = round(x_range[1] * n)
        return xy[start:end]
