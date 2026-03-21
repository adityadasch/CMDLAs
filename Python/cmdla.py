from dataclasses import dataclass
import re

@dataclass
class Parameter:
    key: str
    alias: list[str]

    def __eq__(self, other):
        if isinstance(other, str):
            return self.key == other or other in self.alias
        return False
    
    def __contains__(self, other):
        return self.__eq__(other)

class Command:
    def __init__(self, name:str, alias:list[str] = [], default_param:str = '_',acceptsArgs:bool = True, accepted_param:list[Parameter|str] = []):    
        self.name = name
        self.alias = alias
        self.default_param = accepted_param[accepted_param.index(default_param)].key \
            if len(accepted_param)!=0 else default_param
        self.bindedFunc:callable = None
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

    def AddToRegistrar(self, cmd: Command):
        self.commands.append(cmd)

    def RollBack(self) -> Command:
        return self.commands.pop()

    def RemoveFromRegistrar(self, name:str):
        return self.commands.pop(self.commands.index(name))
    
    def GetInfo(self,name:str):
        print(self.commands[self.commands.index(name)])
    
    def SetQuitCmd(self, cmd: Command = None, index: int = None):
        if cmd is not None:
            self.commands.append(cmd)
            self.quitCommand = len(self.commands)-1
        elif index is not None:
            self.quitCommand = index
        
    def BindFunction(self, name:str, func:callable):
        cmd = self.commands[self.commands.index(name)]
        cmd.bindedFunc = func

    def GetCommandAt(self, name:str):
        return self.commands[self.commands.index(name)]

APP = Registrar()

class Interface:
    currentReg:Registrar = APP
    runFlag:bool = True
    isFromCmd:bool = True
    listIndex: int
    listInput:list[str]

    @classmethod
    def Quit(cls):
        cls.runFlag = False

    @classmethod
    def TakeListInput(cls, input_: list[str]):
        cls.listIndex = -1
        cls.listInput = input_
        cls.isFromCmd = False

    @staticmethod
    def createOptionArg(remain:str, default: str, cmd_input_bool: bool, accept: list[Parameter|str]) -> dict[str: str]:
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
    def fetchInput(cls):
        if cls.isFromCmd:
            return input(cls.currentReg.prompt) + ' '
        else:
            cls.listIndex += 1
            text = cls.listInput[cls.listIndex]
            print('{}{}'.format(cls.currentReg.prompt, text))
            return text + ' '

    @classmethod
    def startLoop(cls):
        quitCmd = cls.currentReg.commands[cls.currentReg.quitCommand]
        cls.currentReg.BindFunction(quitCmd.name, cls.Quit) # Bind quit command to Quit function to flip the flag

        while cls.runFlag:
            user = cls.fetchInput()

            cmd_text = user[:user.find(' ')]
            cmd = cls.currentReg.GetCommandAt(cmd_text)

            if cmd.acceptsArgs:
                remain = user.removeprefix(cmd_text).lstrip()
                options = Interface.createOptionArg(remain, cmd.default_param, len(user.rstrip()) == len(cmd_text), cmd.accepted) 
                cmd.bindedFunc(**options)
            else:
                cmd.bindedFunc()