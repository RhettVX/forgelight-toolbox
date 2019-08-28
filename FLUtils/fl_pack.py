from argparse import ArgumentParser
from os import makedirs
from pathlib import Path

from DbgPack import AssetManager, Asset2


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

            (dir_ / pack.name / name).write_bytes(asset.get_data())

    print('Done\n')


def pack_pack2(am: AssetManager, name: str,  dir_: Path) -> None:
    """

    :param am: Asset manager to pack from
    :param name: Name of file to pack to
    :param dir_: Path to dump packed files
    """

    print(f'Packing to {name} as Pack2...')
    makedirs(dir_, exist_ok=True)
    am.export_pack2(name, dir_)
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

    # Add option to pack raw
    subcmd_pack = sub_parsers.add_parser('pack')
    subcmd_pack.add_argument('path', nargs='+', help='pack files or folders to repack')
    subcmd_pack.add_argument('-n', '--name', default='assets_x64_0.pack2',
                             help='pack file name')
    subcmd_pack.add_argument('-o', '--outdir', default='Packed',
                             help='directory to save repacked file')

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

    elif args.command == 'pack':
        print('Loading packs...')
        am_ = AssetManager([Path(p) for p in args.path])
        pack_pack2(am_, args.name, Path(args.outdir))
