import argparse
import importlib
import pkgutil
import os.path
from Hako.Console.Parser import Parser


class Kernel:
    def __init__(self, app_path):
        self.app_path = os.path.dirname(app_path) + '/commands'
        self.framework_path = os.path.join(os.path.dirname(__file__), './Commands')
        self.commands = []
    
    # Load all commands and attempt to match the user input to them
    def handle(self):
        self.commands = self.load_commands()
        parent = argparse.ArgumentParser(description='Zen CLI', add_help=False)
        parent.add_argument('command_name', help='Name of the command you would like to run.')
        args, unknown = parent.parse_known_args()

        try:
            cmd = self.commands[args.command_name]
            if cmd['params']:
                cmd['instance']._params = cmd['params']
                parser = argparse.ArgumentParser(prog=cmd['name'])
                parser.add_argument('command_name', help=argparse.SUPPRESS)
                for key, param in cmd['params'].items():
                    param.to_args(parser)
            
                cmd_args, unknown_cmd_args = parser.parse_known_args()
                cmd['instance']._param_values = cmd_args
            cmd['instance'].handle()
        except KeyError:
            print('Command "%s" not found, is it registered?' % (args.command_name))
            # raise e ?

    # Load commands from framework and user app locations
    def load_commands(self, prefix='commands.'):
        from_framework = self.load_from_path(self.framework_path)
        from_app = self.load_from_path(self.app_path, prefix=prefix)
        return {**from_framework, **from_app}

    # Import all submodules from a given path and prefix
    def load_from_path(self, path, prefix='Hako.Console.Commands.'):
        loaded = {}
        packages = pkgutil.walk_packages([path], prefix)
        for finder, module_name, is_pkg in packages:
            if not is_pkg:
                imported = importlib.import_module(module_name)
                module = getattr(imported, module_name.split('.')[-1])
                instance = module()
                name, params = Parser.parse(instance.signature)
                loaded[name] = {
                    'module': module,
                    'instance': instance,
                    'name': name,
                    'params': params,
                    'signature': instance.signature,
                    'description': 'example description'
                }
        return loaded