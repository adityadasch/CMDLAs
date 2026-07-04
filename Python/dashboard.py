from cmdla.interface import Interface, Command
from cmdla.switcher import Switch, Add
from cmdla.utils import requires,validate
from cmdla.registrar import Registrar
from cmdla.dataclasses import dataclass, Parameter

@dataclass
class Note:
    message: str = None
    priority: str = None

class NotesDB:
    tasks: list[Note] = []

    @classmethod
    @requires('task')
    def add_task(cls,task,priority=None, **kwargs):
        cls.tasks.append(Note(task, priority))

    @classmethod
    @validate(index=lambda x: x.isdigit())
    def remove_task(cls,index: str, **kwargs):
        cls.tasks.pop(int(index)-1)

    @classmethod
    def list_task(cls):
        for i, t in enumerate(cls.tasks, 1):
            print(i, t)

@dataclass
class Event:
    event: str = None
    date: str = None

class EventsDB:
    events: list[Event] = []

    @classmethod
    def add_event(cls, **kwargs):
        if kwargs.get('event') is None: print('Please provide event message'); return

        event, d = kwargs.get('event'), kwargs.get('date') if kwargs.get('date') else 'today'
        cls.events.append(Event(event, d))

    @classmethod
    def remove_event(cls, **kwargs):
        if kwargs.get('id') is None or str(kwargs.get('id')).isdigit(): print('Please provide valid task id'); return

        cls.events.pop(int(kwargs.get('id')))

    @classmethod
    def list_event(cls):
        for i, t in enumerate(cls.events, 1):
            print(i, t)


def init_note():
    note_reg = Registrar()
    note_reg.prompt = "note> "
    note_reg.help_docs_path = './help_doc/note.json'

    # Commands
    note_reg.AddToRegistrar((
        Command("add", ("a",), "task",
                accepted_param=(Parameter("task", ("t",)), Parameter("priority", ("p",))),
                function=NotesDB.add_task),
        Command("list", ("ls",), acceptsArgs=False, function=NotesDB.list_task),
        Command("remove", ("rm",), "index",
                accepted_param=(Parameter("index", ("i",)),),
                function=NotesDB.remove_task),
    ))

    return note_reg

def init_calendar():
    cal_reg = Registrar()
    cal_reg.prompt = "calendar> "
    cal_reg.help_docs_path = './help_doc/cal.json'

    # Commands
    cal_reg.AddToRegistrar((
        Command("add", ("a",), "event",
                accepted_param=(Parameter("event", ("e",)), Parameter("date", ("d",))),
                function=EventsDB.add_event),
        Command("list", ("ls",), acceptsArgs=False, function=EventsDB.list_event),
        Command("remove", ("rm",), "id",
                accepted_param=(Parameter("id", ("i",)),),
                function=EventsDB.remove_event),
    ))

    return cal_reg

def main():
    note = init_note()
    cal = init_calendar()

    Interface.switchCommand= None

    Add(name='note', reg= note); Add(name='cal', reg=cal)

    Switch(name='note')

    Interface.doHelp = True

    Interface.SetQuitCmd()

    Interface.StartLoop()

if __name__ == '__main__':
    main()