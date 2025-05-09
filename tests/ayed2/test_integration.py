import ast
import pathlib
from unittest import TestCase

from tomos.ayed2.ast.types.enum import EnumConstant
from tomos.ayed2.parser import parser
from tomos.ayed2.evaluation.interpreter import Interpreter
from tomos.ayed2.evaluation.memory import MemoryAddress
from tomos.ayed2.evaluation.unknown_value import UnknownValue


integrations_folder = pathlib.Path(__file__).parent.resolve() / "integrations"
splitter = "// EXPECTATION\n"
error_marker = "ERROR:"


class ExpectedTraceback:
    def __init__(self, expected):
        raw_msg = expected.split(error_marker, 1)[1]
        klass_name, msg = map(str.strip, raw_msg.split(":", 1))
        import importlib
        self.klass = __builtins__.get(klass_name, None)
        if self.klass is None:
            if '.' in klass_name:
                module_name, pure_klass_name = klass_name.rsplit('.', 1)
                module = importlib.import_module(module_name)
                self.klass = getattr(module, pure_klass_name)
        if self.klass is None:
            raise ValueError(f"Unknown exception class \"{klass_name}\"")
        self.msg = msg


def list_test_files(folder_path):
    for file in folder_path.iterdir():
        if file.is_file() and (file.suffix == ".ayed" or file.suffix == ".ayed2"):
            yield file


def split_code_and_expectation(file_path):
    with open(file_path) as f:
        content = f.read()
    if content.count(splitter) != 1:
        raise ValueError(
            f"File {file_path} does not contain the splitter {splitter} (or has more than one)"
        )
    code, raw_expect = content.split(splitter)
    raw_expect = raw_expect.replace("//", "").strip()
    if raw_expect.startswith(error_marker):
        expect = ExpectedTraceback(raw_expect)
    else:
        expect = ast.literal_eval(raw_expect)
    return code, expect


def execute_code(code):
    tree = parser.parse(code)
    interpreter = Interpreter(tree)
    final_state = interpreter.run()
    return final_state


def state_as_python_dict(state):
    result = {}
    for block_name in ["stack", "heap"]:
        state_block = getattr(state, block_name, {})
        block = {}
        for name, cell in state_block.items():
            block[name] = cell.value
        result[block_name] = block
    return result


class IntegrationMeta(type):
    """Builds test functions before unittest does its discovery."""

    def __new__(mcs, name, bases, dict):

        def gen_test(ff):
            def test(self):
                code, expected = split_code_and_expectation(ff)
                if isinstance(expected, ExpectedTraceback):
                    with self.assertRaisesRegex(expected.klass, expected.msg):
                        execute_code(code)
                else:
                    actual = state_as_python_dict(execute_code(code))
                    self.assertStackEqual(actual.get("stack", {}), expected.get("stack", {}))
                    self.assertHeapEqual(actual.get("heap", {}), expected.get("heap", {}))
            return test

        for file in list_test_files(integrations_folder):
            test_name = "test_" + file.stem
            dict[test_name] = gen_test(file)
        return type.__new__(mcs, name, bases, dict)


class TestIntegrationsRunner(TestCase, metaclass=IntegrationMeta):

    def setUp(self):
        self.addresses_translation = {}

    def assertStackEqual(self, actual, expected):
        self.assertSetEqual(set(actual.keys()), set(expected.keys()))
        for k, v in expected.items():
            actual_val = actual[k]
            self.assertMemoryEqual(actual_val, v, "stack", k)

    def assertMemoryEqual(self, actual_value, expected_value, block_name, key):
        base_msg = f"On block {block_name}, name: {key}"
        if actual_value == UnknownValue:
            actual_value = "<?>"
        if isinstance(actual_value, MemoryAddress):
            msg = (
                "Expected addresses must be strings in the form of H<number> or S<number>. Not %s"
                % expected_value
            )
            self.assertIsInstance(expected_value, str, msg)
            self.assertTrue(expected_value.startswith("H") or expected_value.startswith("S"), msg)
            address = str(actual_value)
            actual_value = self.addresses_translation.setdefault(
                address, expected_value
            )  # translation made.
        if isinstance(actual_value, EnumConstant):
            self.assertEqual(str(actual_value), expected_value)
        elif isinstance(expected_value, list):
            self.assertIsInstance(
                actual_value, list, f"{base_msg}, Expected {actual_value} to be a list"
            )
            l_a, l_e = len(actual_value), len(expected_value)
            self.assertEqual(l_a, l_e, f"List lengths differ {l_a} != {l_e}. {base_msg}.")
            for idx, (a, e) in enumerate(zip(actual_value, expected_value)):
                self.assertMemoryEqual(a, e, f"{block_name}:{key} list", idx)
        elif isinstance(expected_value, dict):
            self.assertIsInstance(
                actual_value, dict, f"{base_msg}, Expected {actual_value} to be a dict"
            )
            k_a, k_e = actual_value.keys(), expected_value.keys()  # type: ignore
            self.assertEqual(k_a, k_e, f"Dict keys differ {k_a} != {k_e}. {base_msg}.")
            for subkey in expected_value.keys():
                self.assertMemoryEqual(
                    actual_value[subkey], expected_value[subkey], f"{block_name}:{key} dict", subkey
                )
        else:
            self.assertEqual(actual_value, expected_value, base_msg)

    def assertHeapEqual(self, actual, expected):
        # first adapt actual keys according to translations
        translated_actual = {}
        for ak, av in actual.items():
            if isinstance(ak, MemoryAddress):
                address = str(ak)
                if address in self.addresses_translation:
                    address = self.addresses_translation[address]
                translated_actual[address] = av
            else:
                self.fail(
                    f"Unexpected key {ak} of type {type(ak)} on Heap. Expected MemoryAddress only."
                )

        self.assertSetEqual(set(translated_actual.keys()), set(expected.keys()))
        for k, v in expected.items():
            actual_val = translated_actual[k]
            self.assertMemoryEqual(actual_val, v, "heap", k)
