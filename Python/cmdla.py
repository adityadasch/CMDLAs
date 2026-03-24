from dataclasses import dataclass
import re
from typing import List, Tuple
from plum import dispatch
import pathlib
from colorama import Fore, Style, init

init(autoreset=True)

@dataclass
class Parameter:
    key: str
    alias: Tuple[str]

    def __eq__(self, other):
        if isinstance(other, str):
            return self.key == other or other in self.alias
        return False
    
    def __contains__(self, other):
        return self.__eq__(other)

class Command:
    def __init__(self, name:str, alias:Tuple[str] = [], default_param:str = '_',acceptsArgs:bool = True, accepted_param:Tuple[Parameter|str] = [], function: callable = None):    
        # Gaurdrails
        all_alias_accepted = []
        for par in accepted_param:
            if isinstance(par,Parameter):
                all_alias_accepted.append(par.key)
                for alias in par.alias:
                    all_alias_accepted.append(alias)
            else:
                all_alias_accepted.append(par)
        if accepted_param and (default_param not in all_alias_accepted):
            raise ValueError(f"Default param '{default_param}' not found in accepted_param list")
        if function is not None and not callable(function):
            raise TypeError("function must be callable")
        if not all(isinstance(a, str) for a in alias):
            raise TypeError("All aliases must be strings")
        if not all(isinstance(p, (Parameter, str)) for p in accepted_param):
            raise TypeError("accepted_param must contain only Parameter or str")
        del all_alias_accepted

        # Init
        self.name = name
        self.alias = alias
        self.default_param = accepted_param[accepted_param.index(default_param)].key \
            if len(accepted_param)!=0 else default_param
        self.bindedFunc:callable = function
        self.acceptsArgs:bool = acceptsArgs
        self.accepted = accepted_param # Empty => Any

    def __eq__(self, other):
        if isinstance(other, str):
            return self.name == other or other in self.alias
        return False
    
    def __repr__(self):
        return f'''{self.name.upper()}:\n\t{', '.join([x for x in self.alias])}\t Default param:{self.default_param}'''


class Registrar:
    def __init__(self):
        self.prompt:str = '>' # What should be printed before input?
        self.commands:list[Command] = [] # Commands
        self.quitCommand = -1

    @dispatch
    def AddToRegistrar(self, cmd: Command):
        if not isinstance(cmd, Command):
            raise TypeError("Only Command objects can be registered")

        self.commands.append(cmd)

    @dispatch
    def AddToRegistrar(self, cmd: Tuple):
        for ind,ele in enumerate(cmd):
            if not isinstance(ele,Command):
                raise TypeError(f'Command at index {ind} is of type {ind.__class__.__name__}, expected type Command')
            self.commands.append(ele)
    
    def AddMulToRegistrar(self, cmd: Tuple[Command]):
        for ind,ele in enumerate(cmd):
            if not isinstance(ele,Command):
                raise TypeError(f'Command at index {ind} is of type {ind.__class__.__name__}, expected type Command')
            self.commands.append(ele)

    def RollBack(self) -> Command:
        if not self.commands:
            raise IndexError("No commands to roll back")

        return self.commands.pop()

    def RemoveFromRegistrar(self, name:str):
        try: indx = self.commands.index(name) 
        except ValueError: 
            raise KeyError(f'"{name}" is not a valid command')
        return self.commands.pop(indx)
    
    def GetInfo(self,name:str):
        try: indx = self.commands.index(name) 
        except ValueError: 
            raise KeyError(f'"{name}" is not a valid command')
        print(self.commands[indx])
    
    def SetQuitCmd(self, cmd: Command = None, index: int = None):
        if cmd is not None:
            self.commands.append(cmd)
            self.quitCommand = len(self.commands)-1
        elif index is not None:
            if index >= len(self.commands): 
                raise ValueError(f'{index} is greater than length of registered commands list')
            self.quitCommand = index
        else:
            raise ValueError('Excepted one of two arguments: cmd or index')
        
    def BindFunction(self, name:str, func:callable):
        try:indx = self.commands.index(name)
        except ValueError:
            raise KeyError(f'{name} is not a valid command')
        if not callable(func):
            raise TypeError('The function to be bound must be callable')
        cmd = self.commands[indx]
        cmd.bindedFunc = func

    def GetCommandAt(self, name:str):
        try:indx = self.commands.index(name)
        except ValueError:
            raise KeyError(f'{name} is not a valid command')
        return self.commands[indx]
    

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
            

APP = Registrar()


class Interface:
    currentReg:Registrar = APP
    doHelp: bool = False
    help_docs_path: str = 'description.json'
    _runFlag:bool = True
    _isFromCmd:bool = True
    _listIndex: int
    _listInput:list[str]
    _helpClass: "Help"

    @classmethod
    def _Quit(cls):
        cls._runFlag = False

    @classmethod
    def TakeListInput(cls, input_: list[str]):
        cls._listIndex = -1
        cls._listInput = input_
        cls._isFromCmd = False

    @staticmethod
    def _CreateOptionArg(remain:str, default: str, cmd_input_bool: bool, accept: list[Parameter|str]) -> dict[str: str]:
        'Format: [default_arg] -a [] -b [] -c []'
        hasOptions = remain.find('-')
        hasFlags = remain.find('&')

        if (hasOptions == -1 and hasFlags == -1):
            cmd_args = dict() if cmd_input_bool else {default: remain.strip()} 
            return cmd_args

        # Check if there is no option or flag after command, if so append the default
        
        if remain[0] not in '-&': # does not include option
            remain = f'-{default} ' + remain

        option_list = re.findall(r'-[^-]*', remain) # ['-a IN', '-b C']
        option:dict = dict()
        for op in option_list:
            # '-a IN'
            splitOption = re.split(r"\s", op, maxsplit=1)
            option_name = splitOption[0]
            option_data = True if len(splitOption[1]) == 0 else splitOption[1].strip()

            option_name = option_name[1::]

            if len(accept)==0 or option_name in accept:
                index = accept.index(option_name)
                param = accept[index]
                option[param.key] = option_data
            
        
        
        return option

    @classmethod
    def _FetchInput(cls):
        if cls._isFromCmd:
            return input(cls.currentReg.prompt) + ' '
        else:
            cls._listIndex += 1
            text = cls._listInput[cls._listIndex]
            print('{}{}'.format(cls.currentReg.prompt, text))
            return text + ' '

    @classmethod
    def StartLoop(cls):
        if cls.doHelp:
            cls._helpClass = HelpProvider(cls.currentReg, pathlib.Path(cls.help_docs_path)).GenerateHelpCommand()
            
            try: cls.currentReg.GetInfo('help')
            except KeyError:#Doesn't exist
                cls.currentReg.AddToRegistrar(Command('help',('h'),acceptsArgs=False,function=cls._helpClass.print_help))
            else: cls.currentReg.GetCommandAt('help').bindedFunc = cls._helpClass.print_help

        if cls.currentReg.quitCommand != -1:
            quitCmd = cls.currentReg.commands[cls.currentReg.quitCommand]
            cls.currentReg.BindFunction(quitCmd.name, cls._Quit) # Bind quit command to Quit function to flip the flag

        while cls._runFlag:
            user = cls._FetchInput()

            cmd_text = user[:user.find(' ')]
            try:
                cmd = cls.currentReg.GetCommandAt(cmd_text)
            except:
                print('Command not recognised')
                continue
            try:
                if cmd.acceptsArgs:
                    remain = user.removeprefix(cmd_text).lstrip()
                    options = Interface._CreateOptionArg(remain, cmd.default_param, len(user.rstrip()) == len(cmd_text), cmd.accepted) 
                    cmd.bindedFunc(**options)
                else:
                    cmd.bindedFunc()
            except TypeError:
                print('Command to be implemented')