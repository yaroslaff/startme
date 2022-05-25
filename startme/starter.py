import pkgutil
import importlib
import time

import startme.mods

from lightsleep import Sleep

def iter_namespace(ns_pkg):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


class Starter:
    def __init__(self, hook):
        self._lsleep = Sleep(hook=hook)


    def load_mods(self):
        mods = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in iter_namespace(startme.mods)
        }

    def startup(self):

        self._smjobs = [ cls() for cls in startme.meta.__inheritors__ ]

        for j in self._smjobs:
            j.on_start()

        self._sch = {
            j: j.reschedule()
            for j in self._smjobs 
        }

    def clean_sch(self):
        self._sch = {k:v for k,v in self._sch.items() if v is not None}

    def run(self):


        self.load_mods()
        self.startup()


        while True:
            self.clean_sch()

            if not self._sch:
                return 

            # Execute tasks on schedule
            now = time.time()
            for j, jtime in self._sch.items():
                if  now>=jtime:
                    j.on_schedule()
                    self._sch[j] = j.reschedule()

            # Calculate time to next run
            sch_list = [ time for j, time in self._sch.items() if time is not None]
            if not sch_list:
                return
            exectime = min(sch_list)

            # lightsleep before next run (maybe wake sooner)
            data = self._lsleep.sleep(exectime - time.time())
            if data:
                for j in self._sch:
                    if j.__class__.__name__ == data:
                        j.on_schedule()
                        self._sch[j] = j.reschedule()

