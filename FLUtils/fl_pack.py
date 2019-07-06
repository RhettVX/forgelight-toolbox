from argparse import ArgumentParser
from os import makedirs
from os.path import splitext, basename, join, isdir

from DbgPack import AssetManager


# TODO: Method to pack a dir into a .pack


def unpack_pack(am: AssetManager, dir_: str) -> None:
    """
    Unpacks a '.pack|.pack2' file used by the Forgelight Engine

    :param am: Asset manager to unpack from
    :param dir_: Path to directory to unpack files to
    :return: None
    """

    for pack in am.packs:
        print(f'Unpacking {pack.path}...')
        pack_name = splitext(basename(pack.path))[0]

        makedirs(join(dir_, pack_name), exist_ok=True)

        for asset in pack.assets.values():
            name = asset.name if asset.name else f'{asset.name_hash:#018x}.bin'
            with open(join(dir_, pack_name, name), 'wb') as out_file:
                out_file.write(asset.data)

    print('Done\n')


if __name__ == '__main__':
    parser = ArgumentParser(description='Unpacks a \'.pack|.pack2\' file used by the Forgelight Engine')

    # Optional args
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('-u', '--unpack', action='store_true',
                      help='unpack provided files')
    mode.add_argument('-p', '--pack', action='store_true',
                      help='pack the provided files')

    parser.add_argument('-p1', '--pack1', action='store_true',
                        help='use pack1 (.pack) format for packing. default: pack2 (.pack2)')
    parser.add_argument('-n', '--namelist',
                        help='path to external namelist')

    # Positional args
    parser.add_argument('file', nargs='+',
                        help='files or folders to unpack or pack')

    # Handle the args
    args = parser.parse_args()
    if args.pack:
        # TODO: Add packing method
        raise NotImplementedError
    else:  # Unpack packs
        namelist_ = []

        if args.namelist:
            with open(args.namelist, 'r') as in_file:
                namelist_ = [line.strip() for line in in_file]

        am_ = AssetManager(args.file, namelist_)
        unpack_pack(am_, 'Unpacked')
