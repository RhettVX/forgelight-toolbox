from FLUtils.fl_index import compare_dumps
from pathlib import Path


def test_compare_dumps():
    compare_dumps(Path('index_live.txt').resolve(), Path('index_test.txt').resolve())
