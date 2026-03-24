from dataclasses import dataclass
import re
from typing import List, Tuple
from plum import dispatch

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
        if accepted_param and default_param not in [p.key if isinstance(p, Parameter) else p for p in accepted_param]:
            raise ValueError(f"Default param '{default_param}' not found in accepted_param list")
        if function is not None and not callable(function):
            raise TypeError("function must be callable")
        if not all(isinstance(a, str) for a in alias):
            raise TypeError("All aliases must be strings")
        if not all(isinstance(p, (Parameter, str)) for p in accepted_param):
            raise TypeError("accepted_param must contain only Parameter or str")

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
    def AddToRegistrar(self, cmd: List[Command]):
        for ind,ele in enumerate(cmd):
            if not isinstance(ele,Command):
                raise TypeError(f'Command at index {ind} is of type {type(ind)}, expected type Command')
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

APP = Registrar()

class Interface:
    currentReg:Registrar = APP
    _runFlag:bool = True
    _isFromCmd:bool = True
    _listIndex: int
    _listInput:list[str]

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
        quitCmd = cls.currentReg.commands[cls.currentReg.quitCommand]
        cls.currentReg.BindFunction(quitCmd.name, cls._Quit) # Bind quit command to Quit function to flip the flag

        while cls._runFlag:
            user = cls._FetchInput()

            cmd_text = user[:user.find(' ')]
            cmd = cls.currentReg.GetCommandAt(cmd_text)

            if cmd.acceptsArgs:
                remain = user.removeprefix(cmd_text).lstrip()
                options = Interface._CreateOptionArg(remain, cmd.default_param, len(user.rstrip()) == len(cmd_text), cmd.accepted) 
                cmd.bindedFunc(**options)
            else:
                cmd.bindedFunc()