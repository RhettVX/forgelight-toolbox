from sys import argv, stderr
from os import makedirs
from os.path import splitext, basename, join, isdir

from DbgPack import AssetManager


# TODO: Method to pack a dir into a .pack


def unpack_pack1(path: str, dir_: str) -> None:
    """Unpacks a '.pack' file used by the Forgelight Engine

    :param path: Path to '.pack' file
    :param dir_: Path to directory to unpack files to
    :return: None
    """

    # TODO: Add namelist support
    # with open('namelist.txt', 'r') as in_file:
    #     namelist = [line.strip() for line in in_file]

    am = AssetManager([path])
    print(f'Unpacking "{basename(path)}"...')

    for asset in am:
        pack_name = splitext(basename(asset.path))[0]

        makedirs(join(dir_, pack_name), exist_ok=True)

        name = asset.name if asset.name else f'{asset.name_hash:016x}.bin'
        with open(join(dir_, pack_name, name), 'wb') as out_file:
            out_file.write(asset.data)

    print('Done\n')


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
            unpack_pack1(arg, 'Unpacked')
