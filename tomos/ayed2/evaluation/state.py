UNKNOWN_VALUE = object()


class State:
    def __init__(self):
        self.stack = {}
        self.stack_types = {}
        self.heap = {}
        self.heap_types = {}

    def set_stack_type(self, name, type):
        self.stack_types[name] = type

    def update_stack(self, name, value, type):
        self.stack[name] = value

    def update_heap(self, name, value):
        self.heap[name] = value

    def set_heap_type(self, name, type):
        self.heap[name] = type
