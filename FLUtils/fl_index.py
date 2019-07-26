import os
from argparse import ArgumentParser
from binascii import crc32
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Tuple

from DbgPack import AssetManager
from DbgPack.hash import crc64


# TODO: Load in old indices with the newest namelist
# TODO: Pack everything into the index class
# TODO: Handle identical file names properly


@dataclass()
class IndexEntry:
    name: str = field(default='')
    name_hash: str = field(default=None)
    crc32_: Optional[int] = field(default=None)
    path: Path = field(default=None)
    subpath: Optional[Path] = field(default_factory=Path)

    def __post_init__(self):
        assert self.name or self.name_hash, 'name or name_hash is required'
        assert self.path, 'these arguments are required'

        if self.name == 'NONE':
            self.name = ''

        if not self.name_hash and self.name:
            self.name_hash = crc64(self.name)

        # If subpath is a file, then we are probably in a pack
        if not self.crc32_ and self.name and self.path and (self.path / self.subpath).is_dir():
            fullpath = self.path / self.subpath / self.name

            if fullpath.stat().st_size > 0:
                self.crc32_ = crc32(fullpath.read_bytes())
            else:
                self.crc32_ = 0


@dataclass
class Index:
    entries: Dict[int, IndexEntry] = field(default_factory=dict)

    def add(self, item):
        self.entries[item.name_hash] = item

    def __iter__(self):
        return iter(self.entries.values())

    def __getitem__(self, item):
        return self.entries[item]


def compare_dumps(path_old: Path, path_new: Path, out_dir: Path) -> None:
    """
    Compare to index dumps and create a difference report

    :param path_old: Path to older index dump
    :param path_new: Path to newer index dump
    :param out_dir: Name of folder to output report to
    :return: None
    """

    print('Creating diff report...')

    os.makedirs(out_dir, exist_ok=True)

    # Load indices
    index_old = Index()
    for line in [l.strip() for l in path_old.read_text().split('\n')]:
        if line:
            index_old.add(IndexEntry(*line.split(';')))

    index_new = Index()
    for line in [l.strip() for l in path_new.read_text().split('\n')]:
        if line:
            index_new.add(IndexEntry(*line.split(';')))

    # Identify file changes
    files_new = sorted([index_new[x] for x in index_new.entries.keys() if x not in index_old.entries.keys()],
                       key=lambda x: x.name)
    files_del = sorted([index_old[x] for x in index_old.entries.keys() if x not in index_new.entries.keys()],
                       key=lambda x: x.name)
    files_mod = sorted([index_new[x] for x in index_new.entries.keys()
                       if x in index_old.entries.keys() and index_new[x].crc32_ != index_old[x].crc32_],
                       key=lambda x: x.name)

    with open(out_dir / f'diff-{path_old.stem}-{path_new.stem}.txt', 'w') as out_file:
        out_file.write(f'Diff report:\n"{path_old}"\nand\n"{path_new}"')

        out_file.write(f'\n\n\n{"###[ ADDED ]":#<80}')
        out_file.writelines([f'\n+ "{x.name if x.name else "NONE"}" : {int(x.name_hash):#018x} : "{x.subpath}"'
                             for x in files_new])

        out_file.write(f'\n\n\n{"###[ DELETED ]":#<80}')
        out_file.writelines([f'\n- "{x.name if x.name else "NONE"}" : {int(x.name_hash):#018x} : "{x.subpath}"'
                             for x in files_del])

        out_file.write(f'\n\n\n{"###[ CHANGED ]":#<80}')
        out_file.writelines([f'\n! "{x.name if x.name else "NONE"}" : {int(x.name_hash):#018x} : "{x.subpath}"'
                             for x in files_mod])

    print('Done!')


def load_files(path: Path, namelist: Optional[Path] = None) -> Index:
    """

    :param path: Path of root dir to index
    :param namelist: Path to external namelist
    :return: Index
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


# fl_index -n namelist --index[ -n root [root..]] --diff file1 file2
if __name__ == '__main__':
    parser = ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='command')

    parser.add_argument('-n', '--namelist', help='path to external namelist')

    subcmd_index = sub_parsers.add_parser('index')
    subcmd_index.add_argument('root', nargs='+', help='path of root directory to dump index of')

    subcmd_diff = sub_parsers.add_parser('diff')
    subcmd_diff.add_argument('index1', help='Path to older index')
    subcmd_diff.add_argument('index2', help='Path to newer index')

    args = parser.parse_args()
    if args.command == 'index':
        for path_ in args.root:
            file_path = Path(path_)
            dump_index(load_files(file_path, Path(args.namelist)), file_path.name + '.txt', 'Game Indices')

    elif args.command == 'diff':
        compare_dumps(Path(args.index1), Path(args.index2), Path('Diff Reports'))
