from plot import plot_poly_lines

class Pane:
    def display(self):
        chart = self.render()
        print(chart)

class SinglePane(Pane):
    def __init__(self,
        logs,
        x_coord='step',
        *args,
        **kwargs
    ):
        self.logs = logs
        self.x_coord = x_coord
        self.render_args = args
        self.render_kwargs = kwargs
    
    def render(self):
        poly_lines = {
            name:log.to_poly_line(self.x_coord)
            for name, log in self.logs.items()
        }
        return plot_poly_lines(
            poly_lines, *self.render_args, **self.render_kwargs)

class GridPane(Pane):
    def __init__(self,
        logs,
        layout,
        width=80,
        height=20,
        border=None,
        *args,
        **kwargs,
    ):
        self.logs = logs
        self.layout = layout
        self.width = width
        self.height = height
        self.grid_width = max(len(row) for row in self.layout)
        self.cell_width = self.width // self.grid_width - 2
        self.cell_height = self.height // len(self.layout)
        self.border = border
        self.render_args = args
        self.render_kwargs = kwargs
    
    def render(self):
        plots = []
        
        n = 0
        for i, row in enumerate(self.layout):
            plots.append([])
            for j, log_names in enumerate(row):
                cell_logs = {name : self.logs[name] for name in log_names}
                cell_colors = {name : self.colors[name] for name in log_names}
                cell_lines = {
                    name:log.to_poly_line(x_coord, x_range=x_range)
                    for name, log in cell_logs.items()
                }
                cell_plot = plot_poly_lines(
                    cell_lines,
                    width = self.cell_width,
                    height = self.cell_height,
                    colors = cell_colors,
                    *self.render_args,
                    **self.render_kwargs
                )
        
        return grid(plots, self.cell_width, border=self.border)
