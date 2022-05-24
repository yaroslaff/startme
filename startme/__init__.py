import subprocess
import threading
import time

class meta(type):
    __inheritors__ = list()

    def __new__(meta, name, bases, dct):
        klass = type.__new__(meta, name, bases, dct)
        meta.__inheritors__.append(klass)
        return klass

class StartMe(metaclass=meta):
    
    period = None

    def __init__(self):
        pass

    def on_start(self):
        pass

    def on_schedule(self):
        pass

    def reschedule(self):
        if self.period:
            return time.time() + self.period
        return None

    def __repr__(self):
        return type(self).__name__


class StartMeExec(StartMe):
    def __init__(self):
        self._exec = None

    def on_start(self):
        if self._exec:
            subprocess.run(self._exec)

class StartMeExecNoblock(StartMe):
    def __init__(self):
        self._exec = None
        self.period = 1
        self.process = None
        self.restart = False

    def on_start(self):
        if self._exec:
            self.process = subprocess.Popen(self._exec)
            print(f"{self} start")

    def reschedule(self):
        if not self._exec:
            return None
        if self.process is None:
            return None
        
        return time.time() + self.period


    def on_schedule(self):
        if self.process:
            self.process.poll()
            if self.process.returncode is not None:
                print(f"{self} return: {self.process.returncode}")
                self.process.wait()
                self.process = None

                if self.restart:
                    print(f"{self} restart")
                    self.process = subprocess.Popen(self._exec)



class StartMeThread(StartMe):
    def __init__(self):
        if hasattr(self, 'code'):        
            print(f"{self} start thread")
            self.th = threading.Thread(target = self.code)
            self.th.start()
        else:
            # do not start thread
            self.th = None
            pass

    def reschedule(self):
        if self.th:
            return super().reschedule()

    def on_schedule(self):
        if self.th and not self.th.is_alive():
            print(f"{self} stopped")
            self.th.join()
            self.th = None
