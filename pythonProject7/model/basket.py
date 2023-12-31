from pythonProject7.model.components import Components


class Basket:
    def __init__(self, components=None):
        if components is None:
            components = []
        self.components = components

    @classmethod
    def create(cls):
        component = Components(30, 13)

    def add_component(self, component):
        self.components.append(component)

    def __str__(self):
        return f"Basket with {len(self.components)} components"

    def __repr__(self):
        return '\n'.join([str(component) for component in self.components])
