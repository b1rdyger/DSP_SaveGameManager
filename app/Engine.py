import json
import sys

from app.ProcessChecker import ProcessChecker
from app.SGMEvents.GuiEvents import SGMStop
from app.global_logging import *
from app.MemoryFileSystemFacade import MemoryFileSystemFacade
import os
import threading

from app.EventBus import EventBus
from app.FileCopyHero import FileCopyHero, SaveToBlock
from app.SaveGameManager import SaveGameWindow
from app.widgets.ConsoleOutput import ConsoleOutput
from app.SGMEvents.MFSEvents import MFSDriveCreated


class Engine:
    root_dir = None
    config = None
    hidden_tag_file = '.tag-ram'

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self._config_file = f'{root_dir}config{os.sep}games.json'
        self._console_output = None
        self._mfs_thread = None
        self._fch_thread = None

        self.load_config()

        self.event_bus: EventBus = EventBus()

        self.fch = FileCopyHero(self.event_bus, self.hidden_tag_file)

        self.fch.set_from_path(self.config.get('common_save_dir'))
        backup_folders = self.config.get('backup_save_dirs')
        for one_backup_folder in backup_folders:
            self.fch.add_save_block(SaveToBlock(one_backup_folder['location']))

        # mfs = MemoryFileSystem(self.config.get('common_save_dir'), self.config.get('backup_save_dir')) # @todo
        self.mfs = MemoryFileSystemFacade(self.config.get('common_save_dir'),
                                          self.event_bus, self.hidden_tag_file).get_concrete()

        self.pc = ProcessChecker(self.event_bus, self.config.get('process_name'))

        # self.event_bus.add_listener(SGMStop, self.stop)

        SaveGameWindow(self)

    # engine thread
    def main_runner(self):
        ram_drive_letter = self.mfs.create_or_just_get()

        if ram_drive_letter is not None and self.fch.backup_for_symlink():
            self.mfs.create_symlink()
            self.fch.restore_last_save_from_backup()

        # self._mfs_thread = threading.Thread(target=self.mfs.run).start()
        self._fch_thread = threading.Thread(target=self.fch.run, daemon=True)
        self._fch_thread.start()

    def stop(self):
        self.pc.stop_watching()
        self._fch_thread.join()
        self.fch.full_backup()
        del self.mfs

    # offer gui console to other modules
    @wrapee()
    def set_write_callback(self, co: ConsoleOutput):
        self.fch.set_console_write_callback(co.write)
        co.write("Welcome to the [highlighted:SaveGameManager]")

    def load_profile(self):
        profiles = self.config.get('profiles')

    def load_config(self):
        with open(self._config_file, 'r') as read_content:
            self.config = json.load(read_content)

