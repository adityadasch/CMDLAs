from cmdla import APP, Interface, Command, Parameter, dataclass

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
    if kwargs.get('msg') is None: kwargs['msg'] = 'No msg'
    if kwargs.get('priority') is None: kwargs['priority'] = 'low'
    if kwargs.get('due') is None: kwargs['due'] = 'today'

    tasks.append(Task(kwargs['msg'],kwargs['priority'],kwargs['due'],False))

def listtasks():
    for i, t in enumerate(tasks, 1):
            print(i, t, "Y" if t.done else "N")

def mark(**kwargs):
    if kwargs.get('index') is None: kwargs['index'] = 0
    try:
        tasks[int(kwargs.get('index'))-1].done = True
    except IndexError:
         print('Provide a valid index')

def unmark(**kwargs):
    if kwargs.get('index') is None: kwargs['index'] = 0
    try:
        tasks[int(kwargs.get('index'))-1].done = False
    except IndexError:
         print('Provide a valid index')

def printHelp():
     print('''
Help for CLI Todo:
todo add:
           Create new task
           Param: -m; -p; -d
           -m: Message
           -p: Priority
           -d: Due
           Alias: a
todo list:
           List all tasks
           Alias: l
todo done:
           Mark task at index as done
           Param: -i
           -i: Index
           Alias: d; m; mark
todo undone:
           Unmark task at index
           Param: -i
           -i: Index
           Alias: u; um; unmark
todo help:
           Bring up help
           Alias: h
todo quit:
           Quit CLI Todo
           Alias: q
''')

def main():
    APP.prompt = 'todo '
    add_param = [Parameter('msg', ['m']), 
                Parameter('priority', ['p']),
                Parameter('due',['d'])]
    add = Command('add', ['a'], 'msg', accepted_param=add_param)
    APP.AddToRegistrar(add)
    APP.BindFunction('add', addtask)

    list_ = Command('list',['l'],acceptsArgs=False)
    APP.AddToRegistrar(list_)
    APP.BindFunction('list', listtasks)

    done_param = [Parameter('index', ['i'])]
    done = Command('done',['d','m','mark'], 'index', accepted_param= done_param)
    APP.AddToRegistrar(done)
    APP.BindFunction('done', mark)

    undone = Command('undone',['u','um','unmark'], 'index', accepted_param= done_param)
    APP.AddToRegistrar(undone)
    APP.BindFunction('undone', unmark)

    help_ = Command('help', ['h'], acceptsArgs=False)
    APP.AddToRegistrar(help_)
    APP.BindFunction('help', printHelp)

    APP.SetQuitCmd(Command('quit',('q'), acceptsArgs=False))

if __name__ == '__main__':
    Interface.TakeListInput([
        "add Buy milk -p high -d tomorrow",
        "add Finish report -p medium",
        "list",
        "done -i 1",
        "list",
        "undone -i 1",
        "list",
        "help",
        "quit"])
    Interface.startLoop()