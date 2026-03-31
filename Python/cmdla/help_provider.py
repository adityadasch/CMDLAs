import pathlib
from .registrar import Registrar
from colorama import Fore, Style, init
from .dataclasses import Parameter

init(autoreset=True)

class HelpProvider: 
    def __init__(self, registrar: Registrar, description_file: str|pathlib.Path = pathlib.Path('description.json')): 
        if not isinstance(description_file, (str, pathlib.Path)): 
            raise TypeError( f"Invalid path type: {description_file.__class__.__name__}. Expected str or pathlib.Path." ) 
        if not isinstance(registrar, Registrar):
            raise TypeError(f'Excpected Registrar type, got {registrar.__class__.__name__}')

        self.description_file: pathlib.Path = description_file if isinstance(description_file, pathlib.Path) else \
        pathlib.Path(description_file)
        self.reg = registrar
    
    def _load_desc(self):
        import json
        try:
            with self.description_file.open(encoding='utf-8') as fp:
                data = json.load(fp)
        except FileNotFoundError:
            raise ValueError(f'File {self.description_file.name} doesn\'t exist')
        except json.JSONDecodeError:
            raise SyntaxError('JSON with correct syntax is not provided')
        except UnicodeDecodeError:
            raise ValueError(f"File {self.description_file.name} could not be decoded with UTF-8")
        return data

    
    def GenerateHelpCommand(self):
        '''
        Available functions YELLOW:
        \t <propmt RED> cmd1GREEN [<alias> CYAN]:
        \t\t <description BRIGHT WHITE>
        \t\t Accepted ParamsYELLOW: <parameters>
        \t\t -Param1CYAN: <param_desc>
        '''

        class Help:
            reg:Registrar
            desc: dict = None
    
            @classmethod
            def print_help(cls):
                desc = cls.desc
                print(Fore.YELLOW+Style.BRIGHT+'Available functions')
                for cmd, data in desc.items():
                    print(Fore.RED+cls.reg.prompt+Style.RESET_ALL+Fore.GREEN+Style.BRIGHT+cmd,end='')
                    print(f'{Fore.CYAN}[{Style.BRIGHT+','.join([alias for alias in cls.reg.GetCommandAt(cmd).alias])+Style.NORMAL}]:')
                    print(f'\t{data[0]}')
                    print(f'\t{Fore.YELLOW}Accepted Parameters{Style.RESET_ALL}: {', '.join([arg if isinstance(arg,str) else arg.key for arg in cls.reg.GetCommandAt(cmd).accepted])}')
                    for arg in cls.reg.GetCommandAt(cmd).accepted:
                        if isinstance(arg, str):
                            print(f'\t{Fore.CYAN}{arg}: {data[1][arg]}')
                        elif isinstance(arg, Parameter):
                            print(f'\t{Fore.CYAN}{arg.key}{Style.DIM}[{','.join([alias for alias in arg.alias])}]{Style.RESET_ALL}: {data[1][arg.key]}')

        Help.reg,Help.desc = self.reg, self._load_desc()
        return Help