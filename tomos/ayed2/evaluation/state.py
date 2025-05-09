from tomos.ayed2.ast.types import ArrayOf, Tuple, Synonym
from tomos.exceptions import (
    AlreadyDeclaredVariableError,
    MemoryInfrigementError,
    TomosRuntimeError,
    TomosTypeError,
    UndeclaredVariableError,
)
from tomos.ayed2.evaluation.memory import MemoryAllocator, MemoryAddress
from tomos.ayed2.evaluation.unknown_value import UnknownValue
from tomos.ayed2.evaluation.limits import LIMITER


class State:
    def __init__(self):
        self.allocator = MemoryAllocator()  # creates references to memory cells & clusters
        self.stack = dict()  # stack. Maps names -> cells
        self.heap = dict()  # heap.  Maps mem_address -> cells

    def set_expressions_evaluator(self, evaluator):
        self.evaluator = evaluator

    def __str__(self):
        return f"State(stack={self.stack}, heap={self.heap})"

    def get_expression_evaluator(self):
        if not hasattr(self, "evaluator"):
            raise TomosRuntimeError("Expression evaluator not set.")
        return self.evaluator

    def declare_static_variable(self, name, var_type, read_only=False):
        if name in self.stack:
            raise AlreadyDeclaredVariableError(f"Variable {name} already declared.")
        cell = self.allocator.allocate(MemoryAddress.STACK, var_type)
        if read_only and cell.can_get_set_values_directly:
            cell.read_only = True
        self.stack[name] = cell
        LIMITER.check_type_sizing_limits(var_type)
        LIMITER.check_memory_size_limits(self)

    def undeclare_static_variable(self, name):
        # deletes a variable from the stack. Typicall used when for loop ends
        if name not in self.stack:
            raise UndeclaredVariableError(f"Variable {name} was not declared.")
        del self.stack[name]

    def alloc(self, var):
        # Argument "var" refers to a variable in the stack. Should be a pointer.
        # After the allocation, the variable will "point" to the allocated memory,
        # where "pointing" means that in the stack it will be saved the address of the allocated memory.
        stack_cell = self.cell_after_traversal(var)

        # We need to get ride of Synonyms twice. One for the type, another for the pointed type.
        var_type = stack_cell.var_type
        if isinstance(var_type, Synonym):
            var_type = var_type.underlying_type_closure()

        if not var_type.is_pointer:
            raise TomosTypeError(f"Cannot allocate. Variable {var} is not a pointer.")

        new_cell_type = var_type.of  # type: ignore
        if isinstance(new_cell_type, Synonym):
            new_cell_type = new_cell_type.underlying_type_closure()
        new_cell = self.allocator.allocate(MemoryAddress.HEAP, new_cell_type)
        stack_cell.value = new_cell.address
        self.heap[new_cell.address] = new_cell
        LIMITER.check_memory_size_limits(self)

    def free(self, var):
        # Argument "var" refers to a variable in the stack. Should be a pointer.
        # It should "point" to a previously allocated memory (in the heap). After free, the previously
        # allocated memory will be removed from the heap, and the variable will "point" to UnknownValue.
        stack_cell = self.cell_after_traversal(var)
        if not stack_cell.var_type.is_pointer:
            raise TomosTypeError(f"Cannot free. Variable {var} is not a pointer.")
        if stack_cell.value not in self.heap:
            msg = f"Cannot free. Variable {var} (pointing to {stack_cell.value}) is not pointing to memory cell on the heap."
            raise MemoryInfrigementError(msg)
        del self.heap[stack_cell.value]
        stack_cell.value = UnknownValue

    def cell_after_traversal(self, var):
        # AST Variables have a traversal_path attribute which is a list of steps.
        # Example: if the expression is days[i+1].year, a traversal path should start
        # with the "days" variable, first step should be an ArrayIndexing for (i+1),
        # and following step should be an AccessedField step for "year".

        # Returns the memory cell resulting of walking each of the mentioned steps.

        name = var.name
        if name not in self.stack:
            raise UndeclaredVariableError(f'Can\'t access variable "{name}". It was not declared.')
        cell = self.stack[name]
        for step in var.traverse_path:
            if step.kind == var.DEREFERENCE:
                assert cell.var_type.is_pointer
                if cell.value not in self.heap:
                    msg = f"Accessing var {var}. Can't dereference a pointer to address ({cell.value})"
                    raise MemoryInfrigementError(msg)
                cell = self.heap[cell.value]
            elif step.kind == var.ARRAY_INDEXING:
                assert isinstance(cell.var_type, ArrayOf)
                indexing = step.argument
                exp_eval = self.get_expression_evaluator()
                evaluated_indexing = [exp_eval.eval(expr, self) for expr in indexing]
                try:
                    cell = cell[evaluated_indexing]
                except IndexError:
                    msg = f"Accessing var {var}. Can't access array at index {indexing}."
                    raise MemoryInfrigementError(msg)
            elif step.kind == var.ACCESSED_FIELD:
                if not isinstance(cell.var_type, Tuple):
                    raise MemoryInfrigementError(
                        f"Accessing var {var}, {cell}, {cell.var_type}. Can't access field {step.argument}."
                    )
                field = step.argument
                try:
                    cell = cell.sub_cells[field]
                except KeyError:
                    msg = f"For var {var}. Can't access field {field}."
                    raise MemoryInfrigementError(msg)
            else:
                raise NotImplementedError(f"Unknown step kind {step.kind}")
        return cell

    def set_variable_value(self, var, value, permit_write_on_read_only=False):
        cell = self.cell_after_traversal(var)
        if not cell.can_get_set_values_directly:
            raise MemoryInfrigementError(f"Cell type {type(cell)} can't be modified directly.")

        if cell.read_only and not permit_write_on_read_only:
            raise MemoryInfrigementError(f"Variable {var} is read-only.")

        if not cell.var_type.is_valid_value(value):
            raise TomosTypeError(
                f"Variable {var} was declared of type {cell.var_type}, "
                f"but attempted to set value {value}({type(value)}) that's not valid for this type."
            )
        cell.value = value

    def get_variable_value(self, var):
        cell = self.cell_after_traversal(var)
        if not cell.can_get_set_values_directly:
            raise MemoryInfrigementError(f"Cell type {type(cell)} can't be accessed directly.")
        return cell.value

    def list_declared_variables(self):
        return {name: cell.var_type for name, cell in self.stack.items()}
