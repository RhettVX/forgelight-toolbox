from FLUtils.fl_index import compare_dumps


def test_compare_dumps():
    compare_dumps('old_index_dump.txt', 'new_index_dump.txt')
