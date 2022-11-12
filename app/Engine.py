import json
import os
import threading

from app.EventBus import EventBus
from app.FileCopyHero import FileCopyHero
from app.MemoryFileSystem import MemoryFileSystem
from app.SaveGameManager import SaveGameWindow
from app.widgets.ConsoleOutput import ConsoleOutput


class Engine:
    root_dir = None
    config = None

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self._config_file = root_dir + 'config' + os.sep + 'games.json'
        self._console_output = None
        self._mfs_thread = None
        self._fch_thread = None

        self.load_config()

        self.event_bus = EventBus()

        self.fch = FileCopyHero(self.config, self.event_bus)
        # mfs = MemoryFileSystem(self.config.get('common_save_dir'), self.config.get('backup_save_dir')) # @todo
        # self.mfs = MemoryFileSystem("E:\\bla\\save", "E:\\bla\\save-backup", self.event_bus)

        SaveGameWindow(self)

    def set_write_callback(self, co: ConsoleOutput):
        self._console_output = co
        self._console_output.write("[info:roger that]")

    # engine thread
    def main_runner(self):
        # self._mfs_thread = threading.Thread(target=self.mfs.run).start()
        self._fch_thread = threading.Thread(target=self.fch.run).start()

    def __del__(self):
        # self._mfs_thread.join()
        self._fch_thread.join()

    def load_profile(self):
        profiles = self.config.get('profiles')

    def load_config(self):
        with open(self._config_file, 'r') as read_content:
            self.config = json.load(read_content)

