import time
import math
import pickle

from conspiracy.log import Log, plot_logs, plot_logs_grid

n = 50001

# make some data
# notice we are putting some sleeps in here to mess with the wall-clock time
cos = Log()
sin = Log()
lin = Log()
zero = Log()

for i in range(n):
    cos.log(math.cos(i/10000 * math.pi))
    sin.log(math.sin(i/25000 * math.pi))
    if i % 5000 == 0:
        time.sleep(0.1)

for i in range(n):
    lin.log(i/(n-1) * 2 - 1)
    zero.log(0.)
    if i % 10000 == 0:
        time.sleep(0.2)

# plot all four functions in one screen using the step index as the x-axis
plot = plot_logs(
    {'cos':cos, 'sin':sin, 'lin':lin, 'zero':zero},
    colors='auto',
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
    colors='auto',
    border='top_line',
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
    colors='auto',
    border='line',
    title='Super cool plot',
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
    colors='auto',
    legend=True,
    min_max_y=True,
    border='line',
)
print(plot)

plot = plot_logs(
    {'cos':cos, 'lin':lin},
    colors='auto',
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
    colors='auto',
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
    colors='auto',
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
