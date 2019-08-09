from argparse import ArgumentParser
from os import makedirs
from os.path import splitext, basename, join
from pathlib import Path

from DbgPack import AssetManager, Asset2


# TODO: Method to pack a dir into a .pack


def unpack_pack(am: AssetManager, dir_: Path) -> None:
    """
    Unpacks a '.pack|.pack2' file used by the Forgelight Engine

    :param am: Asset manager to unpack from
    :param dir_: Path to directory to unpack files to
    :return: None
    """

    for pack in am.packs:
        print(f'Unpacking {pack.path}...')

        makedirs(dir_ / pack.name, exist_ok=True)
        for asset in pack.assets.values():

            if isinstance(asset, Asset2):
                name = asset.name if asset.name else f'{asset.name_hash:#018x}.bin'
            else:
                name = asset.name

            (dir_ / pack.name / name).write_bytes(asset.data)

    print('Done\n')


if __name__ == '__main__':
    parser = ArgumentParser(description='Unpacks a \'.pack|.pack2\' file used by the Forgelight Engine')
    sub_parsers = parser.add_subparsers(dest='command')
    sub_parsers.required = True

    subcmd_unpack = sub_parsers.add_parser('unpack')
    subcmd_unpack.add_argument('path', nargs='+', help='pack files or directory to unpack')
    subcmd_unpack.add_argument('-n', '--namelist', help='path to external namelist')
    subcmd_unpack.add_argument('-o', '--outdir', default='Unpacked',
                               help='directory to dump assets')

    # Handle the args
    args = parser.parse_args()
    if args.command == 'unpack':
        namelist_ = []
        namelist_path = Path(args.namelist) if args.namelist else None

        if namelist_path:
            namelist_ = namelist_path.read_text().strip().split('\n')

        pack_files = []
        for path in [Path(p) for p in args.path]:
            if path.is_file():
                pack_files.append(path)
            else:
                pack_files.extend(path.glob('*.pack*'))

        print('Loading packs...')
        am_ = AssetManager(pack_files, namelist_)
        unpack_pack(am_, Path(args.outdir))
