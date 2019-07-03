from FLUtils import fl_pack


def test_unpack_pack1():
    fl_pack.unpack_pack('sample.pack', 'Unpacked')


def test_unpack_pack2_namelist():
    fl_pack.unpack_pack('data_x64_0_with_namelist.pack2', 'Unpacked')


def test_unpack_pack2():
    fl_pack.unpack_pack('data_x64_0_without_namelist.pack2', 'Unpacked', 'namelist.txt')
