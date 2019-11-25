from dataclasses import dataclass, field
from typing import Dict

from .indexable import Indexable


@dataclass()
class IndexableManager:
    indexables: Dict[int, Indexable] = field(default_factory=dict)

    def add(self, item: Indexable):
        self.indexables[item.unique_id] = item

    def __iter__(self):
        return iter(self.indexables.values())

    def __getitem__(self, item: int):
        return self.indexables[item]
