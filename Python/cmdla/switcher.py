from .interface import Interface, Registrar, GLOBAL, Command
from .utils import requires_typed

class AllSwitch:
    dictionary: dict = {'global': GLOBAL}

def Switch(**kwarg):
    '''name: Name of the registrar'''
    name = kwarg.get('name')
    if name == '.':
        Interface.currentReg = AllSwitch.dictionary['global']
    elif name:
        if AllSwitch.dictionary.get(name):
            Interface.currentReg = AllSwitch.dictionary[name]
        else:
            print(f'Can\'t find registrar {name}')
    else:
        print('Available namespaces:')
        for k in AllSwitch.dictionary.keys(): print(f'{k}', end='  ')
        print()

    Interface.createHelpFunc()

@requires_typed(name=str, reg=Registrar)
def Add(name:str, reg: Registrar):
    if isinstance(reg, Registrar):
        AllSwitch.dictionary[name] = reg
    else:
        raise TypeError(f'Expected type Registrar but got {reg.__class__.__name__}')
    if len(AllSwitch.dictionary.keys()) > 1 and not Interface.existSwitch:
        Interface.existSwitch = True
        Interface.switchCommand = Command('switch', default_param='name', accepted_param=('name',), function=Switch)