class Runner:
    def __init__(self, installer):
        self.installer = installer
        installer.set_runner(self)
        pass

    def process(self):
        return True

    def key_event(self, keys):
        return True
