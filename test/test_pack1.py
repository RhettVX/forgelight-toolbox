from FLUtils import fl_pack1


def test_unpack_pack1():
    fl_pack1.unpack_pack1('sample.pack', 'Unpacked')


def test_unpack_pack2_namelist():
    fl_pack1.unpack_pack1('data_x64_0_with_namelist.pack2', 'Unpacked')


def test_unpack_pack2():
    fl_pack1.unpack_pack1('data_x64_0_without_namelist.pack2', 'Unpacked')
