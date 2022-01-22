import math
from colorama import Fore, Back, Style

import numpy

default_palette = {
    0 : 'WHITE',
    1 : 'WHITE',
    2 : 'RED',
    3 : 'BLUE',
    4 : 'GREEN',
    5 : 'YELLOW'
}

def chunk_to_braille(chunk):
    braille_id = (
            bool(chunk[0,0]) * 1 +
            bool(chunk[1,0]) * 2 +
            bool(chunk[2,0]) * 4 +
            bool(chunk[0,1]) * 8 +
            bool(chunk[1,1]) * 16 +
            bool(chunk[2,1]) * 32 +
            bool(chunk[3,0]) * 64 +
            bool(chunk[3,1]) * 128)
    char = chr(0x2800 + braille_id)
    return char

def images_to_row(
        images,
        separator = ' ',
        left_pad = '',
        right_pad = ''):
   
    split_images = [list(im.splitlines()) for im in images]
    lines = [left_pad + separator.join(l) + right_pad
            for l in zip(*split_images)]
    return '\n'.join(lines)

def image_to_braille(
    image,
    use_colors = False,
    color_palette = default_palette,
    background_color = None
):
    
    h = image.shape[0]
    w = image.shape[1]
    out_h = math.ceil(h / 4)
    out_w = math.ceil(w / 2)
    
    lines = []
    for i in range(out_h):
        line = []
        for j in range(out_w):
            chunk = image[i*4:(i+1)*4, j*2:(j+1)*2]
            char = chunk_to_braille(chunk)
            if use_colors:
                max_id = numpy.max(chunk)
                color_name = color_palette[max_id]
                char = getattr(Fore, color_name) + char
            line.append(char)
        line = ''.join(line)
        if use_colors:
            line = line + Style.RESET_ALL
        lines.append(line)
    lines = '\n'.join(lines)
    
    text = lines
    if use_colors and background_color is not None:
        text = getattr(Back, background) + lines
    #if use_colors:
    #    lines = lines + Style.RESET_ALL
    
    return lines

def rasterize_line_segment(
        image,
        line,
        color):
    x0, y0, x1, y1 = line
    x0r = int(round(x0))
    y0r = int(round(y0))
    x1r = int(round(x1))
    y1r = int(round(y1))
    dx = x1 - x0
    dy = y1 - y0
    if abs(dx) > abs(dy):
        if x1 < x0:
            x0, x0r, x1, x1r = x1, x1r, x0, x0r
            y0, y0r, y1, y1r = y1, y1r, y0, y0r
            dx = -dx
            dy = -dy
        steps = x1r - x0r
        if steps:
            for step in range(steps+1):
                t = step/steps
                x = x0r + step
                y = int(round(y0 + t * dy))
                if x < 0 or y < 0 or y >= image.shape[0]:
                    continue
                if x >= image.shape[1]:
                    break
                image[y,x] = color
    
    else:
        if y1 < y0:
            x0, x0r, x1, x1r = x1, x1r, x0, x0r
            y0, y0r, y1, y1r = y1, y1r, y0, y0r
            dx = -dx
            dy = -dy
        steps = y1r - y0r
        if steps:
            for step in range(steps+1):
                t = step/steps
                y = y0r + step
                x = int(round(x0 + t * dx))
                if y < 0 or x < 0 or x >= image.shape[1]:
                    continue
                if y >= image.shape[0]:
                    break
                image[y,x] = color

def rasterize_poly_line(
        image,
        polyline,
        color):
    for i in range(polyline.shape[0]-1):
        p0 = polyline[i]
        p1 = polyline[i+1]
        rasterize_line_segment(
                image,
                (p0[0], p0[1], p1[0], p1[1]),
                color)

def make_legend(plots, colors, width):
    legend = '\n'.join(
        [getattr(Fore, default_palette[color]) + key.ljust(width)[:width]
        for color, key in zip(colors, plots.keys())])
    return legend + Style.RESET_ALL

def plot(
    chart,
    width=160,
    height=80,
    topline=False,
    title=None,
    x_range=None,
    y_range=None,
    colors=(2,3,4,5),
    legend=False,
    minmax_y=False,
):
    
    assert width%2 == 0
    assert height%4 == 0
    
    content = []
    if topline:
        content.append('-'*(width//2))
    if title is not None:
        t = ('%s:'%title).ljust(width//2)[:width//2]
        content.append()
    if legend:
        content.append(make_legend(chart, colors, width//2))
    
    chart = {k:v for k,v in chart.items() if len(v)}
    
    if len(chart):
        if x_range is None:
            x_min = min(numpy.min(line[:,0]) for line in chart.values())
            x_max = max(numpy.max(line[:,0]) for line in chart.values())
            x_range = (x_min, x_max)
        
        if y_range is None:
            y_min = min(numpy.min(line[:,1]) for line in chart.values())
            y_max = max(numpy.max(line[:,1]) for line in chart.values())
            y_range = (y_min, y_max)
        
        x_scale = (x_range[1] - x_range[0])
        y_scale = (y_range[1] - y_range[0])
        
        if minmax_y:
            max_line = (
                Style.RESET_ALL + ('Max: %.04f'%y_range[1]).ljust(width//2))
            content.append(max_line)
        
        image = numpy.zeros((height, width), dtype=numpy.long)
        
        if x_scale and y_scale:
            for i, line in enumerate(chart.values()):
                if colors is None:
                    color = 1
                else:
                    color = colors[i]
                
                line = numpy.array(line).copy()
                line[:,0] -= x_range[0]
                line[:,0] /= x_scale
                line[:,0] *= width
                
                line[:,1] -= y_range[0]
                line[:,1] /= y_scale
                line[:,1] = 1. - line[:,1]
                line[:,1] *= height
                
                rasterize_poly_line(image, line, color)
            
        image = image_to_braille(image, use_colors=True)
        content.append(image)
        
        if minmax_y:
            min_line = (
                Style.RESET_ALL + ('Min: %.04f'%y_range[0]).ljust(width//2))
            content.append(min_line)
    
    content = '\n'.join(content)

    return content

#def plot_grid(charts, grid_width, **kwargs):
#    grid_cells = []
#    for chart in charts:
#        chart_lines = plot(chart, **kwargs)

def grid(grid_cells, grid_width, cell_width, border=False, pad=True):
    #import pdb
    #pdb.set_trace()
    content = []
    if border:
        content.append('+' + ('-'*(cell_width//2) + '+') * grid_width)
    
    for i in range(math.ceil(len(grid_cells)/grid_width)):
        row_cells = grid_cells[i*grid_width:(i+1)*grid_width]
        row_cells = [rc.split('\n') for rc in row_cells]
        for lines in zip(*row_cells):
            if border:
                line = '|' + '|'.join(lines) + '|'
            elif pad:
                line = '  ' + '    '.join(lines) + '  '
            else:
                line = ''.join(lines)
            content.append(line)
    
        if border:
            content.append('+' + ('-'*(cell_width//2) + '+') * grid_width)
    
    content = '\n'.join(content)
    
    return content
