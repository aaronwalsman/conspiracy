import math
from colorama import Fore, Back, Style

import numpy

'''
This is a simple library for making plots that can be printed to a terminal.  It
works "drawing" "pixels" made up of braille characters.  The basic structures
this library uses are:

int_image     : An hxw numpy array containing integers.  Each entry in the
                array represents a pixel, with 0 being "background" and 1...N
                representing different colors defined by a color palette.

color_palette : A mapping from integers to colorama color names.

text_image :    A string of braille characters with newline characters
                separating each line.  These are generated from an int_image.
                Each braille character forms a tiny 4x2 block of pixels, and
                the image is colored by inserting colorama characters into the
                text.  The same color must be applied to an entire 4x2 block
                corresponding to a single character though, so some bleeding
                may occur.
'''

# defaults =====================================================================
default_colors = (2,3,4,5,6,7,8)
default_palette = {
    0 : 'WHITE',
    1 : 'WHITE',
    2 : 'RED',
    3 : 'BLUE',
    4 : 'GREEN',
    5 : 'YELLOW',
    6 : 'MAGENTA',
    7 : 'ORANGE',
    8 : 'PINK',
}

# box drawing characters =======================================================
hh = chr(0x2500 + 0x0)
vv = chr(0x2500 + 0x2)
tl = chr(0x2500 + 0xc)
tr = chr(0x2510 + 0x0)
ml = chr(0x2510 + 0xc)
bl = chr(0x2510 + 0x4)
br = chr(0x2510 + 0x8)
mr = chr(0x2520 + 0x4)
tm = chr(0x2520 + 0xc)
bm = chr(0x2530 + 0x4)
mm = chr(0x2530 + 0xc)
ss = ' '

# int_image to text_image conversion ===========================================
def chunk_to_braille(chunk):
    '''
    turns a 4x2 array into a single braille character
    '''
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

def int_image_to_text_image(
    int_image,
    use_colors = False,
    color_palette = default_palette,
    background_color = None
):
    '''
    "renders" an int_image into a text_image
    
    int_image        : a 2 dimensional integer array
    use_colors       : whether to use color tagging based on the integer values
    color_palette    : what color to assign each integer value
    background_color : the background color of the entire image
    '''
    h = int_image.shape[0]
    w = int_image.shape[1]
    out_h = math.ceil(h / 4)
    out_w = math.ceil(w / 2)
    
    lines = []
    for i in range(out_h):
        line = []
        for j in range(out_w):
            chunk = int_image[i*4:(i+1)*4, j*2:(j+1)*2]
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
    
    return lines

# line drawing =================================================================
def rasterize_line_segment(int_image, line_segment, color):
    '''
    draws a 2d line segment onto an int_image
    
    int_image    : an int_image to draw the line segment onto
    line segment : coordinates of the start and end points (x0, y0, x1, y1)
    color        : an integer value to set at each pixel the line crosses
    '''
    x0, y0, x1, y1 = line_segment
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
                if x < 0 or y < 0 or y >= int_image.shape[0]:
                    continue
                if x >= int_image.shape[1]:
                    break
                int_image[y,x] = color
    
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
                if y < 0 or x < 0 or x >= int_image.shape[1]:
                    continue
                if y >= int_image.shape[0]:
                    break
                int_image[y,x] = color

def rasterize_poly_line(int_image, poly_line, color):
    '''
    draws a poly_line consisting of a series of (x,y) locations
    
    int_image : an int_image to draw the poly_line onto
    poly_line : the coordinates of the line in [(x0, y0), (x1, y1)...] format
    color     : an integer to draw at each location the poly_line touches
    '''
    for i in range(poly_line.shape[0]-1):
        p0 = poly_line[i]
        p1 = poly_line[i+1]
        rasterize_line_segment(
            int_image,
            (p0[0], p0[1], p1[0], p1[1]),
            color,
        )

# legend =======================================================================
def make_legend(colors, width, color_palette=default_palette):
    '''
    makes a legend for a plot
    
    colors : a dictionary mapping names to colors
    '''
    legend = '\n'.join([
        getattr(Fore, color_palette[color]) + name.ljust(width)[:width] +
        Style.RESET_ALL
        for name, color in colors.items()
    ])
    return legend + Style.RESET_ALL

# high level plotting ==========================================================
def plot_poly_lines(
    poly_lines,
    width=80,
    height=20,
    border=None,
    title=None,
    x_range=None,
    y_range=None,
    colors=None,
    legend=False,
    min_max_y=False,
):
    '''
    plot muliple polylines 
    
    poly_lines : a dictionary of {name:poly_line} pairs
    width      : width of the text_image
    height     : height of the text_image
    title      : the title of the plot (None will omit)
    x_range    : the min/max x coordinates of the image
    y_range    : the min/max y coordinates of the image
    colors     : a dictionary of colors to assign to each poly_line
                 'auto' will automatically asign colors,
                 None will assign no colors
    legend     : if True, will add a legend
    min_max_y   : if True, will show the minimum and maximum value of y
    '''
    
    # adjust height/width to account for other elements
    if border == 'line':
        width -= 2
        height -= 2
    elif border == 'top_bottom_line':
        height -= 2
    elif border == 'top_line' or border == 'bottom_line':
        height -= 1
    
    if legend:
        height -= len(poly_lines)
    
    if title:
        height -= 1
    
    if min_max_y:
        height -= 2
    
    if colors is None:
        colors = {name:1 for name in poly_lines}
    elif colors == 'auto':
        colors = {
            name:default_colors[i%len(default_colors)]
            for i, name in enumerate(poly_lines.keys())
        }
    
    content = []
    if border == 'top_line' or border == 'top_bottom_line':
        content.append(hh*(width))
    if title is not None:
        t = ('%s:'%title).ljust(width)[:width]
        content.append(t)
    if legend:
        content.append(make_legend(colors, width))
    
    poly_lines = {k:v for k,v in poly_lines.items() if len(v)}
    
    if len(poly_lines):
        x_min = min(numpy.min(line[:,0]) for line in poly_lines.values())
        x_max = max(numpy.max(line[:,0]) for line in poly_lines.values())
        if x_range is None:
            x_range = (x_min, x_max)
            x_scale = (x_range[1] - x_range[0])
            if x_scale == 0:
                x_range = (x_range[0]-1, x_range[1]+1)
                x_scale = 2
            
        else:
            x_scale = (x_range[1] - x_range[0])
        
        y_min = min(numpy.min(line[:,1]) for line in poly_lines.values())
        y_max = max(numpy.max(line[:,1]) for line in poly_lines.values())
        if y_range is None:
            y_range = (y_min, y_max)
            y_scale = (y_range[1] - y_range[0])
            if y_scale == 0:
                y_range = (y_range[0]-1, y_range[1]+1)
                y_scale = 2
        
        else:
            y_scale = (y_range[1] - y_range[0])
        
        if min_max_y:
            max_line = (
                Style.RESET_ALL + ('Max: %.04f'%y_max).ljust(width))
            content.append(max_line)
        
        image = numpy.zeros((height*4, width*2), dtype=numpy.long)
        
        if x_scale and y_scale:
            for name, poly_line in poly_lines.items():
                if colors is None:
                    color = 1
                else:
                    color = colors[name]
                
                poly_line = numpy.array(poly_line).copy()
                poly_line[:,0] -= x_range[0]
                poly_line[:,0] /= x_scale
                poly_line[:,0] *= width*2-1
                
                poly_line[:,1] -= y_range[0]
                poly_line[:,1] /= y_scale
                poly_line[:,1] = 1. - poly_line[:,1]
                poly_line[:,1] *= height*4-1
                
                rasterize_poly_line(image, poly_line, color)
            
        image = int_image_to_text_image(image, use_colors=True)
        content.append(image)
        
        if min_max_y:
            min_line = (
                Style.RESET_ALL + ('Min: %.04f'%y_min).ljust(width))
            content.append(min_line)
    
    if border == 'bottom_line' or border == 'top_bottom_line':
        content.append(hh*(width))
    
    content = '\n'.join(content)
    if border == 'line':
        content = grid([[content]], width, border='line')

    return content

def grid(text_images, cell_width, border=None):
    '''
    combines a list of text_images into a single grid text image
    
    text_images : the text images that will be arranged into a grid
    '''
    content = []
    
    grid_width = max(len(row) for row in text_images)
    
    w = cell_width
    def h_line(l, h, m, r):
        return l + (w*h + m) * (grid_width-1) + w*h + r
    
    if border == 'line':
        content.append(h_line(tl, hh, tm, tr))
    elif border == 'spaces':
        content.append(h_line(ss, ss, ss, ss))
    
    #rows = math.ceil(len(text_images)/grid_width)
    for i, row in enumerate(text_images):
        #row_cells = text_images[i*grid_width:(i+1)*grid_width]
        #row_cells = [rc.split('\n') for rc in row_cells]
        row_cells = [r.split('\n') for r in row]
        while len(row_cells) < grid_width:
            row_cells.append([ss*w] * len(row_cells[0]))
        for lines in zip(*row_cells):
            if border == 'line':
                line = vv + vv.join(lines) + vv
            elif border == 'spaces':
                line = ss + ss.join(lines) + ss
            elif border is None:
                line = ''.join(lines)
            else:
                raise ValueError('"border" must be "line", "spaces" or None')
            content.append(line)
        
        if i != len(text_images)-1:
            if border == 'line':
                content.append(h_line(ml, hh, mm, mr))
            elif border == 'spaces':
                content.append(h_line(ss, ss, ss, ss))
    
    if border == 'line':
        content.append(h_line(bl, hh, bm, br))
    elif border == 'spaces':
        content.append(h_line(ss, ss, ss, ss))
    
    content = '\n'.join(content)
    
    return content
