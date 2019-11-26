from dataclasses import dataclass, field
from typing import Dict

from .indexable import Indexable


@dataclass()
class IndexableManager:  # Should use a separate manager for each game version
    indexables: Dict[int, Indexable] = field(default_factory=dict)

    def add(self, item: Indexable):
        self.indexables[item.unique_id] = item

    def __iter__(self):
        return iter(self.indexables.values())

    def __getitem__(self, item: int):
        return self.indexables[item]

    def __len__(self):
        return len(self.indexables)
