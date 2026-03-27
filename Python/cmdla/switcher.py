from .interface import Interface, Registrar, APP

class AllSwitch:
    dictionary: dict = {'global': APP}

def Switch(**kwarg):
    name = kwarg.get('name')
    if name:
        Interface.currentReg = AllSwitch.dictionary[name]
        global APP
        APP = Interface.currentReg

def Add(name:str, reg: Registrar):
    if isinstance(reg, Registrar):
        AllSwitch.dictionary[name] = reg
    else:
        raise TypeError(f'Expected type Registrar but got {reg.__class__.__name__}')