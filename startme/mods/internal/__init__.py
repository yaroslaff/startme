from startme import StartMe, StartMeDisabled

class StartBanner(StartMe):
    def on_start(self) -> None:
        print("startme started")
