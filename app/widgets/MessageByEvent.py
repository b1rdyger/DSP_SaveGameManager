from app import EventBus
from app.SGMEvents.FCEEvents import FCHCannotUse
from app.SGMEvents.MFSEvents import *


class MessageByEvent:

    def __init__(self, event_bus: EventBus, callback):
        self.event_bus = event_bus
        self.msg = callback
        self.event_bus.add_listener(MFSDriveCreated, self._drive_created)
        self.event_bus.add_listener(MFSDriveDestroyed, self._drive_destroyed)
        self.event_bus.add_listener(FCHCannotUse, self.cannot_use_path)

    def _drive_created(self):
        self.msg('RAM-Drive created')

    def _drive_destroyed(self):
        self.msg('RAM-Drive removed')

    def cannot_use_path(self, path):
        self.msg(f'Cannot use [error:{path}]')

