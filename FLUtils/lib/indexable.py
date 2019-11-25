from dataclasses import dataclass
from typing import Dict


# TODO: maybe we could access meta_info with Indexable[key]

@dataclass()
class Indexable:
    unique_id: int
    comparable: int
    meta_info: Dict

    def __eq__(self, other):
        if not isinstance(other, Indexable):
            return NotImplemented
        return self.comparable == other.comparable
