import os

from argparse import ArgumentParser
import pickle
import json

from conspiracy.log import Log
from conspiracy.plot import plot_logs, color_name_to_index

def plot_logfiles(
    log_paths,
    file_format,
    keys,
    height=20,
    width=80,
    x_coord='step',
    x_range=(0., 1.),
):
    
    if file_format == 'torch':
        import torch
    
    all_colors = [
        k for k in color_name_to_index.keys()
        if k != 'WHITE' and k != 'EMPTY'
    ]
    
    logs = {}
    colors = {}
    for i, log_path in enumerate(log_paths):
        print('Loading: %s'%log_path)
        if file_format == 'pickle':
            checkpoint_data = pickle.load(open(log_path, 'rb'))
        elif file_format == 'json':
            checkpoint_data = json.load(open(log_path))
        elif file_format == 'torch':
            checkpoint_data = torch.load(
                log_path, map_location=torch.device('cpu'))
        for key in keys:
            try:
                key = int(key)
            except ValueError:
                pass
            checkpoint_data = checkpoint_data[key]
        
        log = Log(state=checkpoint_data)
        logs[log_path] = log
        colors[log_path] = all_colors[i % len(all_colors)]
    
    chart = plot_logs(
        logs,
        colors=colors,
        title='[' + ']['.join(keys) + ']',
        legend=True,
        border='line',
        height=height,
        width=width,
        x_coord=x_coord,
        x_range=x_range,
        min_max_y=True,
    )
    print(chart)

def plot_checkpoint():
    parser = ArgumentParser()
    parser.add_argument('logs', type=str, nargs='+')
    parser.add_argument('--keys', nargs='*')
    parser.add_argument('--x-coord', type=str, default='step')
    parser.add_argument('--x-range', type=float, nargs=2, default=(0., 1.))
    parser.add_argument('--format', type=str, default='json')
    parser.add_argument('--height', type=int, default=20)
    parser.add_argument('--width', type=int, default=80)
    
    args = parser.parse_args()
    
    plot_logfiles(
        args.logs,
        args.format,
        args.keys,
        height=args.height,
        width=args.width,
        x_coord=args.x_coord,
        x_range=args.x_range,
    )

def plot_directory():
    parser = ArgumentParser()
    parser.add_argument('directory', type=str, nargs='+')
    parser.add_argument('--omit', type=str, nargs='+', default=[])
    parser.add_argument('--name-prefix', type=str, default='log')
    parser.add_argument('--keys', nargs='*')
    parser.add_argument('--x-coord', type=str, default='step')
    parser.add_argument('--x-range', type=float, nargs=2, default=(0., 1.))
    parser.add_argument('--format', type=str, default='json')
    parser.add_argument('--height', type=int, default=20)
    parser.add_argument('--width', type=int, default=80)
    
    args = parser.parse_args()
    
    all_colors = [
        k for k in color_name_to_index.keys()
        if k != 'WHITE' and k != 'EMPTY'
    ]
    
    if args.format == 'torch':
        import torch
    
    def recurse_directory(directory):
        sub_directories = [
            os.path.join(directory, d) for d in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, d))
            and not any(omit in d for omit in args.omit)
        ]
        matching_files = [
            os.path.join(directory, f) for f in os.listdir(directory)
            if not os.path.isdir(os.path.join(directory, f))
            and f.startswith(args.name_prefix)
        ]
        
        for sub_directory in sub_directories:
            matching_files = matching_files + recurse_directory(sub_directory)
        
        return matching_files
    
    matching_files = []
    for directory in args.directory:
        matching_files = matching_files + recurse_directory(directory)
    
    bundled_files = {}
    for matching_file in matching_files:
        d, f = os.path.split(matching_file)
        if d not in bundled_files:
            bundled_files[d] = []
        bundled_files[d].append(matching_file)
    
    most_recent_files = []
    for directory, files in bundled_files.items():
        file_times = [os.path.getmtime(f) for f in files]
        most_recent_file = max(zip(file_times, files))[1]
        most_recent_files.append(most_recent_file)
    
    plot_logfiles(
        most_recent_files,
        args.format,
        args.keys,
        height=args.height,
        width=args.width,
        x_coord=args.x_coord,
        x_range=args.x_range,
    )
