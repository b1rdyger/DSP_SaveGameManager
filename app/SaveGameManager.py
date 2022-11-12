import json
import os
import threading
import tkinter as tk
from tkinter import Menu, ttk, LEFT, RIGHT
from tkinter import N, S, W, E
from tkinter.ttk import Scrollbar

from PIL import ImageTk, Image

from app import Engine
from app.widgets.ConsoleOutput import ConsoleOutput


class SaveGameWindow:
    frame_bg = '#ddd'

    def ram_drive_mounted(self):
        self._memory_save_game.configure(bg='lime')

    def ram_drive_unmounted(self):
        self._memory_save_game.configure(bg='#c2d5e6')

    def __init__(self, engine: Engine):
        # setup vars
        self.engine = engine
        self.config = self.engine.config
        self.event_bus = self.engine.event_bus
        self.root_dir = self.engine.root_dir
        self.asset_dir = self.root_dir + 'assets' + os.sep

        # start
        self.root = tk.Tk()
        self.root.geometry('732x382')
        self.root.title('Savegame Manager')
        self.root.iconphoto(False, tk.PhotoImage(file=self.asset_dir + 'logo' + os.sep + 'disk1-256.png'))

        # setup layout
        self.generate_menu()
        self.configure_grid_weights()

        # events
        self.event_bus.add_listener('mfs.symlink.created', self.ram_drive_mounted)
        self.event_bus.add_listener('mfs.symlink.removed', self.ram_drive_unmounted)

        # self.root.resizable(False, False)
        # self.root.protocol("WM_DELETE_WINDOW", self.root.iconify)
        # logo = ImageTk.PhotoImage(file=self.asset_dir + 'dsp_logo_rel32.png')
        self._generate_frame_game(None)

        _frame_disks_game = tk.Frame(self.root, bg=self.frame_bg, height=100, padx=3, pady=2)
        _frame_disks_game.grid(row=1, column=0, sticky=N+S+E+W, padx=2, pady=2)
        _frame_disks_game.columnconfigure(0, weight=0)
        _frame_disks_game.columnconfigure(1, weight=1)

        label_arrow = tk.Canvas(_frame_disks_game, bg=self.frame_bg, bd=0, highlightthickness=0, width=32, height=32)
        icon_game = ImageTk.PhotoImage(Image.open(self.asset_dir + 'arrow_right.png'))
        label_arrow.create_image(0, 0, image=icon_game, anchor=N+W)
        label_arrow.grid(row=0, column=0, padx=0, pady=0, ipadx=0, ipady=0)

        default_save_game = tk.Label(_frame_disks_game, text='default save-path', bg='#c2d5e6', borderwidth=2,
                                     relief='solid', padx=6, pady=4, anchor=W)
        default_save_game.grid(row=0, column=1, sticky=N+E+W, padx=4, pady=4)
        self._memory_save_game = tk.Label(_frame_disks_game, text='RAM-disk', bg='#c2d5e6', borderwidth=2,
                                          relief='solid', padx=6, pady=4, anchor=W)
        self._memory_save_game.grid(row=1, column=1, sticky=N+E+W, padx=4, pady=4)

        frame_disks_others = tk.Frame(self.root, bg='lime', padx=3, pady=2)
        frame_disks_others.grid(row=1, column=1, sticky=N+S+E+W, ipadx=2, ipady=1, padx=2, pady=2)

        _frame_log = tk.Frame(self.root, bg='yellow', padx=3, pady=2)
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

    def _generate_frame_game(self, logo):
        frame_game = tk.Frame(self.root, bg='red', height=80, padx=3, pady=2)
        frame_game.grid(row=0, column=0, columnspan=2, sticky=N + S + E + W, padx=2, pady=2)
        frame_game.rowconfigure(0, weight=0, minsize=40)
        frame_game.rowconfigure(1, weight=0, minsize=40)
        frame_game.columnconfigure(0, weight=1)
        frame_game.columnconfigure(1, weight=0)
        btn_change_game = ttk.Button(frame_game, text='Start Game', command=self.root.destroy)
        btn_change_game.grid(row=0, column=1, sticky=N + S + E + W, ipadx=3, ipady=3)
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
