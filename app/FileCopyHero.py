import glob
import logging
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

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

    def __init__(self, event_bus, hidden_tag_file):
        self.fco = None
        self._event_bus = event_bus
        self.hidden_tag_file = hidden_tag_file

    def set_console_write_callback(self, write_callback: callable):
        self.log = write_callback

    def console_log(self, txt: str):
        if self.log:
            self.log(txt)
        else:
            logging.info(txt)

    def set_from_path(self, save_from: str):
        self.save_from = save_from
        self.fco = FileCreatedObserver(self.save_from, self.smart_backup)

    def add_save_block(self, save_to: SaveToBlock):
        self.save_to_list.append(save_to)

    # just save everything everywhere without worrying about the config
    def full_backup(self):
        self.console_log('Full backup')
        files_in_save = os.listdir(self.save_from)
        if files_in_save not in [None, '']:
            self.backup_files(files_in_save)

    # save everything everywhere according to the configuration
    def smart_backup(self, tryy=5) -> bool:
        if tryy == 0:
            self.console_log('[error:Smart backup fehlgeschlagen! Bitte manuelles Backup vornehmen!]')
            return True
        if tryy == 5:
            self.console_log('[highlighted:Starte Smart backup]')
        files_in_save = os.listdir(self.save_from)
        if files_in_save not in [None, '']:
            # @todo get cluster, config, log_rotate
            try:
                self.backup_files(files_in_save)
                self.console_log('[success:Smart backup erfolgreich!]')
            except Exception:
                time.sleep(0.2)
                self.smart_backup(tryy-1)

    def restore_last_save_from_backup(self) -> bool:
        first_backup_block = next(iter(self.save_to_list or []), None)
        if not first_backup_block:
            return False
        files = list(filter(os.path.isfile, glob.glob(str(first_backup_block.path) + "\\*")))
        files = list(map(lambda f: {'file': f, 'mtime': os.path.getmtime(f)}, files))
        files = sorted(files, key=lambda d: d['mtime'], reverse=True)

        split_dt = 59
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
                logging.exception(e)

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

    def backup_for_symlink(self) -> bool:
        first_backup_path = next(iter(self.save_to_list or []), None)
        if first_backup_path is None:
            return False
        else:
            first_backup_path = first_backup_path.path
        if os.path.isdir(self.save_from):
            if not os.path.isdir(first_backup_path):
                os.mkdir(first_backup_path)
            files_in_save = os.listdir(self.save_from)
            if files_in_save not in [None, '']:
                for file_name in files_in_save:
                    if file_name != self.hidden_tag_file:
                        shutil.copy(os.path.join(self.save_from, file_name), first_backup_path)
                        time.sleep(0.3)
                        os.remove(os.path.join(self.save_from, file_name))
            os.rmdir(self.save_from)
            return True
        return False

    def run(self):
        self.fco.start()
