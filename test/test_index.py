from FLUtils.fl_index import compare_dumps
from pathlib import Path


def test_compare_dumps():
    compare_dumps(Path('old_index.txt').resolve(), Path('new_index.txt').resolve())
