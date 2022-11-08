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

#Globals
"""
Debug
"""
DEBUG = False
"""
MAIN
"""
DSPGAME_PROCESS = ""
DSP_SAVEGAME_FOLDER = ""
BACKUP_SAVE_PATH = ""
COPY_FROM_SAVE_TO_ORIGINAL = ""
"""
Logoff
"""
LOGOFF = False
COUNTER_TO_LOGOFF = 0

"""
etc.
"""
COUNT = 0
MOVE_COUNT = 0

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
            self.config.set('main', 'DSPGAME_PROCESS',  'DSPGAME.exe')
            self.config.set('main', 'FOLDER_WATCHDOG', 'True')
            self.config.set('main', 'DSP_SAVEGAME_FOLDER', rf'"C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\Save"')
            self.config.set('main', 'BACKUP_SAVE_PATH', rf'"C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\save_backup"' )
            self.config.set('main', 'COPY_FROM_SAVE_TO_ORIGINAL', 'True')
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
            self.DSPGAME_PROCESS = self.config.get('main', 'DSPGAME_PROCESS')
            self.DSP_SAVEGAME_FOLDER = self.config.get('main', 'DSP_SAVEGAME_FOLDER')
            self.BACKUP_SAVE_PATH = self.config.get('main', 'BACKUP_SAVE_PATH')
            self.COPY_FROM_SAVE_TO_ORIGINAL = self.config.get('main', 'COPY_FROM_SAVE_TO_ORIGINAL')
            self.COUNTER_TO_LOGOFF = self.config.get('logoff', 'COUNTER_TO_LOGOFF')
            if self.DEBUG:
                print(f'DEBUG = {self.DEBUG}\n'
                      f'FOLDER_WATCHDOG = {self.FOLDER_WATCHDOG}\n'
                      f'DSPGAME_PROCESS = {self.DSPGAME_PROCESS}\n'
                      f'DSP_SAVEGAME_FOLDER = {self.DSP_SAVEGAME_FOLDER}\n'
                      f'BACKUP_SAVE_PATH= {self.BACKUP_SAVE_PATH}\n'
                      f'COPY_FROM_SAVE_TO_ORIGINAL = {self.COPY_FROM_SAVE_TO_ORIGINAL}\n'
                      f'COUNTER_TO_LOGOFF = {self.COUNTER_TO_LOGOFF}\n')


            return print('Config: set global variables sucessfully')
        except KeyError as e:
            return print(f'Config: {e}, Error read the configfile')

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

class Handler(FileSystemEventHandler):
    MOVE_COUNT = 0
    def on_any_event(self, event):
        GAME_PROCESS = bool(checkIfProcessRunning(config.DSPGAME_PROCESS))
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            if GAME_PROCESS or DEBUG:
                # Take any action here when a file is first created.
                split_path = event.src_path.split('\\')
                if 'save' in str(split_path[-1]).lower():
                    time.sleep(3)
                    print(f'Datei: "{split_path[-1]}" wird nach "{config.BACKUP_SAVE_PATH}\\{split_path[-1]}" verschoben!')
                    shutil.move(f'{event.src_path}', f'{config.BACKUP_SAVE_PATH}\\{split_path[-1]}')
                    self.MOVE_COUNT += 1
                    if self.MOVE_COUNT == 3:
                        check_logoff(COUNTER_TO_LOGOFF)
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
        self.my_observer.schedule(self.my_event_handler, path=DSP_SAVEGAME_FOLDER, recursive=False)
        self.my_observer.start()

    def startup_observer(self):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            my_observer.stop()
            my_observer.join()

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
    files = os.listdir(BACKUP_SAVE_PATH)
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

class CheckStates(Thread):
    def __init__(self, state):
        super().__init__()
        self.state = state

    def check(self):
        return self.state

class MainWindow(tk.Tk):
    def __init__(self, watchdog):
        super().__init__()
        self.watchdog = watchdog
        self.title("SavegameManager")  # give title to the window
        self.rootWidth = 500
        self.rootHeight = 500
        # self.geometry('800x600')
        self.minsize(self.rootWidth, self.rootHeight)
        self.maxsize(self.rootWidth, self.rootHeight)
        self.create_body_frame()
        self.create_footer_frame()

    def create_body_frame(self):
        #create Frame and set Column and row configures
        self.header = ttk.Frame(self)
        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=10)
        self.header.columnconfigure(2, weight=1)

        #creating variables and set them
        self.watchdog_var = tk.StringVar()
        self.watchdog_var.set(config.FOLDER_WATCHDOG)

        #creating Labels
        self.headlabel = ttk.Label(self.header, text="Shutdown, Restart and Logout Using Pc").grid(column=0,row=0,sticky=tk.W)
        self.statusLabel = ttk.Label(self.header, text='Watchdog Status:').grid(column=0,row=1,sticky=tk.W)
        self.watchdog_label = ttk.Label(self.header, textvariable=self.watchdog_var).grid(column=1,row=1,sticky=tk.W)

        # creating buttons
        ttk.Button(self.header, text='Change Watchdog', command=lambda: self.watchdog_change()).grid(column=3, row=1,  sticky=tk.W)

        #pack everything
        self.header.pack()

    def create_footer_frame(self):
        self.footer = ttk.Frame(self)
        self.footer.columnconfigure(0, weight=1)
        self.footer.columnconfigure(1, weight=10)
        self.footer.columnconfigure(2, weight=1)
        ttk.Button(self.header, text='Beenden', command=lambda: self.stop()).grid(pady=self.rootHeight/100*80, column=3, row=3, sticky=tk.S)
        self.footer.pack(anchor='center')

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
    if not checkIfProcessRunning(config.DSPGAME_PROCESS) and not config.DEBUG:
        print('Spiel wird gestartet')
        subprocess.Popen(r"C:\Program Files (x86)\Steam\Steam.exe -applaunch 1366540")
        while not checkIfProcessRunning(config.DSPGAME_PROCESS):
            print('Warte auf Spielstart')
            time.sleep(3)
        print('DSP erfolgreich gestartet')
    else:
        print('DSP bereits gestartet')
    if config.COPY_FROM_SAVE_TO_ORIGINAL and not config.DEBUG:
        copy_to_ramdisk()
    if config.LOGOFF and not config.DEBUG:
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
