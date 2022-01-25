import time
import math

import numpy

from conspiracy.plot import plot, grid

class ConsecutiveLog:
    def __init__(self, dims):
        self.dims = dims
        self.step = 0
        self.data = numpy.zeros((1, dims))
    
    def get_state(self):
        return {
            'dims' : self.dims,
            'step' : self.step,
            'data' : self.data,
        }
    
    def set_state(self, state):
        self.dims = state['dims']
        self.step = state['step']
        self.data = state['data']
    
    def log(self, item):
        assert len(item) == self.dims
        if self.step >= self.data.shape[0]:
            self.data = numpy.concatenate(
                (self.data, numpy.zeros_like(self.data)), axis=0).copy()
        self.data[self.step] = item
        
        self.step += 1
    
    def contents(self):
        return self.data[:self.step].copy()

default_capacity = 2048
class ConsecutiveCompressedLog:
    def __init__(self, dims, capacity=default_capacity):
        self.capacity = capacity
        self.dims = dims
        self.step = 0
        self.data = numpy.zeros((capacity, dims))
        self.compression = 1
    
    def get_state(self):
        return {
            'capacity' : self.capacity,
            'dims' : self.dims,
            'step' : self.step,
            'data' : self.data,
            'compression' : self.compression,
        }
    
    def set_state(self, state):
        self.capacity = state['capacity']
        self.dims = state['dims']
        self.step = state['step']
        self.data = state['data']
        self.compresssion = state['compression']
    
    def log(self, item):
        assert len(item) == self.dims
        row = self.step // self.compression
        if row >= self.capacity:
            self.compression = self.compression * 2
            compressed_log = (self.data[0::2] + self.data[1::2]) / 2.
            empty = numpy.zeros((self.capacity//2, self.dims))
            self.data = numpy.concatenate((compressed_log, empty), axis=0)
            row = self.step // self.compression
        n = self.step % self.compression
        self.data[row] = (self.data[row] * n + item)/(n+1)
        
        self.step += 1
    
    def contents(self):
        row = math.ceil(self.step / self.compression)
        return self.data[:row]

class SynchronousConsecutiveLog:
    def __init__(self, *names, compressed=False, capacity=default_capacity):
        self.global_step = 0
        self.logs = {}
        for name in names:
            if compressed:
                self.logs[name] = ConsecutiveCompressedLog(3, capacity)
            else:
                self.logs[name] = ConsecutiveLog(3)
    
    def get_state(self):
        state = {'global_step':self.global_step}
        state.update({name:log.get_state() for name, log in self.logs.items()})
        return state
    
    def set_state(self, state):
        self.global_step = state['global_step']
        for name, log in self.logs.items():
            log.set_state(state[name])
    
    def log(self, **kwargs):
        for name, value in kwargs.items():
            assert name in self.logs, 'Name: %s not in %s'%(
                name, list(self.logs.keys()))
            t = time.time()
            v = float(value)
            if math.isnan(v):
                print('logging NAN: %s'%name)
            
            data = numpy.array([self.global_step, t, float(value)])
            self.logs[name].log(data)
    
    def step(self):
        self.global_step += 1
    
    def contents(self):
        return {name : log.contents for name, log in self.log.items()}
    
    def plot_overlapping(self, x_axis='step', **kwargs):
        lines = {}
        for name, log in self.logs.items():
            if x_axis == 'step':
                lines[name] = log.contents()[:,[0,2]]
            elif x_axis == 'time':
                lines[name] = log.contents()[:,[1,2]]
        graph = plot(lines, **kwargs)
        return graph
    
    def plot_sequential(self, x_axis='step', **kwargs):
        content = []
        for name, log in self.logs.items():
            if x_axis == 'step':
                line = log.contents()[:,[0,2]]
            elif x_axis == 'time':
                line = log.contents()[:,[1,2]]
            graph = plot({name:line}, **kwargs)
            content.append(graph)
        return '\n'.join(content)
    
    def plot_grid(
        self, x_axis='step', grid_width=2, width=60, border=False, **kwargs):
        grid_cells = []
        for name, log in self.logs.items():
            if x_axis == 'step':
                line = log.contents()[:,[0,2]]
            elif x_axis == 'time':
                line = log.contents()[:,[1,2]]
            graph = plot({name:line}, width=width, **kwargs)
            grid_cells.append(graph)
        
        content = grid(
            grid_cells, grid_width=grid_width, cell_width=width, border=border)
        return content

