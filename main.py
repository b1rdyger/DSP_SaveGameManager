import shutil
import subprocess
import sys, os, glob, operator
from threading import Thread
import time
import datetime
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


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
    @staticmethod
    def on_any_event(event):
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
                    MOVE_COUNT += 1
                    if MOVE_COUNT == 3:
                        check_logoff(COUNTER_TO_LOGOFF)
                        MOVE_COUNT = 0
                else:
                    print("Speicherpunkt %s wurde erstellt, aber er wird Ignoriert" % event.src_path)

class threaded_observer(Thread):
    DIRECTORY_TO_WATCH = RAW_DISK_SAVE_PATH
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.init_observer()

    def run(self):
        while self.running:
            self.startup_observer()
            time.sleep(1)

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


def check_newes_safe() -> list: #return hoechstes Safegame
    import re
    saves = []
    print(f'Ueberpruefe Dateien in: {SSD_SAVE_PATH}')
    files = os.listdir(SSD_SAVE_PATH) # Liste der Files im Ordner
    for file in files:
        save_number = re.findall(r'\d+', file) #Extrahiere die Zahlen aus dem Savegame
        saves.append(save_number) if save_number not in saves else saves
    if saves is None or saves == "" or saves == []:
        return None
    else:
        print(f'return {max(saves)}')
        return max(saves)



def get_oldest_file(files, _invert=False):
    """ Find and return the oldest file of input file names.
    Only one wins tie. Values based on time distance from present.
    Use of `_invert` inverts logic to make this a youngest routine,
    to be used more clearly via `get_youngest_file`.
    """
    gt = operator.lt if _invert else operator.gt
    # Check for empty list.
    if not files:
        return None
    # Raw epoch distance.
    now = time.time()
    # Select first as arbitrary sentinel file, storing name and age.
    oldest = files[0], now - os.path.getctime(files[0])
    # Iterate over all remaining files.
    for f in files[1:]:
        age = now - os.path.getctime(f)
        if gt(age, oldest[1]):
            # Set new oldest.
            oldest = f, age
    # Return just the name of oldest file.
    return oldest[0]

def get_last_saves(folder):
    files = list(filter(os.path.isfile, glob.glob(folder + "\\*")))
    files.sort(key=lambda x: os.path.getmtime(x))
    return files[-3:]

def copy_to_ramdisk() -> None: #Kopiere Daten in die RAMDISK
    save_number = check_newes_safe()
    print(save_number)
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

def main():
    print('Ueberprufe Game Prozess')
    if not DEBUG and not checkIfProcessRunning(DSPGAME_PROCESS):
        print('Spiel wird gestartet')
        subprocess.Popen(r"C:\Program Files (x86)\Steam\Steam.exe -applaunch 1366540")
        while not checkIfProcessRunning(DSPGAME_PROCESS):
            print('Warte auf Spielstart')
            time.sleep(3)
        print('DSP erfolgreich gestartet')
    else:
        print('DSP bereits gestartet')
    if COPY_TO_RAMDISK:
        copy_to_ramdisk()
    if LOGOFF and not DEBUG:
        shutdowntime = datetime.datetime.now() + datetime.timedelta(minutes=int(COUNTER_TO_LOGOFF*10))
        final_time_str = shutdowntime.strftime('%d/%m/%Y %H:%M:%S')
        print(f'ACHTUNG: Logofftimer aktiviert, herunterfahren in {int(COUNTER_TO_LOGOFF*10)} Minuten! ({final_time_str})')
    print('Watchdog wird gestartet')
    threaded_observer()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    DEBUG = False
    COPY_TO_RAMDISK = True
    LOGOFF = False
    COUNTER_TO_LOGOFF = 6  # (1 Hour after decide to Logoff).
    main()