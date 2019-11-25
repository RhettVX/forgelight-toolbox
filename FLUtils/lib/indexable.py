from dataclasses import dataclass, field
from typing import Dict

from .indexable_type_enum import IndexableType


# TODO: maybe we could access meta_info with Indexable[key]

@dataclass()
class Indexable:
    unique_id: int  # Will probably just use a hash for this. It needs to cover the name+path of files
    comparable: int  # This will probably just be a hash of the content I wanna track
    category: IndexableType = field(default=IndexableType.GENERAL, init=False)  # This is correct, right?
    meta_info: Dict[str, str]  # Any extra info will go here. I might make Name a variable rather than a tag here

    # This should compare the comparable, which should be a hash of the content I'm trying to track
    def __eq__(self, other):
        if not isinstance(other, Indexable):
            return NotImplemented
        return self.comparable == other.comparable and self.unique_id == other.unique_id
