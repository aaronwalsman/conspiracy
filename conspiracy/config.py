import os
from configparser import ConfigParser
import argparse
import json

class Config:
    '''
    A class for high-level constant configurations.
    To use this, create a subclass with class-level configuration values.
    Thsee can then be automatically parsed from the command line and from
    configuration (.cfg) files.
    
    Supports multiple inheritance, so that one config class can inherit values
    from many others with typical resolution order.
    
    This class supports bool, int, float, str and nested-json values for
    constants, although json is somewhat clunky to specify on the command line.
    
    example1.py:
    from ltron_torch.config import Config
    class MyTrainingConfig(Config):
        learning_rate = 3e-4
        momentum = 0.9
    
    config = MyTrainingConfig.from_commandline()
    print('learning_rate:', config.learning_rate)
    print('momentum:', config.momentum)
    
    command line:
    python example1.py --learning-rate 0.001
    learning_rate: 0.001
    momentum: 0.9
    '''
    
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
    
    def __setattr__(self, attr, value):
        if not hasattr(self.__class__, attr):
            raise AttributeError('Invalid Config Attribute: %s'%attr)
        super().__setattr__(attr, value)
    
    @classmethod
    def primary_attrs(cls):
        return [d for d in dir(cls) if
            d[:2] != '__' and
            not callable(getattr(cls, d))
        ]
    
    @classmethod
    def from_commandline(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('--config', type=str, default=None)
        parser.add_argument('--config-section', type=str, default='CONFIG')
        for primary_attr in cls.primary_attrs():
            default_value = getattr(cls, primary_attr)
            argtype = type(default_value)
            if argtype not in (str, int, float):
                argtype = str
            parser.add_argument(
                '--' + primary_attr.replace('_', '-'),
                type=argtype,
                default=None,
                help="default: %s"%(default_value,))
        
        args = parser.parse_args()
        config_path = args.config
        config_section = args.config_section
        
        parser = ConfigParser(allow_no_value=True)
        if config_path is not None:
            parser.read_file(open(os.path.expanduser(config_path)))
        
        if not parser.has_section(config_section):
            parser[config_section] = {}
        
        for key, value in vars(args).items():
            if key in ('config', 'config_section'):
                continue
            if value is not None:
                parser[config_section][key] = str(value)
        
        return cls.load_config(parser, section=config_section)
    
    @classmethod
    def translate(cls, other, **kwargs):
        args = {}
        for primary_attr in cls.primary_attrs():
            if primary_attr in kwargs:
                source_name = kwargs[primary_attr]
            else:
                source_name = primary_attr
            if hasattr(other, source_name):
                args[primary_attr] = getattr(other, source_name)
        for kwarg in kwargs:
            if not hasattr(cls, kwarg):
                raise AttributeError('The attribute "%s" does not exist'%kwarg)
        return cls(**args)
    
    @classmethod
    def load_config(cls, cfg, section='CONFIG'):
        args = {}
        if isinstance(cfg, ConfigParser):
            parser = cfg
        else:
            parser = ConfigParser(allow_no_value=True)
            parser.read_file(open(os.path.expanduser(cfg)))
        for name in parser[section]:
            try:
                args[name] = parser[section].getint(name)
                continue
            except ValueError:
                pass
            
            try:
                args[name] = parser[section].getboolean(name)
                continue
            except ValueError:
                pass
            
            try:
                args[name] = parser[section].getfloat(name)
                continue
            except ValueError:
                pass
            
            value = parser[section][name]
            try:
                value = json.loads(value)
            except(json.decoder.JSONDecodeError):
                pass
            
            args[name] = value
        
        return cls(**args)
    
    def as_dict(self):
        return {attr : getattr(self, attr) for attr in self.primary_attrs()}
    
    def __str__(self):
        s = self.__class__.__name__ + '\n'
        for attr in self.primary_attrs():
            s += '  %s : %s\n'%(attr, getattr(self, attr))
        return s
    
    def write_config(self, file_path, section='CONFIG'):
        file_path = os.path.expanduser(file_path)
        parser = ConfigParser(allow_no_value=True)
        try:
            parser.read_file(open(file_path))
        except FileNotFoundError:
            pass
        parser[section] = self.as_dict()
        with open(file_path, 'w') as f:
            parser.write(f)
