import numpy

from conspiracy.plot import plot

evil = numpy.array([
    [0,0],
    [1,1],
    [2,0],
    [3,2],
    [4,0],
    [5,3],
    [6,0],
    [7,4]
], dtype=numpy.float)

scheme = numpy.array([
    [0,0],
    [0.5,3],
    [1.75,4],
    [3.25,3],
    [3.75,4],
], dtype=numpy.float)

plots = {
    'evil':evil,
    'scheme':scheme,
}

#image = graph.graph([pline1], 160, 48, colors=[2], x_range=[0,7], y_range=[0,4])
#b_image = graph.image_to_braille(image, use_colors=True)

b_image = plot(plots, 160, 80, legend=True, minmax_y=True)

print(b_image)
