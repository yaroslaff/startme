# startme
startme is systemd/cron alternative for python virtualenv 

## Problem and solution
Sometimes python application is complex and modular. For example, you may have:
- wsgi web application
- telegram bot
- some database maintenance 
- send marketing emails
- ... and more and more

Some of these modules are optional. How to install it (say, telegram bot)? You may install it with pip, but then you need to activate it - edit systemd .service file and install it. Or, for cron jobs, you need to manually add cron job. This makes module installation more complex, long and vulnerable to mistakes.

Startme looks for subclasses of StartMe class and executes it.

## Usage
~~~
# create virtualenv
pipenv shell

# install startme
pipenv install startme

# Now lets run it. Not very impressive.
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

Look [startme-examples](https://github.com/yaroslaff/startme-examples) sources as documentation, it's very small. For example, `StartMeExampleBoot` is just one class with one method with just one line of code.

~~~
from startme import StartMe

class StartMeExampleBoot(StartMe):
    def on_start(self):
        print(self.__class__.__name__, "started")
~~~

All `StartMe` subclasses are automatically detected, loaded and executed. No need for systemd or cron inside virtualenv.

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