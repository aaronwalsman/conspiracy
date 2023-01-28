import math
import time

import numpy

from conspiracy.plot import plot_poly_lines, grid

default_capacity = 2048
class Log:
    def __init__(self,
        capacity=default_capacity,
        state=None,
        log_callbacks=None,
    ):
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
        
        if log_callbacks is None:
            log_callbacks = []
        self.log_callbacks = log_callbacks
        
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
        value = float(value)
        row = self.step // self.compression
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
        
        for log_callback in self.log_callbacks:
            log_callback(value, self.step)
        
        self.step += 1
    
    def add_log_callback(self, log_callback):
        self.log_callbacks.append(log_callback)
    
    def add_tensorboard_log_callback(self, writer, name):
        def log_tensorboard(value, step):
            writer.add_scalar(name, value, step)
        self.add_log_callback(log_tensorboard)
    
    def get_contents(self):
        row = math.ceil(self.step / self.compression)
        return self.data[:row]
    
    #def get_recent_y(self):
    #    row = math.ceil(self.step / self.compression)
    #    return self.contents[row-1,0]
    
    def get_y(self):
        return self.contents[:,0]
    
    def get_x(self):
        return self.contents[:,1]
    
    def get_t(self):
        return self.contents[:,2]
    
    contents = property(get_contents)
    x = property(get_x)
    y = property(get_y)
    t = property(get_t)
    
    def to_poly_line(self, x_coord, x_range=(0.,1.), approximation=False):
        if x_coord == 'step':
            xy = self.contents[:,[1,0]]
        elif x_coord == 'time':
            xy = self.contents[:,[2,0]]
        elif x_coord == 'relative_time':
            xy = self.contents[:,[2,0]].copy()
            xy[:,0] -= xy[0,0]
        
        if approximation:
            r = int(math.floor(xy.shape[0] / approximation))
            clip_xy = xy[:r*approximation]
            clip_xy = clip_xy.reshape(approximation, r, 2)
            clip_xy = numpy.mean(clip_xy, axis=1)
            xy = clip_xy
        
        n = xy.shape[0]
        start = round(x_range[0] * n)
        end = round(x_range[1] * n)
        return xy[start:end]
