from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class IndexableType(Enum):
    GENERAL = 0
    FILE = 1
    ASSET = 2
    STRING = 3
    ITEM = 4
    VEHICLE = 5
    TINT = 6


@dataclass()
class Indexable:
    unique_id: int  # Will probably just use a hash for this. It needs to cover the name+path of files
    comparable: int  # This will probably just be a hash of the content I wanna track
    category: IndexableType = field(default=IndexableType.GENERAL)
    meta_info: Dict[str, str] = field(default_factory=dict)  # Any extra info will go here. I might make Name a
    # variable rather than a tag here

    # This should compare the comparable, which should be a hash of the content I'm trying to track
    def __eq__(self, other):
        if not isinstance(other, Indexable):
            return NotImplemented
        return self.comparable == other.comparable and self.unique_id == other.unique_id

    # This is just s shortcut for accessing meta info
    def __getitem__(self, item: str):
        return self.meta_info[item]
