# utils.py

from typing import TypeVar
from table import Table

T = TypeVar("T", bound="Table")



def model_to_table(model_class: type[T], con=None) -> T:
    """Return the table for a model class."""
    table = model_class(con)
    table.model = model_class
    return table
