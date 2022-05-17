# startme
autostart for python applications/modules inside single virtualenv

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

All `StartMe` subclasses are automatically detected, loaded and executed. No need for systemd or cron inside virtualenv.