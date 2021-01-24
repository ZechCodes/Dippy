import bevy


class Component(bevy.Injectable):
    __components__ = []

    def __init_subclass__(cls, **kwargs):
        Component.__components__.append(cls)
