from cmdla import APP, Interface, Command, Parameter, dataclass, Switch, Add, Registrar

@dataclass
class Task:
    msg: str
    priority: str
    due: str
    done: bool

    def __repr__(self):
        return f'{self.msg}'

tasks: list[Task] = []

def addtask(**kwargs):
    print(kwargs)
    if kwargs.get('task') is None: kwargs['task'] = 'No msg'
    if kwargs.get('priority') is None: kwargs['priority'] = 'low'
    if kwargs.get('due') is None: kwargs['due'] = 'today'

    tasks.append(Task(kwargs['task'],kwargs['priority'],kwargs['due'],False))

def listtasks():
    for i, t in enumerate(tasks, 1):
            print(i, t, "Y" if t.done else "N")

def mark_(**kwargs):
    if kwargs.get('index') is None: kwargs['index'] = 0
    try:
        tasks[int(kwargs.get('index'))-1].done = True
    except IndexError:
         print('Provide a valid index')

def unmark_(**kwargs):
    if kwargs.get('index') is None: kwargs['index'] = 0
    try:
        tasks[int(kwargs.get('index'))-1].done = False
    except IndexError:
         print('Provide a valid index')

def removetask(**kwargs):
    if kwargs.get('index') is None: kwargs['index'] = 0
    try:
        tasks.pop(int(kwargs.get('index'))-1)
    except IndexError:
         print('Provide a valid index')

def main():
    APP.prompt= 'todo '
    add = Command(
            'add',
            ('a',),
            'task',
            accepted_param=(
                Parameter('task', ('t',)),
                Parameter('priority', ('p',))
            ),function=addtask
        )
    
    rem = Command(
            'rem',
            ('r',),
            'i',
            accepted_param=(
                Parameter('index', ('i',)),
            ),function=removetask
        )
    
    mark = Command(
            'mark',
            ('m',),
            'i',
            accepted_param=(
                Parameter('index', ('i',)),
            ),function=mark_
        )
    
    unmark = Command(
            'unmark',
            ('um',),
            'i',
            accepted_param=(
                Parameter('index', ('i',)),
            ),function=unmark_
        )
    
    list_ = Command(
            'list',
            ('ls',),
            acceptsArgs=False,
            accepted_param=(),function=listtasks
        )
    
    switch = Command('group', default_param='name', accepted_param=('name',), function=Switch)
    
    APP.AddToRegistrar((add,rem,mark,unmark,list_,))

    APP.SetQuitCmd(Command('quit',('q'), acceptsArgs=False))

    foo = Registrar()

    foo.prompt= 'foo '

    Add('foo', foo)

    Interface.exitsSwitch = True
    Interface.switchCommand = switch

if __name__ == '__main__':
    main()
    
    Interface.doHelp=True
    Interface.StartLoop()