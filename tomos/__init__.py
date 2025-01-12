from tomos.ayed2.parser import parser
from tomos.ayed2.evaluation.interpreter import Interpreter
from tomos.ui.interpreter_hooks import RememberState


def parse(source_code=None, file_path=None):
    if source_code is not None and file_path is not None:
        raise ValueError("Only one of source_code or file_path can be provided")
    if source_code is not None:
        ast = parser.parse(source_code)
    elif file_path is not None:
        with open(file_path) as f:
            ast = parser.parse(f.read())
    else:
        raise ValueError("No source_code or file_path was provided")
    return ast


def execute_ast(ast, with_animation_metadata=False):
    """Returns final state and a metadata dict"""
    metadata = {}
    if with_animation_metadata:
        timeline = RememberState()
        post_hooks=[timeline]
        metadata["timeline"] = timeline
    else:
        post_hooks=[]
    interpreter = Interpreter(ast, post_hooks=post_hooks)
    final_state = interpreter.run()
    return final_state, metadata