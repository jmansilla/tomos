
def wait_for_input(*args):
    # would be better to react to any key press
    input("[Press Enter]... ")


class Sleeper:
    def __init__(self, delta) -> None:
        self.delta = delta

    def __call__(self, *args):
        from time import sleep
        sleep(self.delta)