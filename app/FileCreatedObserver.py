import os.path
import pathlib
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileCreatedObserver:

    def __init__(self, save_game_path: str, backup_func):
        self.save_game_path = save_game_path
        self.my_event_handler = Handler(backup_func)
        self.my_observer = None
        self.init_observer()

    def __del__(self):
        self.stop()
        self.my_observer.join()

    def init_observer(self):
        self.my_observer = Observer()
        try:
            self.my_observer.schedule(self.my_event_handler, path=self.save_game_path, recursive=False)
        finally:
            pass

    def start(self):
        self.my_observer.start()

    def stop(self):
        self.my_observer.stop()


class Handler(FileSystemEventHandler):

    def __init__(self, backup_func):
        self.backup_func = backup_func

    def on_any_event(self, event):
        if event.is_directory:
            return None
        elif event.event_type == 'created':
            self.backup_func()
