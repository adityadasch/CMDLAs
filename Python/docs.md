# Registers
#### - Create a register using the Registrar() class
#### - Setup a custom prompt using register.prompt {Default is >}
#### - Provide a help doc using register.help_docs_path


# Command Class
```
Parameter class
Params:
key: str -> The name of the parameter
alias: Tuple[str] -> [str]
```
---
### Params:
`name: str`-> The name of the command

`alias: Tuple[str]` -> Any and all alias(s) Eg: ('foo', 'bar')

`acceptsArgs: bool` -> If the command is a arged command or not

`accepted_param: Parameter|str` -> All the parameters to be searched

`function: callable` -> Function that can be called when command invoked

# Adding Commands to funcs
<b> Commands can be added to registers using the AddToRegistrar function</b>
Params:
`cmd:Command|Tuple[Command]` -> The (list) of commands to be registered

# Registering Register
Created Registers can be registered using the Add function provided in the switcher submodule if switching between command namespaces is needed

# Registering a switch
Either a command for switch can be created using the Command class or let the interface create one. The default switcher is invoked by command switch and is created by Add()

# Setting up help
Help command invoked by help[h] command by default. To change the settings you can use the following

HelpSettings.name -> changes primary command name

HelpSettings.alias -> provides alias support

*`Interface.doHelp` should be set to `True`*

# Setting up Quit Command
Done by calling Interface.SetQuitCmd() with optional argument of cmd:Command

# Starting loop 
Done by calling Interface.StartLoop

## Utilities
*decorators available in cmdla.utils*

`requires('req1', 'req2',..., 'reqn')` -> Checks if req1, req2,...,reqn are being passed into the function

`requires_typed(req1=type, req2=type,...,reqn=type)` -> Checks if req1, req2,...,reqn are being passed into the function and their types

`validate(req1=filter, req2=filter,...,reqn=filter)` -> Checks if the provided value satisfy callable filter i.e, filter(arg) is `True`