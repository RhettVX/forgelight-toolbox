from argparse import ArgumentParser
from binascii import crc32
from collections import namedtuple
from os import makedirs, walk
from pathlib import Path
from typing import List

import dataclasses

from DbgPack import AssetManager

# TODO: Add method for comparison
# TODO: Use dataclasses for storing indices

Entry = namedtuple('Entry', 'name name_hash crc32 path')


def compare_dumps(path_old: str, path_new: str) -> None:
    """
    Compare to index dumps and create a difference report

    :param path_old: Path to older index dump
    :param path_new:  Path to newer index dump
    :return: None
    """

    # Load old index
    with open(path_old, 'r') as file_old:
        index_old = [Entry(*l.strip().split(';')) for l in file_old]

    # Load new index
    with open(path_new, 'r') as file_new:
        index_new = [Entry(*l.strip().split(';')) for l in file_new]


def load_files(path: str, namelist: str = None) -> List[Entry]:
    """

    :param path: Path of root dir to index
    :param namelist: Path to external namelist
    :return:
    """

    packs = []
    entries = []
    namelist_ = []

    if namelist:
        with open(namelist, 'r') as in_file:
            namelist_ = [line.strip() for line in in_file]

    print('Indexing files...')
    for root, _, files in walk(path):
        for file in files:
            file_path = Path(root, file)

            if file_path.suffix in ('.pack', '.pack2'):
                packs.append(file_path)
            else:
                with open(file_path, 'rb') as in_file:
                    checksum = crc32(in_file.read())

                entries.append(Entry(file_path.name, 'None', checksum, file_path))

    if packs:
        print('Indexing packs...')
        am = AssetManager(packs, namelist=namelist_)
        for a in am:
            entries.append(Entry(a.name if a.name else 'None', a.name_hash, a.crc32, a.path))

    print('Done\n')
    return entries


def dump_index(index: List[Entry], name: str, dir_: str) -> None:
    """

    :param index: List of index entries to dump
    :param name: Name of file to dump index to
    :param dir_: Directory to store index dump in
    :return: None
    """

    print('Dumping index...')
    makedirs(dir_, exist_ok=True)
    file_path = Path(dir_, name)
    with open(file_path, 'w') as out_file:
        for entry in index:
            out_file.write(f'{entry.name};{entry.name_hash};{entry.crc32};{entry.path}\n')

    print('Done\n')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-n', '--namelist', help='path to external namelist')
    parser.add_argument('dir', nargs='+', help='path of root directory to dump index of')

    args = parser.parse_args()

    for path_ in args.dir:
        arg_path = Path(path_)
        dump_index(load_files(arg_path, args.namelist), arg_path.name+'.txt', 'Game Indices')