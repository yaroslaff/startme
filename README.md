# startme
startme is systemd/cron alternative for python virtualenv 

## Problem and solution
You have your application. You have also optional component (e.g. telegram bot) which is used only on some of installations. Also, recently you developed other component (e.g. cleanup tool which deletes outdated records from db) which you plan to install on every instance. And maybe many other components which must be started either on boot or periodically.

You may install each module with pip, but afer this you need to activate it: edit systemd .service file and install it (or, for cron jobs, you need to manually add cron job). This makes module installation more complex, long and vulnerable to mistakes.

With startme it is much easier - you should just install module (pip install ...) and on next restart startme will load all modules and will execute it as planned.

## Usage
~~~
# create virtualenv
pipenv shell

# install startme
pipenv install startme

# Now lets run it. Finished immediately. Not very impressive.
(x) xenon@braconnier:/tmp/x$ startme 
startme started
(x) xenon@braconnier:/tmp/x$ 

# Now install example plugin
pipenv install startme-examples

# run again...
(x) xenon@braconnier:/tmp/x$ startme 
StartMeExampleBoot started
startme started
00:20:25 Ticker tick 10
00:20:35 Ticker tick 10
00:20:45 Ticker tick 10
00:20:55 Ticker tick 10
00:21:05 Ticker tick 10
00:21:15 Ticker1min tick 60
00:21:15 Ticker tick 10
00:21:25 Ticker tick 10
~~~

[startme-examples](https://github.com/yaroslaff/startme-examples) has three very simple classes, inherited from `StartMe`. `StartMeExampleBoot` - wants to be executed once on start. `Ticker` wants to be executed every 10 seconds and `Ticker1min` wants to be executed every 1 minute. 

All `StartMe` subclasses are automatically detected, loaded and executed. No need for systemd or cron inside virtualenv. If `startme` installed as systemd unit, example code will be started on restart automatically, no need for any installation except `pip3 install startme-examples`. **Magic!**

You may have dozens of modules in requirements for your package, pip will install it automatically, and startme will start it automatically when startme itself starts from systemd. No matter how complex is your application, installation is one `pip3 install ...` command!

## Advanced usage
Startme uses interruptable [lightsleep](https://github.com/yaroslaff/lightsleep) so you can trigger immediate execution of cron tasks.

~~~
# Session 1, start startme
$ startme --hook redis
...

# Session 2, redis-cli
$ redis-cli publish sleep Ticker1min
$ redis-cli publish sleep Ticker1min
$ redis-cli publish sleep Ticker1min

# Session 1 again, Ticker1min triggered
00:06:28 Ticker1min tick 60
00:06:28 Ticker1min tick 60
00:06:28 Ticker1min tick 60
~~~

## Install

`pip3 install startme` or `pipenv install startme` or `pip3 install git+https://github.com/yaroslaff/startme`.

### Add to systemd
Use your project name instead of `test`:

~~~
startme --systemd test | sudo tee /etc/systemd/system/startme-test.service
sudo systemctl daemon-reload 
sudo systemctl enable startme-test.service
sudo systemctl start startme-test.service
~~~

You may add lightsleep hook parametes to environment file `/etc/default/startme-test`:
~~~
STARTME_HOOK=redis
~~~

## How to write startme modules

Startme workis very simple: It loads all submodules of `startme.mods` (e.g. `startme.mods.yourmodule`), detects all children of `StartMe` class and creates one instance of each class. 

### Methods
There are thee important methods of any class inhereted from StartMe:

#### on_start()
`on_start()` executed once, when startme starts. This method should return in short time. So, if you want to start something long-running, you should start new thread or process,

#### reschedule()
`reschedule()` must return unixtime (e.g. `return time.time() + 60`) when startme should call `on_schedule()` method of this object. After calling `on_schedule()`, startme will call `reschedule()` again.  If `reschedule()` returns `None`, startme will never call it anymore. 

#### on_schedule()
Any your code which must runs periodically, `reschedule()` sets time, when `on_schedule()` will be called.


### Your first startme module
Lets create this very simple file `my.py`:
~~~
from startme import StartMe

class StartTest(StartMe):
    def on_start(self) -> None:
        print(f"{self} started")
~~~

Startme runs modules from same path, where startme package itself is installed. This is usual situation when you install many modules with `pip install ...`. But when you develop new module, you may want to specify path to module without installation. We will use `-m` (`--mods`) for this:
~~~
$ startme -m my.py 
StartTest started
startme started
$
~~~

Now you can create setup.py and install your module with pip from [pypi](https://pypi.org/) or git repository, startme will start it.

Lets try other test module `uptime.py`:
~~~
from startme import StartMe
import time

class Uptime(StartMe):
    def __init__(self):
        self.period = 1
        self.started = time.time()

    def reschedule(self):
        return time.time() + self.period

    def on_schedule(self):
        print(f"Uptime: { int(time.time() - self.started)} seconds")
~~~

Run:
~~~
$ startme -m uptime.py 
startme started
Uptime: 1 seconds
Uptime: 2 seconds
Uptime: 3 seconds
...
~~~

### Startme subclasses
Startme has built-in set of simple, but handy subclasses.

#### StartMeExec
Runs external program. E.g.:
~~~
from startme import StartMeExec

class StartTest(StartMeExec):
    def __init__(self):
        self._exec = ['ls', '-l']
~~~

Rub:
~~~
$ startme -m my.py 
total 8
drwxr-xr-x 2 xenon xenon 4096 May 29 16:30 __pycache__
-rw-r--r-- 1 xenon xenon  121 May 29 16:30 my.py
startme started
~~~

startme blocks when executing this code, so it's good only for quick tasks.

#### StartMeExecNoblock
This is non-blocking version. Lets make some rather long-running program `x.sh`:
~~~
#!/bin/sh
echo `date` started
sleep 5
echo `date` stopped
~~~

my.py:
~~~
from startme import StartMeExecNoblock

class StartTest(StartMeExecNoblock):
    def __init__(self):
        super().__init__()
        self._exec = ['./x.sh']
~~~

Lets run it along with uptime.py to confirm it's not blocking:
~~~
$ startme -m my.py uptime.py 
StartTest start
startme started
Sun May 29 16:47:36 +07 2022 started
Uptime: 1 seconds
Uptime: 2 seconds
Uptime: 3 seconds
Uptime: 4 seconds
Sun May 29 16:47:41 +07 2022 stopped
StartTest return: 0
Uptime: 5 seconds
Uptime: 6 seconds
...
~~~

Next nice feature - just set `self.restart = True` in `__init__()` of StartTest to get auto-restart:
~~~
$ startme -m my.py uptime.py 
StartTest start
startme started
Sun May 29 16:49:32 +07 2022 started
Uptime: 1 seconds
Uptime: 2 seconds
Uptime: 3 seconds
Uptime: 4 seconds
Sun May 29 16:49:37 +07 2022 stopped
StartTest return: 0
StartTest restart
Uptime: 5 seconds
Sun May 29 16:49:37 +07 2022 started
Uptime: 6 seconds
~~~

#### StartMeThread
StartMeThread is nice way to run python code in separate thread.
~~~
from startme import StartMeThread
import time

class StartTest(StartMeThread):
    def code(self):
        while(True):
            print("doing something important in python")
            time.sleep(1)
~~~
~~~
$ startme -m my.py uptime.py 
StartTest start thread
doing something important in python
startme started
Uptime: 1 seconds
doing something important in python
Uptime: 2 seconds
...
~~~

### Embed startme in your program
Instead of using `startme` script, you may embed startme features into your code. see `startme` script sources for example.
~~~
from startme.starter import Starter
....
starter = Starter(hook=args.hook, mods=args.mods)
starter.run()
~~~















