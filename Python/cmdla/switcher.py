from .interface import Interface, Registrar, GLOBAL

class AllSwitch:
    dictionary: dict = {'global': GLOBAL}

def Switch(**kwarg):
    '''name: Name of the registrar'''
    name = kwarg.get('name')
    if name and name!='.':
        Interface.currentReg = AllSwitch.dictionary[name]
    else:
        Interface.currentReg = AllSwitch.dictionary['global']

    Interface.createHelpFunc()

def Add(name:str, reg: Registrar):
    if isinstance(reg, Registrar):
        AllSwitch.dictionary[name] = reg
    else:
        raise TypeError(f'Expected type Registrar but got {reg.__class__.__name__}')