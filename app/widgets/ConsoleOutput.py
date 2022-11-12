import os
import re
import tkinter
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
        while msg != "":
            if matched := re.search('\\[([a-zA-Z0-9]+):(.*?)]', msg):
                all_start, _ = matched.span(0)
                sub_msg_start, sub_msg_end = matched.span(2)
                tag = matched[1]
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
        with open(f'{self.script_dir}app{os.sep}widgets{os.sep}tag_colors.css', mode='r') as file:
            tag_colors_css = file.read()
        all_tags = {}
        while found := re.search('--([a-zA-Z0-9_-]+)\\s*:\\s*(#[a-zA-Z0-9]{3,6});', tag_colors_css):
            tag_name = found[1]
            tag_color = found[2]
            all_tags[tag_name] = tag_color
            tag_colors_css = tag_colors_css[found.span(0)[1]:]
        for tag, color in all_tags.items():
            self.tag_configure(tag, foreground=color)
