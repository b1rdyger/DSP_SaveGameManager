import time


class FileCopyHero:
    def __init__(self, config, event_bus):
        self.config = config
        self._event_bus = event_bus
        pass

    def run(self):
        while True:
            time.sleep(1)
        pass
