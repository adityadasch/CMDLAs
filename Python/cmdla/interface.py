from .registrar import Registrar
from .dataclasses import HelpSettings, Command, Parameter
from .help_provider import HelpProvider,pathlib
import re


GLOBAL = Registrar()

class Interface:
    currentReg:Registrar = GLOBAL
    helpSettings: HelpSettings = HelpSettings()
    doHelp: bool = False
    help_docs_path: str = 'description.json'
    existSwitch: bool = False
    switchCommand: Command = None
    _runFlag:bool = True
    _isFromCmd:bool = True
    _listIndex: int
    _listInput:list[str]
    _quitCmd: Command= None

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
        cls.createHelpFunc()

        while cls._runFlag:
            user = cls._FetchInput()

            cmd_text = user[:user.find(' ')]
            if cls.existSwitch and cls.switchCommand == cmd_text:
                remain = user.removeprefix(cmd_text).lstrip()
                options = Interface._CreateOptionArg(remain, cls.switchCommand.default_param, len(user.rstrip()) == len(cmd_text), cls.switchCommand.accepted) 
                cls.switchCommand.bindedFunc(**options)
                continue
            if cls._quitCmd is not None and cls._quitCmd == cmd_text:
                cls._quitCmd.bindedFunc()
                continue
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

    @classmethod
    def createHelpFunc(cls):
        if cls.doHelp:
            if cls.currentReg.help_docs_path is None:
                print(f'The registrar({cls.currentReg.prompt}) doesn\'t have a help docs path')
                return
            
            if  cls.currentReg.helpClass is None:
                cls.currentReg.helpClass = HelpProvider(cls.currentReg, pathlib.Path(cls.currentReg.help_docs_path)).GenerateHelpCommand()
            else:
                return
            
            try: cls.currentReg.GetInfo('help')
            except KeyError:#Doesn't exist
                cls.currentReg.AddToRegistrar(Command(**cls.helpSettings.asDict, function=cls.currentReg.helpClass.print_help))   
            else: cls.currentReg.GetCommandAt('help').bindedFunc = cls.currentReg.helpClass.print_help
    
    @classmethod
    def SetQuitCmd(self, cmd: Command = None):
        '''cmd: Unbinded command'''
        if cmd is not None:
            self._quitCmd = cmd
            self._quitCmd.bindedFunc = self._Quit
        else:
            self._quitCmd = Command('quit',('q',),acceptsArgs=False, function=self._Quit)