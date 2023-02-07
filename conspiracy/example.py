import random
import time
import math
import pickle

from conspiracy.log import Log
from conspiracy.plot import plot_logs, plot_logs_grid

# make some data
cos = Log()
sin = Log()
lin = Log()
zero = Log()

for epoch in range(1,11):
    print('Epoch: %i'%epoch)
    for i in range(5000*(epoch-1), 5000*epoch):
        cos.log(math.cos(i/10000 * math.pi))
        sin.log(math.sin(i/25000 * math.pi))
    
    for i in range(5000*(epoch-1), 5000*epoch):
        lin.log(i/(50000-1) * 2 - 1)
        zero.log(0.)
        
    plot = plot_logs(
        {'cos':cos, 'sin':sin, 'lin':lin, 'zero':zero},
        colors={'cos':'RED', 'sin':'BLUE', 'lin':'YELLOW', 'zero':'GREEN'},
        border='top_line',
        legend=True,
        min_max_y=True,
        width=80,
        height=20,
        x_coord='step',
    )
    print(plot)

# plot cosine and linear using absolute wall-clock time as the x-axis
plot = plot_logs(
    {'cos':cos, 'lin':lin},
    colors={'cos':'RED', 'sin':'BLUE', 'lin':'YELLOW', 'zero':'GREEN'},
    border='top_line',
    title='Wall Clock',
    legend=True,
    min_max_y=True,
    width=80,
    height=20,
    x_coord='time',
)
print(plot)

# plot cosine and linear using relative wall-clock time on the x-axis
plot = plot_logs(
    {'cos':cos, 'lin':lin},
    colors={'cos':'RED', 'sin':'BLUE', 'lin':'YELLOW', 'zero':'GREEN'},
    border='line',
    title='Relative Time',
    legend=True,
    min_max_y=True,
    width=80,
    height=20,
    x_coord='relative_time',
)
print(plot)

plot = plot_logs_grid(
    [[{'cos':cos}, {'sin':sin}],
     [{'lin':lin, 'zero':zero}],
    ],
    colors={'cos':'RED', 'sin':'BLUE', 'lin':'YELLOW', 'zero':'GREEN'},
    legend=True,
    min_max_y=True,
    border='line',
)
print(plot)

plot = plot_logs(
    {'cos':cos, 'lin':lin},
    colors={'cos':'RED', 'sin':'BLUE', 'lin':'YELLOW', 'zero':'GREEN'},
    border='line',
    title='Super cool plot',
    legend=True,
    min_max_y=True,
    width=80,
    height=20,
    x_coord='step',
    x_range=(0.,1.),
)
print(plot)

plot = plot_logs(
    {'cos':cos, 'lin':lin},
    colors={'cos':'RED', 'sin':'BLUE', 'lin':'YELLOW', 'zero':'GREEN'},
    border='line',
    title='Super cool plot',
    legend=True,
    min_max_y=True,
    width=80,
    height=20,
    x_coord='step',
    x_range=(0.2,1.),
)
print(plot)

plot = plot_logs(
    {'cos':cos, 'lin':lin},
    colors={'cos':'RED', 'sin':'BLUE', 'lin':'YELLOW', 'zero':'GREEN'},
    border='line',
    title='Super cool plot',
    legend=True,
    min_max_y=True,
    width=80,
    height=20,
    x_coord='step',
    x_range=(0.5,1.),
)
print(plot)

cos_noise = Log(capacity=5000)
sin_noise = Log(capacity=5000)

for epoch in range(1,11):
    print('Epoch: %i'%epoch)
    for i in range(50*(epoch-1), 50*epoch):
        cos_noise.log(math.cos(i/100 * math.pi) + random.random() * 0.75)
        sin_noise.log(math.sin(i/250 * math.pi) + random.random() * 0.25)
        
    plot = plot_logs(
        {'cos':cos_noise, 'sin':sin_noise},
        colors={'cos':'RED', 'sin':'BLUE'},
        border='line',
        legend=True,
        min_max_y=True,
        width=80,
        height=20,
        x_coord='step',
        windowed_mean_std=100,
    )
    print(plot)
