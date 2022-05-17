
class meta(type):
    __inheritors__ = list()

    def __new__(meta, name, bases, dct):
        klass = type.__new__(meta, name, bases, dct)
        meta.__inheritors__.append(klass)
        return klass

class StartMe(metaclass=meta):
        
    def __init__(self):
        pass

    def on_start(self):
        pass

    def on_shedule(self):
        pass

    def reschedule(self):
        return None

    def __repr__(self):
        return type(self).__name__


class x(StartMe):
    pass