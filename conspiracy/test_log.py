import math

from conspiracy.log import SynchronousConsecutiveLog

log = SynchronousConsecutiveLog('cos', 'sin', 'lin', 'neg', compressed=True)

n = 50001
print_i = 1000

for i in range(n):
    log.log(cos=math.cos(i/10000 * math.pi))
    log.log(sin=math.sin(i/10000 * math.pi))
    log.log(lin=i/(n-1) * 2 - 1.)
    log.log(neg=-(i/(n-1) * 2 - 1.))
    log.step()
    
    if i%print_i == 0:
        print(log.plot(legend=True, minmax_y=True, width=80, height=40))
