import os
import re
from datetime import datetime
from tkinter import Text, END

from app import EventBus
from app.widgets.MessageByEvent import MessageByEvent


class ConsoleOutput(Text):
    lines = []
    event_bus: EventBus = None

    def __init__(self, script_dir: str, event_bus: EventBus, master=None, cnf=None, **kw):
        if cnf is None:
            cnf = {}
        super().__init__(master, cnf, fg='#ddd', bg='black', font=('Lucida Console', 11), padx=1, pady=3, **kw)
        self.script_dir = script_dir

        self.set_colors()
        self.event_bus = event_bus

        MessageByEvent(self.event_bus, self.write)

    def write(self, msg: str):
        now = datetime.now()
        self.insert(END, '[' + now.strftime("%H:%M:%S") + '] ', 'timestamp')
        while len(msg) > 0:
            matched = re.search('\\[([a-zA-Z0-9]{1,5}):(.*?)]', msg)
            if matched:
                all_start, _ = matched.span(0)
                sub_msg_start, sub_msg_end = matched.span(2)
                tag = matched.group(1)
                if all_start > 0:
                    self.insert(END, msg[:all_start])
                    msg = msg[all_start:]
                    sub_msg_start = sub_msg_start - all_start
                    sub_msg_end = sub_msg_end - all_start
                msg = msg[sub_msg_start:]
                sub_msg_end -= sub_msg_start
                self.insert(END, msg[:sub_msg_end], tag)
                msg = msg[sub_msg_end + 1:]
            else:
                self.insert(END, msg)
                break
        self.insert(END, "\n")

    def set_colors(self):
        file = open(self.script_dir + 'app' + os.sep + 'widgets' + os.sep + 'tag_colors.css', mode='r')
        tag_colors_css = file.read()
        file.close()

        all_tags = {}
        while True:
            found = re.search('--([a-zA-Z0-9_-]+)\\s*:\\s*(#[a-zA-Z0-9]{3,6});', tag_colors_css)
            if found:
                tag_name = found.group(1)
                tag_color = found.group(2)
                all_tags[tag_name] = tag_color
                tag_colors_css = tag_colors_css[found.span(0)[1]:]
            else:
                break
        for tag, color in all_tags.items():
            self.tag_configure(tag, foreground=color)

# if __name__ == '__main__':
#     root = tkinter.Tk()
#     root.geometry('732x382')
#     eb = EventBus.EventBus()
#     script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep + os.pardir + os.sep + os.pardir + os.sep
#     co = ConsoleOutput(script_dir, eb, root, height=20, width=40)
#     co.pack(fill='both', expand=True)
#     co.write("hello world!")
#     co.write("bla[info:high light]foo bar")
#     co.write("[info:start] something")
#     co.write("something [info:end]")
#     co.write("bla[info: this ]foo bar")
#     co.write("cry [info:this] baz bar")
#     co.write("cry [info:this] baz [info:here] bar")
#     co.write("cry [info:this] baz [info:here] [X] bar")
#     co.write("cry [info:this loot] bar")
#     co.write("cry [info: wrong 1 bar")
#     co.write("cry [wrong] 2 bar")
#     root.mainloop()
