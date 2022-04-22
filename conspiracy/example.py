import time
import math
import pickle

from conspiracy.log import Log, plot_logs, plot_logs_grid

logs = {
    'cos' : Log(),
    'sin' : Log(),
    'lin' : Log(),
    'zero' : Log(),
}

n = 50001

for i in range(n):
    logs['cos'].log(math.cos(i/10000 * math.pi))
    logs['sin'].log(math.sin(i/25000 * math.pi))
    logs['zero'].log(0.)
    if i % 5000 == 0:
        time.sleep(0.1)

for i in range(n):
    logs['lin'].log(i/(n-1) * 2 - 1)
    if i % 10000 == 0:
        time.sleep(0.2)

plot = plot_logs(
    logs,
    colors='AUTO',
    top_line=True,
    legend=True,
    min_max_y=True,
    width=160,
    height=60,
    x_coord='step',
)
print(plot)

plot = plot_logs(
    logs,
    colors='AUTO',
    top_line=True,
    legend=True,
    min_max_y=True,
    width=160,
    height=60,
    x_coord='time',
)
print(plot)

plot = plot_logs(
    logs,
    colors='AUTO',
    top_line=True,
    legend=True,
    min_max_y=True,
    width=160,
    height=60,
    x_coord='relative_time',
)
print(plot)

plot = plot_logs_grid(
    {'cos':logs['cos'], 'sin':logs['sin'], 'lin':logs['lin']},
    colors='AUTO',
    legend=True,
    min_max_y=True,
    border='line',
)
print(plot)
