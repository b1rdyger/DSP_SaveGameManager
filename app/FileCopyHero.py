from datetime import datetime, timedelta
import glob
import os
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

from app.FileCreatedObserver import FileCreatedObserver
from app.SGMEvents.FCEEvents import FCHCannotUse, FCHRestored


@dataclass
class SaveToBlock:
    path: Path
    cap_number: int = 0
    cap_size_mb: int = 0
    tpe: str = 'auto'


class FileCopyHero:

    save_from: str = None
    save_to_list: list[SaveToBlock] = []
    log: callable = None

    def __init__(self, event_bus):
        self.fco = None
        self._event_bus = event_bus

    def set_console_write_callback(self, write_callback: callable):
        self.log = write_callback

    def console_log(self, txt: str):
        if self.log:
            self.log(txt)
        else:
            print(txt)

    def set_from_path(self, save_from: str):
        self.save_from = save_from
        self.fco = FileCreatedObserver(self.save_from, self.smart_backup)

    def add_save_block(self, save_to: SaveToBlock):
        self.save_to_list.append(save_to)

    def full_backup(self):
        self.console_log('Full backup')
        files_in_save = os.listdir(self.save_from)
        if files_in_save not in [None, '']:
            self.backup_files(files_in_save)

    def smart_backup(self):
        self.console_log('Smart backup')
        self.full_backup()

    def restore_last_save_from_backup(self) -> bool:
        first_backup_block = next(iter(self.save_to_list or []), None)
        if not first_backup_block:
            return False
        files = list(filter(os.path.isfile, glob.glob(str(first_backup_block.path) + "\\*")))
        files = list(map(lambda f: {'file': f, 'mtime': os.path.getmtime(f)}, files))
        files = sorted(files, key=lambda d: d['mtime'], reverse=True)

        split_dt = 60
        dts = (d0['mtime']-d1['mtime'] for d0, d1 in zip(files, files[1:]))
        split_at = [i for i, dt in enumerate(dts, 1) if dt >= split_dt]
        groups = [files[i:j] for i, j in zip([0]+split_at, split_at+[None])]

        for savegame in groups[0]:
            savegame_filename_only = savegame['file'].split('\\')[-1]
            try:
                shutil.copy(f'{savegame["file"]}', f'{self.save_from}')
                self.console_log(f'[file:{savegame_filename_only}] successfully restored')
                self._event_bus.emit(FCHRestored)
            except Exception as e:
                self.console_log(f'[error:{savegame_filename_only}] was not restored')
                print(e)

    def backup_files(self, files: list[str]):
        for save_to in self.save_to_list:
            if not os.path.isdir(save_to.path):
                try:
                    os.mkdir(save_to.path)
                except FileExistsError:
                    self._event_bus.emit(FCHCannotUse, save_to.path)
                    continue
            for file in files:
                shutil.copy(f'{self.save_from}{os.sep}{file}', f'{save_to.path}')

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

    def run(self):
        self.fco.start()
        while True:
            time.sleep(1)
        pass
