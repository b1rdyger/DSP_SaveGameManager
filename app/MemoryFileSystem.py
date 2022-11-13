import os
import shutil
import string
import time
from ctypes import windll

import numpy as np
from fs.osfs import OSFS

from app import EventBus
from app.SGMEvents.MFSEvents import *


class MemoryFileSystem:
    possible_drives = ['R', 'S', 'T', 'V']  # https://en.wikipedia.org/wiki/Drive_letter_assignment#Common_assignments
    ram_drive: str = None

    def __init__(self, save_path, event_bus: EventBus, hidden_tag_file: str):
        self._event_bus = event_bus
        self.save_path = save_path
        self.hidden_tag_file = hidden_tag_file

    def __replace_path_with_symlink(self) -> bool:
        if os.listdir(self.save_path):
            self._event_bus.emit(MFSSavePathNotEmpty)
            return False
        if not os.path.isdir(self.save_path):
            self._event_bus.emit(MFSSavePathDoesNotExists)
            return False
        os.rmdir(self.save_path)
        self.create_symlink()
        return True

    # noinspection SpellCheckingInspection
    # these drive can be possible ram drives
    def __get_mounted_drives(self) -> list:
        bitmask = windll.kernel32.GetLogicalDrives()
        drives = [letter for i, letter in enumerate(string.ascii_uppercase) if bitmask & (1 << i)]
        return list(set(drives).intersection(self.possible_drives))

    def create_or_just_get(self) -> str | None:
        drives = self.__get_mounted_drives()
        for letter in drives:
            if os.path.isfile(letter + ':\\' + self.hidden_tag_file):
                self.ram_drive = letter
                return self.ram_drive
        if all_good_drives := [i for i in self.possible_drives if i not in drives]:
            first_good_drive = all_good_drives[0]
            self.__create_ram_drive(first_good_drive)
            self.ram_drive = first_good_drive
            return self.ram_drive
        else:
            return None

    def __create_ram_drive(self, letter, size: int = 512) -> bool:
        size = np.clip(size, 4, 8192)
        success = os.system(f'imdisk -a -s {size}M -m "{letter}:" -p "/fs:NTFS /V:SaveGameManager /Q /y"') == 0
        if success and os.path.ismount(f'{letter}:'):
            OSFS(f'{letter}:\\').create(self.hidden_tag_file)
            os.system(f'attrib +H {letter}' + ':\\' + self.hidden_tag_file)
            self.ram_drive = letter
            self._event_bus.emit(MFSDriveCreated)
            return True
        return False

    def __destroy_ram_drive(self, ram_drive_letter=None) -> bool:
        if ram_drive_letter is None:
            ram_drive_letter = self.ram_drive
        if ram_drive_letter:
            ret = os.system(f'imdisk -D -m "{ram_drive_letter}:"') == 0
            if ret:
                self._event_bus.emit(MFSDriveDestroyed)
            return ret
        return True

    def destroy_all_ram_drives(self):
        drives = self.__get_mounted_drives()
        for letter in drives:
            if os.path.isfile(letter + ':\\' + self.hidden_tag_file):
                self.__destroy_ram_drive(letter)

    def create_symlink(self) -> bool:
        try:
            os.symlink(self.ram_drive + ':\\', self.save_path)
            if os.readlink(self.save_path):
                self._event_bus.emit(MFSSymlinkCreated)
                return True
        finally:
            pass
        return False

    def restore_save_empty(self) -> bool:
        if os.path.islink(self.save_path):
            os.rmdir(self.save_path)
            os.mkdir(self.save_path)
            self._event_bus.emit(MFSSymlinkRemoved)
            return True
        return False

    def __del__(self):
        self.__destroy_ram_drive()
        self.restore_save_empty()
