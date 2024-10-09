from dataclasses import dataclass


class RememberState:
    @dataclass
    class Frame:
        line_number: int
        last_sentence: object
        state: object
        expression_values: dict

    def __init__(self):
        self.timeline = []

    def __call__(self, last_sentence, state, expression_values):
        f = self.Frame(last_sentence.line_number, last_sentence, state, expression_values)
        self.timeline.append(f)

