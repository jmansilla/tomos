# τόμος  -  tomos

Tomographies for your code

![code tomography logo](https://github.com/user-attachments/assets/1138b7bb-815a-43e4-8384-c742ce029c76)


## What it's tomos?

It's and interpreter of AyED2 language, and also a memory visualizer of executions.

The grammar of the language can be found
[here](https://github.com/jmansilla/tomos/blob/main/tomos/ayed2/parser/grammar.lark).
You can also find simple examples in [this folder](https://github.com/jmansilla/tomos/tree/main/demo/ayed2_examples), and a bit more complex ones with these [linked_list](https://github.com/jmansilla/tomos/tree/main/demo/linked_list) or [bubble_sort](https://github.com/jmansilla/tomos/tree/main/demo/bubble_sort) ones.

### installation & usage

A simple pip install should do it. It's recommened to install it on a virtual environment, but it's up to you.

```
]$ pip install tomos
```

After installed, you should have a new command named `tomos`, and you can check everything it's working fine by running

```
]$ tomos --version
```

Assuming you have a valid AyED2 file (example.ayed), you can run the interpreter like this:

```
]$ tomos example.ayed
```

that should show on screen the final state of such execution.

If you want to generate the visualization trace, add the parameter `--autoplay`.

For a complete list of options, use `--help`





