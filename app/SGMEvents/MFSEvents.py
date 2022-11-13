from app.SGMEvents.__SGMEvent import SGMEvent


class MFSDriveCreated(SGMEvent):
    pass


class MFSDriveDestroyed(SGMEvent):
    pass


class MFSSavePathNotEmpty(SGMEvent):
    pass


class MFSSavePathDoesNotExists(SGMEvent):
    pass


class MFSSymlinkCreated(SGMEvent):
    pass


class MFSSymlinkRemoved(SGMEvent):
    pass
