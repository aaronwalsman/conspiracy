import math
import time

import numpy

from conspiracy.plot import plot_poly_lines, grid, default_colors

default_capacity = 2048
class Log:
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
    
    def to_poly_line(self, x_coord):
        if x_coord == 'step':
            return self.contents()[:,[1,0]]
        elif x_coord == 'time':
            return self.contents()[:,[2,0]]
        elif x_coord == 'relative_time':
            xy = self.contents()[:,[2,0]].copy()
            xy[:,0] -= xy[0,0]
            return xy

def plot_logs(logs, x_coord='step', *args, **kwargs):
    poly_lines = {name:log.to_poly_line(x_coord) for name, log in logs.items()}
    return plot_poly_lines(poly_lines, *args, **kwargs)
    
def plot_logs_grid(
    logs,
    x_coord='step',
    grid_width=2,
    width=160,
    height=80,
    colors='AUTO',
    border=None,
    *args,
    **kwargs
):
    cell_width=width//grid_width - 4
    plots = []
    for i, (name, log) in enumerate(logs.items()):
        if colors == 'AUTO':
            cell_colors = {name:default_colors[i%len(default_colors)]}
        plots.append(plot_logs(
            {name:log},
            width=cell_width,
            height=40,
            colors=cell_colors,
            *args,
            **kwargs,
        ))
    
    return grid(plots, grid_width, cell_width//2, border=border)
