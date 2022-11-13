from configparser import ConfigParser
import os

class ConfigSystem():
    LOGOFF = False
    configfile = "./config/config.ini"
    """
    This class will check if there is a config file.
    If there is a configfile this will be loaded.
    If not a configfile will be created.
    """
    def __init__(self):
        self.config = ConfigParser()
        self.check_configfile()
        self.LOGOFF = False

    def check_configfile(self):
        if not os.path.isfile(self.configfile):
            print('No config found')
            self.config.add_section('debug')
            self.config.set('debug', 'DEBUG', 'True')
            self.config.add_section('main')
            self.config.set('main', 'DSPGAME_START_GAME', 'True')
            self.config.set('main', 'FOLDER_WATCHDOG', 'True')
            self.config.set('main', 'DSP_SAVEGAME_FOLDER', rf'C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\Save')
            self.config.set('main', 'BACKUP_SAVE_PATH', rf'C:\Users\{os.getlogin()}\Documents\Dyson Sphere Program\save_backup' )
            self.config.set('main', 'COPY_FROM_SAVE_TO_ORIGINAL', 'True')
            self.config.set('main', 'DSPGAME_PROCESS',  'DSPGAME.exe')
            self.config.set('main', 'STEAM_PATH', r'C:\Program Files (x86)\Steam\Steam.exe')
            self.config.add_section('logoff')
            self.config.set('logoff', 'COUNTER_TO_LOGOFF', '6')

            with open(self.configfile, 'w') as f:
                self.config.write(f)
            print('Config: "config.ini" created')
        else:
            print('Config: "config.ini" found')
        try:
            self.config.read(self.configfile)
        except:
            print('Config: cannot read "config.ini"')
        print('Config: set varaibles')
        self.read_config()

    def read_config(self) -> bool:
        try:
            self.DEBUG = self.config.get('debug', 'DEBUG')
            self.FOLDER_WATCHDOG = self.config.get('main','FOLDER_WATCHDOG')
            self.DSP_SAVEGAME_FOLDER = self.config.get('main', 'DSP_SAVEGAME_FOLDER')
            self.BACKUP_SAVE_PATH = self.config.get('main', 'BACKUP_SAVE_PATH')
            self.COPY_FROM_SAVE_TO_ORIGINAL = self.config.get('main', 'COPY_FROM_SAVE_TO_ORIGINAL')
            self.DSPGAME_PROCESS = self.config.get('main', 'DSPGAME_PROCESS')
            self.DSPGAME_START_GAME = self.config.get('main', 'DSPGAME_START_GAME')
            self.STEAM_PATH = self.config.get('main', 'STEAM_PATH')
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
                print('Config: set global variables sucessfully')
                return True
        except KeyError as e:
            print(f'Config: {e}, Error read the configfile')
            return False

    def update_config(self, checkbox, state):
        self.config.read(self.configfile)
        print(f'checkbox: {checkbox}, state={state}')
        if 'DEBUG' in checkbox:
            self.config.set('debug', f'{checkbox}', f'{state}')
        else:
            self.config.set('main', f'{checkbox}', f'{state}')
        with open(self.configfile, 'w+') as f:
            self.config.write(f)

if __name__ == '__main__':
    print('ConfigSystem loaded')