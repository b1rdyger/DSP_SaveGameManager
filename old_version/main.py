# -*- coding: utf-8 -*-
import datetime
import glob
import os
import shutil
import subprocess
import sys
import time
import tkinter as tk
from threading import Thread

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import tkinter.font as tkFont
import tkinter.messagebox as tkMSG

#Own Classes
from app.MemoryFileSystem import MemoryFileSystem
from app.ConfigSystem import ConfigSystem
from app.global_functions import ProcessChecker, GetLastSaves

#Globals
COUNT = 0
MOVE_COUNT = 0


class Handler(FileSystemEventHandler):
    MOVE_COUNT = 0

    def on_any_event(self, event):
        GAME_PROCESS = bool(ProcessChecker(config.DSPGAME_PROCESS))
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            if GAME_PROCESS or config.DEBUG:
                # Take any action here when a file is first created.
                split_path = event.src_path.split('\\')
                if 'save' in str(split_path[-1]).lower():
                    time.sleep(3)
                    print(f'Datei: "{split_path[-1]}" wird nach "{config.BACKUP_SAVE_PATH}\\{split_path[-1]}" verschoben!')
                    try:
                        shutil.move(f'{event.src_path}', f'{config.BACKUP_SAVE_PATH}\\{split_path[-1]}')
                    except:
                        pass
                    self.MOVE_COUNT += 1
                    if self.MOVE_COUNT == 3:
                        check_logoff()
                        self.MOVE_COUNT = 0
                else:
                    print("Speicherpunkt %s wurde erstellt, aber er wird Ignoriert" % event.src_path)

class threaded_observer(Thread):
    running = False
    def __init__(self):
        Thread.__init__(self)
        self.my_observer = None
        if config.FOLDER_WATCHDOG == "True":
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
        try:
            self.my_observer.schedule(self.my_event_handler, path=config.DSP_SAVEGAME_FOLDER, recursive=False)
        except FileNotFoundError as e:
            tkMSG.showerror('ERROR:', f'Dateipfad "{config.DSP_SAVEGAME_FOLDER}" nicht gefunden\n\n PROGRAMM WIRD BEENDET')
            sys.exit()
        self.my_observer.start()

    def startup_observer(self):
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            my_observer.stop()
            my_observer.join()

def check_logoff():
    global COUNT
    if config.LOGOFF:
        COUNT += 1
        if int(COUNT) == int(config.COUNTER_TO_LOGOFF):
            print('Spiel wird beendet')
            time.sleep(5)
            os.system(f"taskkill /im {config.DSPGAME_PROCESS}")
            while ProcessChecker(config.DSPGAME_PROCESS):
                print('Spiel laeuft noch')
            print('Spiel wurde beendet\n Python wird beendet')
            os.system("shutdown /s /t 60")
            sys.exit()
    if config.DEBUG:
        print(
            f'Logoff = {config.LOGOFF}\nCounter_to_logoff= {int(int(config.COUNTER_TO_LOGOFF) * 10)} min\nActual Counter = {COUNT}\n')


class MainWindow(tk.Tk):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.watchdog = None
        self.LOGOFF = False
        self.title("DSP_SaveGameManager")
        self.wm_attributes("-transparentcolor", "grey")
        #setting window size
        width = 600
        height = 500
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(alignstr)
        self.resizable(width=False, height=False)
        self.labels_view()
        self.messagebox_view()
        self.checkboxes_view()
        self.buttons_view()
        self.update_messages()
        self.main() #Main routine
        self.bind('<Return>', lambda x: self.button_click('start'))
        self.bind('<Escape>', lambda x: self.button_click('stop'))


    def copy_to_ramdisk(self) -> None:
        try:
            files = os.listdir(config.BACKUP_SAVE_PATH)
            found1 = True
        except FileNotFoundError as e:
            tkMSG.showerror('ERROR:',
                            f'Dateipfad nicht gefunden\n"{config.BACKUP_SAVE_PATH}"\n\n Es wird nicht kopiert')
            found1 = False
        try:
            files2 = os.listdir(config.DSP_SAVEGAME_FOLDER)
            found2 = True
        except FileNotFoundError as e:
            found2 = False
            tkMSG.showerror('ERROR:',
                            f'Dateipfad "{config.DSP_SAVEGAME_FOLDER}" nicht gefunden\n\n Es wird nicht kopiert')
        if found1 and found2:
            if files in ['', [], None]:
                print('Keine Savegames gefunden')
            else:
                list_savegames = GetLastSaves(config.BACKUP_SAVE_PATH)
                print(f'Last Savegames are: {list_savegames}')
                for savegame in list_savegames:
                    savegame_filename_only = savegame.split('\\')[-1]
                    print('Savegame wird in RAMDISK geladen')
                    print(
                        f'Datei: "{savegame}" wird nach "{config.DSP_SAVEGAME_FOLDER}\\{savegame_filename_only}" kopiert!')
                    try:
                        shutil.copy2(f'{config.BACKUP_SAVE_PATH}\\{savegame_filename_only}',
                                f'{config.DSP_SAVEGAME_FOLDER}\\{savegame_filename_only}')
                    except FileExistsError:
                        pass
                    time.sleep(1)
        else:
            print('Es wurde nichts kopiert')

    def main(self):
        print('Window wird erstellt')
        print('Ueberprufe Game Prozess')
        if config.COPY_FROM_SAVE_TO_ORIGINAL in [True, "True"]:
            print('COPY_FROM_SAVE_TO_ORIGINAL: Kopiere Savegames')
            self.copy_to_ramdisk()
        if not ProcessChecker(self.config.DSPGAME_PROCESS) and self.config.DSPGAME_START_GAME in [True, "True"]:
            print('Spiel wird gestartet')
            subprocess.Popen(rf"{self.config.STEAM_PATH} -applaunch 1366540")
            while not ProcessChecker(self.config.DSPGAME_PROCESS):
                print('Warte auf Spielstart')
                time.sleep(3)
            print('DSP erfolgreich gestartet')
        else:
            print('DSP bereits gestartet')
        self.watchdog = threaded_observer()

    def labels_view(self):
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

        self.LABEL_LOGOFF=tk.Label(self)
        ft = tkFont.Font(family='Times',size=10)
        self.LABEL_LOGOFF["font"] = ft
        self.LABEL_LOGOFF["fg"] = "#333333"
        self.LABEL_LOGOFF["justify"] = "right"
        self.LABEL_LOGOFF["text"] = f"Logofftimer {int(self.config.COUNTER_TO_LOGOFF) * 10} min"
        self.LABEL_LOGOFF.place(x=120,y=160,width=255,height=30)

    def checkboxes_view(self):
        self.CHECKBOX_DEBUG_VAR = tk.BooleanVar()
        self.CHECKBOX_DEBUG=tk.Checkbutton(self, variable=self.CHECKBOX_DEBUG_VAR)
        ft = tkFont.Font(family='Times',size=10)
        self.CHECKBOX_DEBUG["font"] = ft
        self.CHECKBOX_DEBUG["fg"] = "#333333"
        self.CHECKBOX_DEBUG["justify"] = "center"
        self.CHECKBOX_DEBUG["text"] = ""
        self.CHECKBOX_DEBUG.place(x=390,y=40,width=70,height=25)
        self.CHECKBOX_DEBUG["offvalue"] = False
        self.CHECKBOX_DEBUG["onvalue"] = True
        self.CHECKBOX_DEBUG["command"] = self.CHECKBOX_DEBUG_COMMAND
        self.CHECKBOX_DEBUG.select() if self.config.DEBUG == "True" else self.CHECKBOX_DEBUG.deselect()

        self.CHECKBOX_FOLDER_WATCHDOG_VAR = tk.BooleanVar()
        self.CHECKBOX_FOLDER_WATCHDOG=tk.Checkbutton(self, variable=self.CHECKBOX_FOLDER_WATCHDOG_VAR)
        ft = tkFont.Font(family='Times',size=10)
        self.CHECKBOX_FOLDER_WATCHDOG["font"] = ft
        self.CHECKBOX_FOLDER_WATCHDOG["fg"] = "#333333"
        self.CHECKBOX_FOLDER_WATCHDOG["justify"] = "center"
        self.CHECKBOX_FOLDER_WATCHDOG["text"] = ""
        self.CHECKBOX_FOLDER_WATCHDOG.place(x=390,y=70,width=70,height=25)
        self.CHECKBOX_FOLDER_WATCHDOG["offvalue"] = False
        self.CHECKBOX_FOLDER_WATCHDOG["onvalue"] = True
        self.CHECKBOX_FOLDER_WATCHDOG["command"] = self.CHECKBOX_FOLDER_WATCHDOG_COMMAND
        self.CHECKBOX_FOLDER_WATCHDOG.select() if self.config.FOLDER_WATCHDOG == "True" else self.CHECKBOX_FOLDER_WATCHDOG.deselect()

        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL_VAR = tk.BooleanVar()
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL=tk.Checkbutton(self, variable=self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL_VAR)
        ft = tkFont.Font(family='Times',size=10)
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["font"] = ft
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["fg"] = "#333333"
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["justify"] = "center"
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["text"] = ""
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL.place(x=390,y=100,width=70,height=25)
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["offvalue"] = False
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["onvalue"] = True
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL["command"] = self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL_COMMAND
        self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL.select() if self.config.COPY_FROM_SAVE_TO_ORIGINAL == "True" else self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL.deselect()

        self.CHECKBOX_DSPGAME_START_GAME_VAR = tk.BooleanVar()
        self.CHECKBOX_DSPGAME_START_GAME=tk.Checkbutton(self, variable=self.CHECKBOX_DSPGAME_START_GAME_VAR)
        ft = tkFont.Font(family='Times',size=10)
        self.CHECKBOX_DSPGAME_START_GAME["font"] = ft
        self.CHECKBOX_DSPGAME_START_GAME["fg"] = "#333333"
        self.CHECKBOX_DSPGAME_START_GAME["justify"] = "center"
        self.CHECKBOX_DSPGAME_START_GAME["text"] = ""
        self.CHECKBOX_DSPGAME_START_GAME.place(x=390, y=130, width=70, height=25)
        self.CHECKBOX_DSPGAME_START_GAME["offvalue"] = False
        self.CHECKBOX_DSPGAME_START_GAME["onvalue"] = True
        self.CHECKBOX_DSPGAME_START_GAME["command"] = self.CHECKBOX_DSPGAME_START_GAME_COMMAND
        self.CHECKBOX_DSPGAME_START_GAME.select() if self.config.DSPGAME_START_GAME == "True" else self.CHECKBOX_DSPGAME_START_GAME.deselect()

        self.CHECKBOX_LOGOFF_VAR = tk.BooleanVar()
        self.CHECKBOX_LOGOFF=tk.Checkbutton(self, variable=self.CHECKBOX_LOGOFF_VAR)
        ft = tkFont.Font(family='Times',size=10)
        self.CHECKBOX_LOGOFF["font"] = ft
        self.CHECKBOX_LOGOFF["fg"] = "#333333"
        self.CHECKBOX_LOGOFF["justify"] = "center"
        self.CHECKBOX_LOGOFF["text"] = ""
        self.CHECKBOX_LOGOFF.place(x=390, y=160, width=70, height=25)
        self.CHECKBOX_LOGOFF["offvalue"] = False
        self.CHECKBOX_LOGOFF["onvalue"] = True
        self.CHECKBOX_LOGOFF["command"] = self.CHECKBOX_LOGOFF_COMMAND
        self.CHECKBOX_LOGOFF.select() if self.config.LOGOFF else self.CHECKBOX_LOGOFF.deselect()

    def messagebox_view(self):
        self.MESSAGE_BOX=tk.Message(self)
        ft = tkFont.Font(family='Times',size=10)
        self.MESSAGE_BOX["font"] = ft
        self.MESSAGE_BOX["fg"] = "#333333"
        self.MESSAGE_BOX["justify"] = "center"
        self.MESSAGE_BOX["text"] = "Dies ist ein langer text"
        self.MESSAGE_BOX.place(x=40,y=340,width=497,height=127)

    def buttons_view(self):
        self.BUTTON_SAVE=tk.Button(self)
        self.BUTTON_SAVE["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        self.BUTTON_SAVE["font"] = ft
        self.BUTTON_SAVE["fg"] = "#000000"
        self.BUTTON_SAVE["justify"] = "center"
        self.BUTTON_SAVE["text"] = "Start DSP"
        self.BUTTON_SAVE.place(x=420,y=450,width=70,height=25)
        self.BUTTON_SAVE["command"] = lambda: self.button_click('start')

        self.BUTTON_BEENDEN=tk.Button(self)
        self.BUTTON_BEENDEN["bg"] = "#e9e9ed"
        ft = tkFont.Font(family='Times',size=10)
        self.BUTTON_BEENDEN["font"] = ft
        self.BUTTON_BEENDEN["fg"] = "#000000"
        self.BUTTON_BEENDEN["justify"] = "center"
        self.BUTTON_BEENDEN["text"] = "Beenden"
        self.BUTTON_BEENDEN.place(x=500,y=450,width=70,height=25)
        self.BUTTON_BEENDEN["command"] = lambda: self.button_click('stop')

    def CHECKBOX_DEBUG_COMMAND(self):
        self.config.update_config('DEBUG', self.CHECKBOX_DEBUG_VAR.get())

    def CHECKBOX_FOLDER_WATCHDOG_COMMAND(self):
        self.config.update_config('FOLDER_WATCHDOG', self.CHECKBOX_FOLDER_WATCHDOG_VAR.get())

    def CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL_COMMAND(self):
        self.config.update_config('COPY_FROM_SAVE_TO_ORIGINAL', self.CHECKBOX_COPY_FROM_SAVE_TO_ORIGINAL_VAR.get())

    def CHECKBOX_DSPGAME_START_GAME_COMMAND(self):
        self.config.update_config('DSPGAME_START_GAME', self.CHECKBOX_DSPGAME_START_GAME_VAR.get())

    def CHECKBOX_LOGOFF_COMMAND(self):
        global final_time_str
        if not self.config.LOGOFF:
            self.config.LOGOFF = True
            self.shutdowntime = datetime.datetime.now() + datetime.timedelta(minutes=int(int(self.config.COUNTER_TO_LOGOFF) * 10))
            self.final_time_str = self.shutdowntime.strftime('%d/%m/%Y %H:%M:%S')
            print(f'ACHTUNG: Logofftimer aktiviert, herunterfahren in {int(int(self.config.COUNTER_TO_LOGOFF) * 10)} Minuten! ({self.final_time_str})')
        else:
            self.config.LOGOFF = False
            COUNT = 0
            print('Logofftimer deaktiviert')

    def button_click(self, args):
        if args == 'start':
            self.button_functions('start_dsp')
        if args == 'stop':
            self.button_functions('stop_programm')

    def button_functions(self, args):
        if args == 'start_dsp':
            if not ProcessChecker(self.config.DSPGAME_PROCESS):
                subprocess.Popen(rf"{self.config.STEAM_PATH} -applaunch 1366540")
            else:
                tkMSG.showerror('ERROR!', 'Spiel läuft bereits')

        if args == 'stop_programm':
            if ProcessChecker(self.config.DSPGAME_PROCESS):
                if tkMSG.askokcancel('ACHTUNG!', 'Spiel läuft noch,\nwirklich beenden?'):
                    self.destroy()
                else:
                    tkMSG.showinfo('Oh happy day', 'Programm bleibt aktiv')
            else:
                self.destroy()


    def update_messages(self):
        if ProcessChecker(self.config.DSPGAME_PROCESS):
            self.MESSAGE_BOX["fg"] = "#f00"
            self.BUTTON_SAVE["text"] = "DSP Aktiv!"
            if self.config.LOGOFF:
                self.MESSAGE_BOX[
                    "text"] = f'ACHTUNG!:\nLogoff timer Aktiviert\nDas System wird um\n{self.final_time_str}\nheruntergefahren!!!'
                self.LABEL_LOGOFF["fg"] = "#f00"
                self.LABEL_LOGOFF["text"] = f'Logofftimer: Shutdown um {self.final_time_str}'
            else:
                self.LABEL_LOGOFF["fg"] = "#123"
                self.LABEL_LOGOFF["text"] = f"Logofftimer {int(self.config.COUNTER_TO_LOGOFF) * 10} min"
                self.MESSAGE_BOX[
                    "text"] = 'ACHTUNG!:\nDas Spiel läuft noch, das Programm nicht beenden,\nsonst werden keine Savegames kopiert'
        else:
            self.BUTTON_SAVE["text"] = "Start DSP"
            self.MESSAGE_BOX["text"] = 'Spiel läuft nicht, Programm kann beendet werden'
        self.after(1000, self.update_messages)


def main():
    global config
    config = ConfigSystem()
    mfs = MemoryFileSystem(config.DSP_SAVEGAME_FOLDER, config.BACKUP_SAVE_PATH)
    app = MainWindow(config)
    app.mainloop()

if __name__ == '__main__':
    main()
