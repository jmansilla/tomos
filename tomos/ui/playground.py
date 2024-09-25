from tomos.ui.interpreter_hooks import ShowSentence, ShowState, Sleeper, wait_for_input


if __name__ == "__main__":
    import sys
    from tomos.ayed2.parser import parser
    from tomos.ayed2.evaluation.interpreter import Interpreter

    source = sys.argv[1]
    ast = parser.parse(open(source).read())
    print(ast.pretty())

    interpreter = Interpreter(ast,
                              pre_hooks=[ShowSentence(source, full=True),
                                        #  Sleeper(0.5),
                                         wait_for_input,
                                         ],
                              post_hooks=[ShowState('state.mem'), ])
    if "--run" in sys.argv:
        result = interpreter.run()
        print(result)
    elif "-i" in sys.argv:
        print (sys.argv)
        import ipdb; ipdb.set_trace()


