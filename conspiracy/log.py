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

def plot_logs(logs, x_coord='step', x_range=(0.,1.), *args, **kwargs):
    poly_lines = {
        name:log.to_poly_line(x_coord, x_range=x_range)
        for name, log in logs.items()
    }
    return plot_poly_lines(poly_lines, *args, **kwargs)
    
def plot_logs_grid(
    log_grid,
    x_coord='step',
    width=80,
    height=20,
    colors='auto',
    border=None,
    *args,
    **kwargs
):
    grid_width = max(len(row) for row in log_grid)
    cell_width=width//grid_width - 2
    plots = []
    
    n = 0
    for i, row in enumerate(log_grid):
        plots.append([])
        for j, logs in enumerate(row):
            if colors == 'auto':
                cell_colors = {}
                for k, name in enumerate(logs.keys()):
                    color = default_colors[(n+k)%len(default_colors)]
                    cell_colors[name] = color
            else:
                cell_colors = None
            plots[-1].append(plot_logs(
                logs,
                width=cell_width,
                height=height//len(log_grid),
                colors=cell_colors,
                *args,
                **kwargs,
            ))
            n += len(logs)
    
    return grid(plots, cell_width, border=border)
