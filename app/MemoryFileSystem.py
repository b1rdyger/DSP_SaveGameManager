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
    hidden_tag_file = '.tag-ram'
    possible_drives = ['R', 'S', 'T', 'V']  # https://en.wikipedia.org/wiki/Drive_letter_assignment#Common_assignments
    ram_drive: str = None

    def __init__(self, save_path, backup_path, event_bus: EventBus):
        self._event_bus = event_bus
        self.save_path = save_path
        self.backup_path = backup_path

    def run(self):
        self.create_or_just_get()
        time.sleep(0.3)
        if self._delete_save_folder():
            self._create_symlink()

    # noinspection SpellCheckingInspection
    # these drive can be possible ram drives
    def get_mounted_drives(self) -> list:
        bitmask = windll.kernel32.GetLogicalDrives()
        drives = [letter for i, letter in enumerate(string.ascii_uppercase) if bitmask & (1 << i)]
        return list(set(drives).intersection(self.possible_drives))

    def create_or_just_get(self) -> str | None:
        drives = self.get_mounted_drives()
        for letter in drives:
            if os.path.isfile(letter + ':\\' + self.hidden_tag_file):
                self.ram_drive = letter
                return self.ram_drive
        all_good_drives = [i for i in self.possible_drives if i not in drives]
        if len(all_good_drives) > 0:
            first_good_drive = all_good_drives[0]
            self.create_ram_drive(first_good_drive)
            self.ram_drive = first_good_drive
            return self.ram_drive
        else:
            raise Exception('no free drive')

    def create_ram_drive(self, letter, size: int = 512) -> bool:
        size = np.clip(size, 4, 8192)
        success = os.system(f'imdisk -a -s {size}M -m "{letter}:" -p "/fs:NTFS /V:SaveGameManager /Q /y"') == 0
        if success and os.path.ismount(f'{letter}:'):
            OSFS(f'{letter}:\\').create(self.hidden_tag_file)
            os.system(f'attrib +H ' + letter + ':\\' + self.hidden_tag_file)
            self.ram_drive = letter
            self._event_bus.emit(MFSDriveCreated)
            return True
        return False

    def destroy_ram_drive(self) -> bool:
        if self.ram_drive:
            ret = os.system(f'imdisk -D -m "{self.ram_drive}:"') == 0
            if ret:
                self._event_bus.emit(MFSDriveDestroyed)
            return ret
        return True

    def _create_symlink(self) -> bool:
        try:
            os.symlink(self.ram_drive + ':\\', self.save_path)
            if os.readlink(self.save_path):
                self._event_bus.emit('mfs.symlink.created')
                return True
        finally:
            pass
        return False

    def _delete_save_folder(self) -> bool:
        if os.path.isdir(self.save_path):
            if not os.path.isdir(self.backup_path):
                os.mkdir(self.backup_path)
            files_in_save = os.listdir(self.save_path)
            if files_in_save not in [None, '']:
                for file_name in files_in_save:
                    if file_name != self.hidden_tag_file:
                        shutil.move(os.path.join(self.save_path, file_name), self.backup_path)
            os.rmdir(self.save_path)
            return True
        return False

    def _restore_save_empty(self) -> bool:
        if os.path.islink(self.save_path):
            os.rmdir(self.save_path)
            os.mkdir(self.save_path)
            self._event_bus.emit('mfs.symlink.removed')
            return True
        return False

    def __del__(self):
        self.destroy_ram_drive()
        self._restore_save_empty()


if __name__ == '__main__':
    p = 'E:\\bla\\save'
    b = 'E:\\bla\\save-backup'
    mfs = MemoryFileSystem(p, b, None)
    time.sleep(3)
    del mfs



