from pydantic import ConfigDict
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing import dataclass_transform


@dataclass_transform()
def dataclass(cls):
    """
    A decorator that behaves identically to applying the Pydantic `dataclass`
    with `config=ConfigDict(arbitrary_types_allowed=True)`.
    """
    # Applying Pydantic dataclass with the specified config
    return pydantic_dataclass(config=ConfigDict(arbitrary_types_allowed=True))(cls)
