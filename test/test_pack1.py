from FLUtils import fl_pack1


def test_unpack_pack1():
    fl_pack1.unpack_pack1('sample.pack', 'Unpacked')
    fl_pack1.unpack_pack1('data_x64_0_with_namelist.pack2', 'Unpacked')
    fl_pack1.unpack_pack1('data_x64_0_without_namelist.pack2', 'Unpacked')
