# Terminal Plotting Using Conspiracy
The main semantics are to use a `Log` object to store values, the use `plot_logs` to display them.  Example:
```
from conspiracy import Log, plot_logs
my_log = Log(capacity=1024)
for i in range(5000):
  my_log.log(i)

chart = plot_logs(
  {'my_log':my_log},
  colors={'my_log':'RED'},
  border='line',
  legend=True,
  min_max_y=True,
)
print(chart)
```

The `capacity` argument of `Log` indicates how many values are stored in the log.
When you overrun the capacity, the log starts compressing (and averaging) the data stored inside it.
`capacity` can also be `'adaptive'` in which case the log will continue to grow to store all logged data.
See `conspiracy/example.py` for more examples.
