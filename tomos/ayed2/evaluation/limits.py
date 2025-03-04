from copy import deepcopy
from pathlib import Path

from buttons_and_dials import ConfigSet

from tomos.exceptions import (
    ArraySizeLimitExceededError,
    ArrayDimensionsLimitExceededError,
    TupleSizeLimitExceededError,
    ExecutionStepsLimitExceededError,
    MemoryLimitExceededError,
    TypeCompositionLimitExceededError,
)


here = Path(__file__).parent.resolve()
limits_configs = ConfigSet(
    "AYED_LIMITS", here / "limits.toml", check_cwd=False, argv_prefix="--cfg"
)


class Limiter:
    # This class works as a singleton, and injects checks on several places.
    # Given the singleton architecture, it shall not have state of any kind and instead
    # rely on the status of monitored objets

    def __init__(self, data):
        self._limits = deepcopy(data)

    def check_type_sizing_limits(self, _type, depth=1, crumbs=[]):
        # Checks that the type is not too complex. Returns None if the type is ok,
        # otherwise raises an exception.
        if _type in crumbs:
            # avoid clashing in recursive types
            return

        crumbs = crumbs[:] + [_type]

        # check depth
        lim_depth = self._limits.TYPE_COMPOSITION_DEPTH_LIMIT
        if lim_depth is not None and depth > lim_depth:
            raise TypeCompositionLimitExceededError()

        from tomos.ayed2.ast.types import ArrayOf, PointerOf, Synonym, Tuple  # cyclic import

        # if synonym, traverse untill we reach the actual type
        if isinstance(_type, Synonym):
            _type = _type.underlying_type_closure()

        if isinstance(_type, PointerOf):
            # depth not increased
            return self.check_type_sizing_limits(_type.of, depth=depth, crumbs=crumbs)

        if isinstance(_type, ArrayOf):
            lim_adim = self._limits.MAXIMUM_ARRAY_DIMENSIONS
            lim_asize = self._limits.MAXIMUM_ARRAY_SIZE

            if lim_adim is not None and len(_type.axes) > lim_adim:
                raise ArrayDimensionsLimitExceededError()
            if lim_asize is not None and _type.number_of_elements() > lim_asize:
                raise ArraySizeLimitExceededError()
            self.check_type_sizing_limits(_type.of, depth + 1)

        if isinstance(_type, Tuple):
            lim_tsize = self._limits.MAXIMUM_TUPLE_SIZE
            if lim_tsize is not None and len(_type.fields_mapping) > lim_tsize:
                raise TupleSizeLimitExceededError()
            for t in _type.fields_mapping.values():
                self.check_type_sizing_limits(t, depth + 1, crumbs=crumbs)

    def check_memory_size_limits(self, state_object):
        # checks that the memory size is not exceeded both in stack and heap
        lim_stack = self._limits.MAXIMUM_STACK_CELLS
        lim_heap = self._limits.MAXIMUM_HEAP_CELLS
        if lim_stack is not None:
            count = sum(cell.cell_count for cell in state_object.stack.values())
            if count > lim_stack:
                raise MemoryLimitExceededError()

        if lim_heap is not None:
            count = sum(cell.cell_count for cell in state_object.heap.values())
            if count > lim_heap:
                raise MemoryLimitExceededError()
        pass

    def check_execution_counter_limits(self, interpreter):
        lim_steps = self._limits.EXECUTION_STEPS_LIMIT
        if lim_steps is not None and interpreter.execution_counter > lim_steps:
            raise ExecutionStepsLimitExceededError()


LIMITER = Limiter(limits_configs)
