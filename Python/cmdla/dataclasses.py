from dataclasses import dataclass
from typing import List, Tuple

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
                for alias_ in par.alias:
                    all_alias_accepted.append(alias_)
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

@dataclass
class HelpSettings:
    _name: str = 'help'
    _alias:Tuple[str] = ('h',)

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value:str):
        if isinstance(value, str):self._name = value
        else:
            raise TypeError(f'Name assignment not supported for {value.__class__.__name__}')
    @property
    def alias(self):
        return self._alias
    @alias.setter
    def alias(self, value:Tuple):
        if isinstance(value, tuple):self._alias = value
        else:
            raise TypeError(f'Alias assignment not supported for {value.__class__.__name__}')
    
    @property
    def asDict(self)->dict:
        return {"name":self.name,"alias":self.alias, "acceptsArgs":False}
