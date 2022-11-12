import json
import os
import subprocess
import threading
import tkinter as tk
from tkinter import Menu, ttk, LEFT, RIGHT, DISABLED, NORMAL
from tkinter import N, S, W, E
from tkinter.ttk import Scrollbar

from PIL import ImageTk, Image

from app import Engine
from app.SGMEvents.GuiEvents import SGMStop
from app.SGMEvents.MFSEvents import *
from app.SGMEvents.PCEvents import PCRunning
from app.widgets.ConsoleOutput import ConsoleOutput


class SaveGameWindow:
    frame_bg = '#ddd'
    game_running = False
    last_state = None

    def ram_drive_mounted(self):
        self._memory_save_game.configure(bg='lime')

    def ram_drive_unmounted(self):
        self._memory_save_game.configure(bg='#c2d5e6')

    def process_checker(self, *state):
        self.game_running = state
        if self.last_state == state:
            return
        if state:
            self.frame_game.configure(background='lime')
            self.btn_start_game.configure(state=DISABLED)
        else:
            self.frame_game.configure(background='red')
            self.btn_start_game.configure(state=NORMAL)
        self.last_state = state

    def __init__(self, engine: Engine):
        # setup vars
        self.engine = engine
        self.config = self.engine.config
        self.event_bus = self.engine.event_bus
        self.root_dir = self.engine.root_dir
        self.asset_dir = f'{self.root_dir}assets{os.sep}'

        # start
        self.root = tk.Tk()
        self.root.geometry('732x382')
        self.root.title('Savegame Manager')
        self.root.iconphoto(False, tk.PhotoImage(file=f'{self.asset_dir}logo{os.sep}disk1-256.png'))

        # setup layout
        self.generate_menu()
        self.configure_grid_weights()

        # events
        self.event_bus.add_listener(MFSSymlinkCreated, self.ram_drive_mounted)
        self.event_bus.add_listener(MFSSymlinkRemoved, self.ram_drive_unmounted)
        self.event_bus.add_listener(PCRunning, self.process_checker)
        self.root.protocol("WM_DELETE_WINDOW", lambda: threading.Thread(target=self.on_closing, daemon=True).start())

        # self.root.resizable(False, False)
        # self.root.protocol("WM_DELETE_WINDOW", self.root.iconify)
        # logo = ImageTk.PhotoImage(file=self.asset_dir + 'dsp_logo_rel32.png')
        self._generate_frame_game(None)

        frame_disks_game = tk.Frame(self.root, bg=self.frame_bg, height=100, padx=3, pady=2)
        frame_disks_game.grid(row=1, column=0, sticky=N+S+E+W, padx=2, pady=2)
        frame_disks_game.columnconfigure(0, weight=0)
        frame_disks_game.columnconfigure(1, weight=1)

        label_arrow = tk.Canvas(frame_disks_game, bg=self.frame_bg, bd=0, highlightthickness=0, width=32, height=32)
        icon_game = ImageTk.PhotoImage(Image.open(f'{self.asset_dir}arrow_right.png'))
        label_arrow.create_image(0, 0, image=icon_game, anchor=N+W)
        label_arrow.grid(row=0, column=0, padx=0, pady=0, ipadx=0, ipady=0)

        default_save_game = tk.Label(frame_disks_game, text='default save-path', bg='#c2d5e6', borderwidth=2,
                                     relief='solid', padx=6, pady=4, anchor=W)
        default_save_game.grid(row=0, column=1, sticky=N+E+W, padx=4, pady=4)
        self._memory_save_game = tk.Label(frame_disks_game, text='RAM-disk', bg='#c2d5e6', borderwidth=2,
                                          relief='solid', padx=6, pady=4, anchor=W)
        self._memory_save_game.grid(row=1, column=1, sticky=N+E+W, padx=4, pady=4)

        frame_disks_others = tk.Frame(self.root, bg=self.frame_bg, padx=3, pady=2)
        frame_disks_others.grid(row=1, column=1, sticky=N+S+E+W, ipadx=2, ipady=1, padx=2, pady=2)

        _frame_log = tk.Frame(self.root, bg=self.frame_bg, padx=3, pady=2)
        _frame_log.grid(row=2, column=0, columnspan=2, sticky=N+S+E+W, ipadx=2, ipady=1, padx=2, pady=2)

        text_log = ConsoleOutput(self.root_dir, self.event_bus, _frame_log)
        text_log.pack(expand=True, fill='both')
        scroll = Scrollbar(_frame_log, command=text_log.yview)
        text_log.configure(yscrollcommand=scroll.set)

        # btn_start = tk.Button(self.root, text='Start Game', bd=2, command=self.root.destroy, bg='red')

        # running
        self.engine.set_write_callback(text_log)
        cu1 = threading.Thread(target=self.engine.main_runner, daemon=True)
        cu1.start()

        self.root.mainloop()
        self.event_bus.remove_all_listener()
        cu1.join()

    def on_closing(self):
        self.engine.stop()
        self.root.destroy()

    def start_dsp(self):
        subprocess.Popen(rf"{self.config.get('steam_path')} -applaunch 1366540")

    def _generate_frame_game(self, logo):
        self.frame_game = tk.Frame(self.root, bg=self.frame_bg, height=80, padx=3, pady=2)
        self.frame_game.grid(row=0, column=0, columnspan=2, sticky=N + S + E + W, padx=2, pady=2)
        self.frame_game.rowconfigure(0, weight=0, minsize=40)
        self.frame_game.rowconfigure(1, weight=0, minsize=40)
        self.frame_game.columnconfigure(0, weight=1)
        self.frame_game.columnconfigure(1, weight=0)
        self.btn_start_game = ttk.Button(self.frame_game, text='Start Game!', command=lambda: self.start_dsp)
        self.btn_start_game.grid(row=0, column=1, sticky=N + S + E + W, ipadx=3, ipady=3)
        btn_change_game = ttk.Button(self.frame_game, text='Exit!',
                                     command=lambda: threading.Thread(target=self.on_closing, daemon=True).start())
        btn_change_game.grid(row=0, column=2, sticky=N + S + E + W, ipadx=3, ipady=3)
        # label_profile = tk.Label(frame_game, text='Dyson Sphere Program', compound='left', image=logo,
        #                          anchor=W, justify=LEFT)
        # label_profile.grid(row=0, column=0, sticky=W)

    def configure_grid_weights(self):
        self.root.columnconfigure(0, weight=1, uniform='fifthly')
        self.root.columnconfigure(1, weight=1, uniform='fifthly')
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)

    def generate_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = Menu(
            menubar,
            tearoff=0
        )
        file_menu.add_command(label='New')
        file_menu.add_command(label='Open...')
        file_menu.add_command(label='Close')
        file_menu.add_separator()
        file_menu.add_command(
            label='Exit',
            command=self.root.destroy
        )
        menubar.add_cascade(
            label="File",
            menu=file_menu
        )
        help_menu = Menu(
            menubar,
            tearoff=0
        )
        help_menu.add_command(label='Welcome')
        help_menu.add_command(label='About...')
        menubar.add_cascade(
            label="Help",
            menu=help_menu
        )
