from app import EventBus
from app.SGMEvents.PCEvents import PCRunning
import threading
import time

from psutil import NoSuchProcess, AccessDenied, process_iter


class ProcessChecker:

    checker_running = False
    process_running = False

    def __init__(self, event_bus: EventBus, process_name: str):
        self.event_bus = event_bus
        self.process_name = process_name.lower()
        self.checker_running = True
        self.t = threading.Thread(target=self.check_if_process_running, daemon=True)
        self.t.start()

    def stop_watching(self):
        self.checker_running = False
        self.t.join()

    def check_if_process_running(self):
        while self.checker_running:
            self.process_running = False
            for proc in process_iter():
                try:
                    if self.process_name in proc.name().lower():
                        self.process_running = True
                except (NoSuchProcess, AccessDenied):
                    self.process_running = False
            self.event_bus.emit(PCRunning, self.process_running)
            time.sleep(1)
