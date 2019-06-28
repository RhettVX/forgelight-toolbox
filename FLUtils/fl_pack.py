from sys import argv, stderr
from os import makedirs
from os.path import splitext, basename, join, isdir

from DbgPack import AssetManager


# TODO: Method to pack a dir into a .pack


def unpack_pack(path: str, dir_: str) -> None:
    """Unpacks a '.pack|.pack2' file used by the Forgelight Engine

    :param path: Path to '.pack|.pack2' or  file
    :param dir_: Path to directory to unpack files to
    :return: None
    """

    # FIXME: Make this optional. Don't push until fixed
    with open('namelist.txt', 'r') as in_file:
        namelist = [line.strip() for line in in_file]

    # namelist = None  # FIXME

    am = AssetManager([path], namelist=namelist)
    print(f'Unpacking "{basename(path)}"...')

    for asset in am:
        pack_name = splitext(basename(asset.path))[0]

        makedirs(join(dir_, pack_name), exist_ok=True)

        name = asset.name if asset.name else f'{asset.name_hash:016x}.bin'
        with open(join(dir_, pack_name, name), 'wb') as out_file:
            out_file.write(asset.data)

    print('Done\n')


def pack_dir(path: str) -> None:
    pass

# USAGE: python fl_pack.py [-f --format pack|pack2(Default)] file [files...]
# Pack when a folder is passed
# Unpack when a pack|pack2 file is passed
# Default to pack2 packing
if __name__ == '__main__':
    argc = len(argv)

    if argc < 2:
        print('Missing arguments', file=stderr)
        exit(1)

    for arg in argv[1:]:
        if isdir(arg):
            # TODO: Pack dir
            pass

        else:  # arg is a file
            print(arg)
            unpack_pack(arg, 'Unpacked')
