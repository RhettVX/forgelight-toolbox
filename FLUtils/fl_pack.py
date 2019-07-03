from argparse import ArgumentParser
from os import makedirs
from os.path import splitext, basename, join, isdir

from DbgPack import AssetManager


# TODO: Method to pack a dir into a .pack


def unpack_pack(path: str, dir_: str, namelist: str = None) -> None:
    """Unpacks a '.pack|.pack2' file used by the Forgelight Engine

    :param path: Path to '.pack|.pack2' or  file
    :param dir_: Path to directory to unpack files to
    :param namelist: Path to filename list
    :return: None
    """

    namelist_ = []

    if namelist:
        with open(namelist, 'r') as in_file:
            namelist_ = [line.strip() for line in in_file]

    am = AssetManager([path], namelist=namelist_)
    print(f'Unpacking "{basename(path)}"...')

    for asset in am:
        pack_name = splitext(basename(asset.path))[0]

        makedirs(join(dir_, pack_name), exist_ok=True)

        name = asset.name if asset.name else f'{asset.name_hash:#018x}.bin'
        with open(join(dir_, pack_name, name), 'wb') as out_file:
            out_file.write(asset.data)

    print('Done\n')


if __name__ == '__main__':
    parser = ArgumentParser(description='Unpacks a \'.pack|.pack2\' file used by the Forgelight Engine')
    parser.add_argument('-p1', '--pack1', action='store_true', help='use pack1 (.pack) format')
    parser.add_argument('-n', '--namelist', help='path to external namelist')
    parser.add_argument('file', nargs='+', help='files or folders to unpack or pack')

    args = parser.parse_args()

    for path_ in args.file:
        if isdir(path_):
            # TODO: Pack directory
            raise NotImplementedError
        else:
            unpack_pack(path_, 'Unpacked', args.namelist)
