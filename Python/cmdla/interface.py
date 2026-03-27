from .registrar import Registrar
from .dataclasses import HelpSettings, Command, Parameter
from .help_provider import HelpProvider,pathlib
import re


APP = Registrar()

class Interface:
    currentReg:Registrar = APP
    helpSettings: HelpSettings = HelpSettings()
    doHelp: bool = False
    help_docs_path: str = 'description.json'
    _runFlag:bool = True
    _isFromCmd:bool = True
    _listIndex: int
    _listInput:list[str]
    _helpClass: "Help" # type: ignore

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
                cls.currentReg.AddToRegistrar(Command(**cls.helpSettings.asDict, function=cls._helpClass.print_help))   
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