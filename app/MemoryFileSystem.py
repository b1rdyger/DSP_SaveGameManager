import os
import shutil
import string
import sys
import time
from ctypes import windll

from fs.osfs import OSFS


class MemoryFileSystem:
    hidden_tag_file = '.tag-ram'
    possible_drives = ['R', 'S', 'T', 'V']
    ram_drive: str or None = None

    def __init__(self, save_path, backup_path):
        self.save_path = save_path
        self.backup_path = backup_path
        self.create_or_just_get()
        time.sleep(0.3)
        if self.delete_save_folder():
            self.create_symlink()

    # noinspection SpellCheckingInspection
    # these drive can be possible ram drives
    def get_mounted_drives(self) -> list:
        bitmask = windll.kernel32.GetLogicalDrives()
        drives = [letter for i, letter in enumerate(string.ascii_uppercase) if bitmask & (1 << i)]
        return list(set(drives).intersection(self.possible_drives))

    def create_or_just_get(self) -> str or None:
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

    def create_ram_drive(self, letter) -> bool:
        success = os.system(f'imdisk -a -s 512M -m "{letter}:" -p "/fs:NTFS /V:SaveGameManager /Q /y"') == 0
        if success and os.path.ismount(f'{letter}:'):
            OSFS(f'{letter}:\\').create(self.hidden_tag_file)
            os.system('attrib +H ' + letter + ':\\' + self.hidden_tag_file)
            self.ram_drive = letter
            return True
        return False

    def destroy_ram_drive(self) -> bool:
        if self.ram_drive:
            return os.system(f'imdisk -D -m "{self.ram_drive}:"') == 0
        return True

    def create_symlink(self) -> bool:
        try:
            os.symlink(self.ram_drive + ':\\', self.save_path)
            if os.readlink(self.save_path):
                return True
        finally:
            pass
        return False

    def delete_save_folder(self) -> bool:
        if not os.path.isdir(self.save_path):
            return False
        if not os.path.isdir(self.backup_path):
            os.mkdir(self.backup_path)
        files_in_save = os.listdir(self.save_path)
        if files_in_save not in [None, '']:
            for file_name in files_in_save:
                if file_name != self.hidden_tag_file:
                    shutil.move(os.path.join(self.save_path, file_name), self.backup_path)
        os.rmdir(self.save_path)
        return True

    def restore_save_empty(self):
        try:
            os.mkdir(self.save_path)
        finally:
            pass

    def __del__(self):
        self.delete_save_folder()
        self.destroy_ram_drive()
        self.restore_save_empty()


if __name__ == '__main__':
    print('MemoryFileSystem.py loaded')
    # p = 'E:\\bla\\save'
    # b = 'E:\\bla\\save-backup'
    # mfs = MemoryFileSystem(p, b)
    # time.sleep(3)
    # del mfs
