import datetime
import glob
import os
import shutil
import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk
from threading import Thread
from configparser import ConfigParser
import psutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import tkinter.font as tkFont

"""
Start global variables
"""
COUNT = 0
MOVE_COUNT = 0
"""
End global variables
"""

class config():
    """
    This class will check if there is a config file.
    If there is a configfile this will be loaded.
    If not a configfile will be created.
    """
    def __init__(self):
        self.config = ConfigParser()
        print('#####################')
        print('Config:')
        self.check_file('./config.ini')
        self.LOGOFF = False

    def check_file(self, file):
        if not os.path.isfile(file):
            print('No config found')
            self.config.add_section('debug')
            self.config.set('debug', 'DEBUG', 'True')
            self.config.add_section('main')
            self.config.set('main', 'FOLDER_WATCHDOG', 'True')
            self.config.set('main', 'DSP_SAVEGAME_FOLDER', rf'C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\Save')
            self.config.set('main', 'BACKUP_SAVE_PATH', rf'C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\save_backup' )
            self.config.set('main', 'COPY_FROM_SAVE_TO_ORIGINAL', 'True')
            self.config.add_section('game')
            self.config.set('game', 'DSPGAME_PROCESS',  'DSPGAME.exe')
            self.config.set('game', 'DSPGAME_START_GAME', 'True')
            self.config.set('game', 'STEAM_PATH', r'C:\Program Files (x86)\Steam\Steam.exe')
            self.config.add_section('logoff')
            self.config.set('logoff', 'COUNTER_TO_LOGOFF', '6')

            with open('config.ini', 'w') as f:
                self.config.write(f)
            print('Config: "config.ini" created')
        else:
            print('Config: "config.ini" found')
        try:
            self.config.read('config.ini')
        except:
            print('Config: cannot read "config.ini"')
        print('Config: set global varaibles')
        try:
            self.DEBUG = self.config.get('debug', 'DEBUG')
            self.FOLDER_WATCHDOG = self.config.get('main','FOLDER_WATCHDOG')
            self.DSP_SAVEGAME_FOLDER = self.config.get('main', 'DSP_SAVEGAME_FOLDER')
            self.BACKUP_SAVE_PATH = self.config.get('main', 'BACKUP_SAVE_PATH')
            self.COPY_FROM_SAVE_TO_ORIGINAL = self.config.get('main', 'COPY_FROM_SAVE_TO_ORIGINAL')
            self.DSPGAME_PROCESS = self.config.get('game', 'DSPGAME_PROCESS')
            self.DSPGAME_START_GAME = self.config.get('game', 'DSPGAME_START_GAME')
            self.STEAM_PATH = self.config.get('game', 'STEAM_PATH')
            self.COUNTER_TO_LOGOFF = self.config.get('logoff', 'COUNTER_TO_LOGOFF')
            if self.DEBUG:
                print(f'DEBUG = {self.DEBUG}\n'
                      f'FOLDER_WATCHDOG = {self.FOLDER_WATCHDOG}\n'
                      f'DSP_SAVEGAME_FOLDER = {self.DSP_SAVEGAME_FOLDER}\n'
                      f'BACKUP_SAVE_PATH= {self.BACKUP_SAVE_PATH}\n'
                      f'COPY_FROM_SAVE_TO_ORIGINAL = {self.COPY_FROM_SAVE_TO_ORIGINAL}\n'
                      f'DSPGAME_PROCESS = {self.DSPGAME_PROCESS}\n'
                      f'DSPGAME_START_GAME = {self.DSPGAME_START_GAME}\n'
                      f'STEAM_PATH = {self.STEAM_PATH}\n'
                      f'COUNTER_TO_LOGOFF = {self.COUNTER_TO_LOGOFF}\n')


            return print('Config: set global variables sucessfully')
        except KeyError as e:
            return print(f'Config: {e}, Error read the configfile')

class Handler(FileSystemEventHandler):
    MOVE_COUNT = 0
    def on_any_event(self, event):
        GAME_PROCESS = bool(checkIfProcessRunning(config.DSPGAME_PROCESS))
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            if GAME_PROCESS or config.DEBUG:
                # Take any action here when a file is first created.
                split_path = event.src_path.split('\\')
                if 'save' in str(split_path[-1]).lower():
                    time.sleep(3)
                    print(f'Datei: "{split_path[-1]}" wird nach "{config.BACKUP_SAVE_PATH}\\{split_path[-1]}" verschoben!')
                    shutil.move(f'{event.src_path}', f'{config.BACKUP_SAVE_PATH}\\{split_path[-1]}')
                    self.MOVE_COUNT += 1
                    if self.MOVE_COUNT == 3:
                        check_logoff(config.COUNTER_TO_LOGOFF)
                        self.MOVE_COUNT = 0
                else:
                    print("Speicherpunkt %s wurde erstellt, aber er wird Ignoriert" % event.src_path)

class threaded_observer(Thread):
    running = False
    def __init__(self):
        Thread.__init__(self)
        self.my_observer = None
        if config.FOLDER_WATCHDOG == True:
            self.running = True
            self.init_observer()

    def run(self):
        while self.running:
            self.startup_observer()
            time.sleep(1)

    def start(self):
        if not self.running and not self.my_observer:
            self.init_observer()
        self.running = True

    def stop(self):
        self.running = False

    def init_observer(self):
        global my_observer
        self.my_event_handler = Handler()
        self.my_observer = Observer()
        self.my_observer.schedule(self.my_event_handler, path=config.DSP_SAVEGAME_FOLDER, recursive=False)
        self.my_observer.start()

    def startup_observer(self):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            my_observer.stop()
            my_observer.join()

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def check_logoff(counter_to_logoff):
    global COUNT, LOGOFF
    if LOGOFF:
        if COUNT == counter_to_logoff:
            time.sleep(10)
            print('Spiel wird beendet')
            os.system(f"taskkill /im {config.DSPGAME_PROCESS}")
            while checkIfProcessRunning(config.DSPGAME_PROCESS):
                print('Spiel laeuft noch')
            print('Spiel wurde beendet\n Python wird beendet')
            os.system("shutdown /s /t 60")
            sys.exit()
        COUNT +=1
    print(f'Logoff = {config.LOGOFF}\nCounter_to_logoff =  {counter_to_logoff}\nActual Counter = {COUNT}\n')

def get_last_saves(folder):
    files = list(filter(os.path.isfile, glob.glob(folder + "\\*")))
    files.sort(key=lambda x: os.path.getmtime(x))
    return files[-3:]

def copy_to_ramdisk() -> None: #Kopiere Daten in die RAMDISK
    files = os.listdir(config.BACKUP_SAVE_PATH)
    if files == [] or files == "" or files is None:
        print('Keine Savegames gefunden')
    else:
        list_savegames = get_last_saves(config.BACKUP_SAVE_PATH)
        print(f'Last Savegames are: {list_savegames}')
        for savegame in list_savegames:
            savegame_filename_only = savegame.split('\\')[-1]
            print('Savegame wird in RAMDISK geladen')
            print(f'Datei: "{savegame}" wird nach "{config.DSP_SAVEGAME_FOLDER}\\{savegame_filename_only}" kopiert!')
            shutil.copy(f'{config.BACKUP_SAVE_PATH}\\{savegame_filename_only}', f'{config.DSP_SAVEGAME_FOLDER}\\{savegame_filename_only}')
            time.sleep(1)

class MainWindow(tk.Tk):
    def __init__(self, watchdog):
        super().__init__()
        self.watchdog = watchdog
        self.title("DSP_SaveGameManager")
        #setting window size
        width=600
        height=500
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(alignstr)
        self.resizable(width=False, height=False)
        self.labels()
        self.messagebox()
        self.checkboxes()
        self.buttons()

    def labels(self):
        LABEL_HEADER = tk.Label(self)
        ft = tkFont.Font(family='Times', size=14)
        LABEL_HEADER["cursor"] = "cross"
        LABEL_HEADER["font"] = ft
        LABEL_HEADER["fg"] = "#333333"
        LABEL_HEADER["justify"] = "center"
        LABEL_HEADER["text"] = "DSP SaveGameManager "
        LABEL_HEADER.place(x=160,y=10,width=246,height=30)

        LABEL_DEBUG=tk.Label(self)
        ft = tkFont.Font(family='Times',size=10)
        LABEL_DEBUG["font"] = ft
        LABEL_DEBUG["fg"] = "#333333"
        LABEL_DEBUG["justify"] = "right"
        LABEL_DEBUG["text"] = "DEBUG?"
        LABEL_DEBUG.place(x=120,y=40,width=257,height=30)

        LABEL_FOLDER_WATCHDOG=tk.Label(self)
        ft = tkFont.Font(family='Times',size=10)
        LABEL_FOLDER_WATCHDOG["font"] = ft
        LABEL_FOLDER_WATCHDOG["fg"] = "#333333"
        LABEL_FOLDER_WATCHDOG["justify"] = "right"
        LABEL_FOLDER_WATCHDOG["text"] = "Save Data into Backup folder?"
        LABEL_FOLDER_WATCHDOG.place(x=120,y=70,width=255,height=30)

        LABEL_COPY_FROM_SAVE_TO_ORIGIAL=tk.Label(self)
        ft = tkFont.Font(family='Times',size=10)
        LABEL_COPY_FROM_SAVE_TO_ORIGIAL["font"] = ft
        LABEL_COPY_FROM_SAVE_TO_ORIGIAL["fg"] = "#333333"
        LABEL_COPY_FROM_SAVE_TO_ORIGIAL["justify"] = "right"
        LABEL_COPY_FROM_SAVE_TO_ORIGIAL["text"] = "Restore last Save?"
        LABEL_COPY_FROM_SAVE_TO_ORIGIAL.place(x=120,y=100,width=255,height=30)

        LABEL_DSP_START_GAME=tk.Label(self)
        ft = tkFont.Font(family='Times',size=10)
        LABEL_DSP_START_GAME["font"] = ft
        LABEL_DSP_START_GAME["fg"] = "#333333"
        LABEL_DSP_START_GAME["justify"] = "right"
        LABEL_DSP_START_GAME["text"] = "Autostart DSP?"
        LABEL_DSP_START_GAME.place(x=120,y=130,width=255,height=30)

    def checkboxes(self):
        CHECKBOX_DEBUG=tk.Checkbutton(self)
        ft = tkFont.Font(family='Times',size=10)
        CHECKBOX_DEBUG["font"] = ft
        CHECKBOX_DEBUG["fg"] = "#333333"
        CHECKBOX_DEBUG["justify"] = "center"
        CHECKBOX_DEBUG["text"] = ""
        CHECKBOX_DEBUG.place(x=390,y=40,width=70,height=25)
        CHECKBOX_DEBUG["offvalue"] = False
        CHECKBOX_DEBUG["onvalue"] = True
        CHECKBOX_DEBUG["command"] = self.CHECKBOX_DEBUG

        CHECKBOX_FOLDER_WATCHDOG=tk.Checkbutton(self)
        ft = tkFont.Font(family='Times',size=10)
        CHECKBOX_FOLDER_WATCHDOG["font"] = ft
        CHECKBOX_FOLDER_WATCHDOG["fg"] = "#333333"
        CHECKBOX_FOLDER_WATCHDOG["justify"] = "center"
        CHECKBOX_FOLDER_WATCHDOG["text"] = ""
        CHECKBOX_FOLDER_WATCHDOG.place(x=390,y=70,width=70,height=25)
        CHECKBOX_FOLDER_WATCHDOG["offvalue"] = False
        CHECKBOX_FOLDER_WATCHDOG["onvalue"] = True
        CHECKBOX_FOLDER_WATCHDOG["command"] = self.CHECKBOX_FOLDER_WATCHDOG

        CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL=tk.Checkbutton(self)
        ft = tkFont.Font(family='Times',size=10)
        CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["font"] = ft
        CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["fg"] = "#333333"
        CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["justify"] = "center"
        CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["text"] = ""
        CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL.place(x=390,y=100,width=70,height=25)
        CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["offvalue"] = False
        CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["onvalue"] = True
        CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["command"] = self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL

        CHECKBOX_DSP_START_GAME=tk.Checkbutton(self)
        ft = tkFont.Font(family='Times',size=10)
        CHECKBOX_DSP_START_GAME["font"] = ft
        CHECKBOX_DSP_START_GAME["fg"] = "#333333"
        CHECKBOX_DSP_START_GAME["justify"] = "center"
        CHECKBOX_DSP_START_GAME["text"] = ""
        CHECKBOX_DSP_START_GAME.place(x=390,y=130,width=70,height=25)
        CHECKBOX_DSP_START_GAME["offvalue"] = False
        CHECKBOX_DSP_START_GAME["onvalue"] = True
        CHECKBOX_DSP_START_GAME["command"] = self.CHECKBOX_DSP_START_GAME

    def messagebox(self):
        MESSAGE_BOX=tk.Message(self)
        ft = tkFont.Font(family='Times',size=10)
        MESSAGE_BOX["font"] = ft
        MESSAGE_BOX["fg"] = "#333333"
        MESSAGE_BOX["justify"] = "center"
        MESSAGE_BOX["text"] = "Dies ist ein langer text"
        MESSAGE_BOX.place(x=40,y=340,width=497,height=127)

    def buttons(self):
        BUTTON_SAVE=tk.Button(self)
        BUTTON_SAVE["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        BUTTON_SAVE["font"] = ft
        BUTTON_SAVE["fg"] = "#000000"
        BUTTON_SAVE["justify"] = "center"
        BUTTON_SAVE["text"] = "Save"
        BUTTON_SAVE.place(x=420,y=450,width=70,height=25)
        BUTTON_SAVE["command"] = lambda: self.save()

        BUTTON_BEENDEN=tk.Button(self)
        BUTTON_BEENDEN["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        BUTTON_BEENDEN["font"] = ft
        BUTTON_BEENDEN["fg"] = "#000000"
        BUTTON_BEENDEN["justify"] = "center"
        BUTTON_BEENDEN["text"] = "Beenden"
        BUTTON_BEENDEN.place(x=500,y=450,width=70,height=25)
        BUTTON_BEENDEN["command"] = lambda: self.stop()

    def CHECKBOX_DEBUG(self):
        print("command")


    def CHECKBOX_FOLDER_WATCHDOG(self):
        print("command")


    def CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL(self):
        print("command")


    def CHECKBOX_DSP_START_GAME(self):
        print("command")


    def watchdog_change(self):
        if self.watchdog.running:
            self.watchdog.stop()
            self.watchdog_var.set('Watchdog beendet')
        else:
            self.watchdog.start()
            self.watchdog_var.set('Watchdog gestartet')


    def stop(self):
        self.destroy()

def main():
    print('Window wird erstellt')
    print('Ueberprufe Game Prozess')
    if config.COPY_FROM_SAVE_TO_ORIGINAL in [True, "True"]:
        print('COPY_FROM_SAVE_TO_ORIGINAL: Kopiere Savegames')
        copy_to_ramdisk()
    if not checkIfProcessRunning(config.DSPGAME_PROCESS) and config.DSPGAME_START_GAME in [True, "True"]:
        print('Spiel wird gestartet')
        subprocess.Popen(rf"{config.STEAM_PATH} -applaunch 1366540")
        while not checkIfProcessRunning(config.DSPGAME_PROCESS):
            print('Warte auf Spielstart')
            time.sleep(3)
        print('DSP erfolgreich gestartet')
    else:
        print('DSP bereits gestartet')

    if config.LOGOFF in [True, "True"]:
        shutdowntime = datetime.datetime.now() + datetime.timedelta(minutes=int(config.COUNTER_TO_LOGOFF*10))
        final_time_str = shutdowntime.strftime('%d/%m/%Y %H:%M:%S')
        print(f'ACHTUNG: Logofftimer aktiviert, herunterfahren in {int(config.COUNTER_TO_LOGOFF*10)} Minuten! ({final_time_str})')
    print('Watchdog wird gestartet')
    watchdog = threaded_observer()
    print('Watchdog wurde gestartet')
    app = MainWindow(watchdog)
    app.mainloop()


if __name__ == '__main__':
    """
    read and set the globals first
    """
    config = config()
    """
    start the main function
    """
    main()
