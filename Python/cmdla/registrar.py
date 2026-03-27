from .dataclasses import Command, Tuple
from plum import dispatch

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
