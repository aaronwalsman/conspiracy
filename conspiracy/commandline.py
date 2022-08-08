from argparse import ArgumentParser
import pickle
import json

from conspiracy.log import Log
from conspiracy.plot import plot_logs, color_name_to_index

def plot_checkpoint():
    parser = ArgumentParser()
    parser.add_argument('checkpoint', type=str, nargs='+')
    parser.add_argument('--keys', nargs='*')
    parser.add_argument('--x-coord', type=str, default='step')
    parser.add_argument('--xrange', type=float, nargs=2, default=(0., 1.))
    parser.add_argument('--format', type=str, default='pickle')
    parser.add_argument('--height', type=int, default=20)
    parser.add_argument('--width', type=int, default=80)
    
    args = parser.parse_args()
    
    all_colors = [k for k in color_name_to_index.keys() if k != 'WHITE']
    
    if args.format == 'torch':
        import torch
    
    logs = {}
    colors = {}
    for i, checkpoint_path in enumerate(args.checkpoint):
        print('Loading: %s'%checkpoint_path)
        if args.format == 'pickle':
            checkpoint_data = pickle.load(open(checkpoint_path, 'rb'))
        elif args.format == 'json':
            checkpoint_data = json.load(open(checkpoint_path))
        elif args.format == 'torch':
            checkpoint_data = torch.load(
                checkpoint_path, map_location=torch.device('cpu'))
        for key in args.keys:
            try:
                key = int(key)
            except ValueError:
                pass
            checkpoint_data = checkpoint_data[key]
        
        log = Log(state=checkpoint_data)
        logs[checkpoint_path] = log
        colors[checkpoint_path] = all_colors[i % len(all_colors)]
    
    chart = plot_logs(
        logs,
        colors=colors,
        title='[' + ']['.join(args.keys) + ']',
        legend=True,
        border='line',
        height=args.height,
        width=args.width,
        x_coord=args.x_coord,
        x_range=args.xrange,
        min_max_y=True,
    )
    print(chart)
