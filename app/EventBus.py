from app.SGMEvents.__SGMEvent import SGMEvent


class EventBus:
    listeners = {}

    def add_listener(self, event_name, callback):
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)

    def remove_listener(self, event_name, callback):
        self.listeners[event_name].remove(callback)
        if len(self.listeners) == 0:
            del self.listeners[event_name]

    def remove_all_listener(self):
        self.listeners = {}

    def emit(self, event_name: SGMEvent | str, arguments=None):
        listeners = self.listeners.get(event_name, [])
        for listener in listeners:
            listener(arguments) if arguments else listener()

    def __del__(self):
        self.remove_all_listener()
