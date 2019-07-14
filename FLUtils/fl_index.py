import os
from argparse import ArgumentParser
from binascii import crc32
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from DbgPack import AssetManager
from DbgPack.hash import crc64


# TODO: Pack everything into the index class


@dataclass
class IndexEntry:
    name: str = field(default='')
    name_hash: str = field(default=None)
    crc32_: Optional[int] = field(default=None)
    path: Path = field(default=None)
    subpath: Optional[Path] = field(default_factory=Path)

    def __post_init__(self):
        assert self.name or self.name_hash, 'name or name_hash is required'
        assert self.path, 'these arguments are required'

        if not self.name_hash and self.name:
            self.name_hash = crc64(self.name)

        # If subpath is a file, then we are probably in a pack
        # TODO: and empty files will have a crc32 of 0, so we don't want to regenerate that
        if not self.crc32_ and self.name and self.path and (self.path / self.subpath).is_dir():
            self.crc32_ = crc32((self.path / self.subpath / self.name).read_bytes())


@dataclass
class Index:
    entries: Dict[int, IndexEntry] = field(default_factory=dict)

    def add(self, item):
        self.entries[hash((item.name_hash, item.subpath))] = item

    def __iter__(self):
        return iter(self.entries.values())


# TODO: Restore functionality to this function
def compare_dumps(path_old, path_new: str) -> None:
    """
    Compare to index dumps and create a difference report

    :param path_old: Path to older index dump
    :param path_new:  Path to newer index dump
    :return: None
    """
    pass


def load_files(path: Path, namelist: Optional[Path] = None) -> Index:
    """

    :param path: Path of root dir to index
    :param namelist: Path to external namelist
    :return: Set[IndexEntry]
    """
    index = Index()
    packs: List[Tuple] = []
    namelist_ = []

    if namelist:
        print('Loading namelist')
        namelist_ = [line.strip() for line in namelist.read_text().split('\n')]

    print(f'Indexing {path}...')
    path_len = len(str(path))
    for root, _, files in os.walk(path):
        for file in files:
            subpath = Path(root[path_len:].lstrip(os.sep))
            fullpath = path / subpath / file

            if fullpath.suffix in ('.pack', '.pack2'):
                packs.append((path, subpath, file))

            else:
                e = IndexEntry(name=file, path=path, subpath=subpath)
                index.add(e)

    for i in index:
        print(i)

    if packs:
        print('Indexing packs...')

        am = AssetManager([str(Path(*p)) for p in packs], namelist=namelist_)
        for a in am:
            e = IndexEntry(name=a.name, name_hash=a.name_hash, crc32_=a.crc32,
                           path=Path(a.path[:path_len]), subpath=Path(a.path[path_len:]))
            index.add(e)

    print('Done\n')
    return index


def dump_index(index: Index, name: str, dir_: str) -> None:
    """

    :param index: List of index entries to dump
    :param name: Name of file to dump index to
    :param dir_: Directory to store index dump in
    :return: None
    """

    print('Dumping index...')
    os.makedirs(dir_, exist_ok=True)
    file_path = Path(dir_, name)
    with file_path.open('w') as out_file:
        for entry in index:
            out_file.write(
                f'{entry.name if entry.name else "NONE"};{entry.name_hash};{entry.crc32_};{entry.path};{entry.subpath}\n')

    print('Done\n')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-n', '--namelist', help='path to external namelist')
    parser.add_argument('dir', nargs='+', help='path of root directory to dump index of')

    args = parser.parse_args()

    for path_ in args.dir:
        file_path = Path(path_)
        dump_index(load_files(file_path, Path(args.namelist)), file_path.name + '.txt', 'Game Indices')
