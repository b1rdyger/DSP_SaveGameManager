import json
import logging
import os
import sys
import threading

from app.EventBus import EventBus
from app.FileCopyHero import FileCopyHero, SaveToBlock
from app.MemoryFileSystem import MemoryFileSystem
from app.SaveGameManager import SaveGameWindow
from app.widgets.ConsoleOutput import ConsoleOutput


class Engine:
    root_dir = None
    config = None
    logger = logging.getLogger(__name__)

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self._config_file = f'{root_dir}config{os.sep}games.json'
        self._console_output = None
        self._mfs_thread = None
        self._fch_thread = None

        self.load_config()

        self.event_bus = EventBus()

        self.fch = FileCopyHero(self.event_bus)

        self.fch.set_from_path(self.config.get('common_save_dir'))
        backup_folders = self.config.get('backup_save_dirs')
        for one_backup_folder in backup_folders:
            self.fch.add_save_block(SaveToBlock(one_backup_folder['location']))

        # mfs = MemoryFileSystem(self.config.get('common_save_dir'), self.config.get('backup_save_dir')) # @todo
        self.mfs = MemoryFileSystem(self.config.get('common_save_dir'), self.event_bus)

        SaveGameWindow(self)

    # offer gui console to other modules
    def set_write_callback(self, co: ConsoleOutput):
        self.fch.set_console_write_callback(co.write)
        co.write("Welcome to the [highlighted:SaveGameManager]")

    # engine thread
    def main_runner(self):
        # self.fch.full_backup()
        self.fch.restore_last_save_from_backup()

        # self._mfs_thread = threading.Thread(target=self.mfs.run).start()
        self._fch_thread = threading.Thread(target=self.fch.run, daemon=True).start()

    def __del__(self):
        # self._mfs_thread.join()
        self._fch_thread.join()

    def load_profile(self):
        profiles = self.config.get('profiles')

    def load_config(self):
        with open(self._config_file, 'r') as read_content:
            self.config = json.load(read_content)
