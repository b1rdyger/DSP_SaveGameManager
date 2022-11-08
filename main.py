import datetime
import glob
import os
import shutil
import subprocess
import time
import tkinter as tk
from tkinter import ttk
from threading import Thread

import psutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

#Globals
DSPGAME_PROCESS = 'DSPGAME.exe'
RAW_DISK_SAVE_PATH=rf'C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\Save'
SSD_SAVE_PATH=rf'C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\save_backup'
GAME_PROCESS = False
COUNT = 0
MOVE_COUNT = 0

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
        GAME_PROCESS = bool(checkIfProcessRunning(DSPGAME_PROCESS))
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            if GAME_PROCESS or DEBUG:
                # Take any action here when a file is first created.
                split_path = event.src_path.split('\\')
                if 'save' in str(split_path[-1]).lower():
                    time.sleep(3)
                    print(f'Datei: "{split_path[-1]}" wird nach "{SSD_SAVE_PATH}\\{split_path[-1]}" verschoben!')
                    shutil.move(f'{event.src_path}', f'{SSD_SAVE_PATH}\\{split_path[-1]}')
                    self.MOVE_COUNT += 1
                    if self.MOVE_COUNT == 3:
                        check_logoff(COUNTER_TO_LOGOFF)
                        self.MOVE_COUNT = 0
                else:
                    print("Speicherpunkt %s wurde erstellt, aber er wird Ignoriert" % event.src_path)

class threaded_observer(Thread):
    running = False
    DIRECTORY_TO_WATCH = RAW_DISK_SAVE_PATH
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.init_observer()

    def run(self):
        while self.running:
            self.startup_observer()
            time.sleep(1)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def init_observer(self):
        global my_observer
        self.my_event_handler = Handler()
        self.my_observer = Observer()
        self.my_observer.schedule(self.my_event_handler, path=RAW_DISK_SAVE_PATH, recursive=False)
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
            os.system(f"taskkill /im {GAME_PROCESS}")
            while checkIfProcessRunning(GAME_PROCESS):
                print('Spiel laeuft noch')
            print('Spiel wurde beendet\n Python wird beendet')
            os.system("shutdown /s /t 60")
            sys.exit()
        COUNT +=1
    print(f'Logoff = {LOGOFF}\nCounter_to_logoff =  {counter_to_logoff}\nActual Counter = {COUNT}\n')

def get_last_saves(folder):
    files = list(filter(os.path.isfile, glob.glob(folder + "\\*")))
    files.sort(key=lambda x: os.path.getmtime(x))
    return files[-3:]

def copy_to_ramdisk() -> None: #Kopiere Daten in die RAMDISK
    files = os.listdir(SSD_SAVE_PATH)
    if files == [] or files == "" or files is None:
        print('Keine Savegames gefunden')
    else:
        list_savegames = get_last_saves(SSD_SAVE_PATH)
        print(f'Last Savegames are: {list_savegames}')
        for savegame in list_savegames:
            savegame_filename_only = savegame.split('\\')[-1]
            print('Savegame wird in RAMDISK geladen')
            print(f'Datei: "{savegame}" wird nach "{RAW_DISK_SAVE_PATH}\\{savegame_filename_only}" kopiert!')
            shutil.copy(f'{SSD_SAVE_PATH}\\{savegame_filename_only}', f'{RAW_DISK_SAVE_PATH}\\{savegame_filename_only}')
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
        self.watchdog_var.set('Watchdog gestartet')

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
    if not checkIfProcessRunning(DSPGAME_PROCESS) and not DEBUG:
        print('Spiel wird gestartet')
        subprocess.Popen(r"C:\Program Files (x86)\Steam\Steam.exe -applaunch 1366540")
        while not checkIfProcessRunning(DSPGAME_PROCESS):
            print('Warte auf Spielstart')
            time.sleep(3)
        print('DSP erfolgreich gestartet')
    else:
        print('DSP bereits gestartet')
    if COPY_TO_RAMDISK and not DEBUG:
        copy_to_ramdisk()
    if LOGOFF and not DEBUG:
        shutdowntime = datetime.datetime.now() + datetime.timedelta(minutes=int(COUNTER_TO_LOGOFF*10))
        final_time_str = shutdowntime.strftime('%d/%m/%Y %H:%M:%S')
        print(f'ACHTUNG: Logofftimer aktiviert, herunterfahren in {int(COUNTER_TO_LOGOFF*10)} Minuten! ({final_time_str})')
    print('Watchdog wird gestartet')
    watchdog = threaded_observer()
    print('Watchdog wurde gestartet')
    app = MainWindow(watchdog)
    app.mainloop()





if __name__ == '__main__':
    DEBUG = True
    COPY_TO_RAMDISK = True
    LOGOFF = False
    COUNTER_TO_LOGOFF = 6  # (1 Hour after decide to Logoff).
    main()
