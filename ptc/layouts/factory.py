class LayoutFactory:
    def __init__(self, viewer):
        self.viewer = viewer
        self.available_managers = []

    def get_manager(self, name):
        for manager in self.available_managers:
            if manager.handle(name):
                return manager

        return None

    def register_manager(self, manager):
        self.available_managers.append(manager)
