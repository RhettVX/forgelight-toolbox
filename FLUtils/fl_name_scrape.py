from re import search, compile, IGNORECASE
from argparse import ArgumentParser
from os import makedirs
from pathlib import Path
from struct import unpack
from typing import List, Dict
from zlib import decompress

from DbgPack import AssetManager
from DbgPack.hash import crc64


known_exts = ('adr agr ags apb apx bat bin cdt cnk0 cnk1 cnk2 cnk3 cnk4 cnk5 crc crt cso cur dat db dds def dir dll '
              'dma dme dmv dsk dx11efb dx11rsb dx11ssb eco efb exe fsb fxd fxo gfx gnf i64 ini jpg lst lua mrn pak '
              'pem playerstudio png prsb psd pssb tga thm tome ttf txt vnfo wav xlsx xml xrsb xssb zone').split()


# TODO: Replace this with the improved version from zone-parse
def read_cstring(data: bytes) -> bytes:
    chars = []
    for c in data:
        if c == 0x0:
            return bytes(chars)
        chars.append(c)


def scrape_packs(paths: List[Path], limit_files=True) -> Dict[int, str]:
    """
    :param paths: List of paths to pack files to scrape
    :param limit_files: Limit scraping to known file formats
    :return: List of scraped names
    """
    names = {}
    file_pattern = compile(bytes(r'([><\w-]+\.(' + r'|'.join(known_exts) + r'))', 'utf-8'))

    for path in paths:
        print(f'Scraping {path.name}...')
        am = AssetManager([path])
        for a in am:
            data = a.get_data()
            # If no name, check file header. If no match, skip this file
            if a.data_length > 0 and limit_files:
                if data[:1] == b'#':  # flatfile
                    pass
                elif data[:14] == b'<ActorRuntime>':  # adr
                    mo = search(b'<Base fileName="([\\w-]+)_LOD0\\.dme"', data, IGNORECASE)
                    if mo:
                        name = mo[1] + b'.adr'
                        names[crc64(name)] = name.decode('utf-8')
                elif data[:10] == b'<ActorSet>':  # agr
                    pass
                elif data[:5] == b'<?xml':  # xml
                    pass
                elif data[:12] == b'*TEXTUREPART':  # eco
                    pass
                elif data[:4] == b'DMAT':  # dma
                    pass
                elif data[:4] == b'DMOD':  # dme
                    pass
                elif data[:4] == b'FSB5':  # fsb
                    header_size = unpack('<I', data[12:16])[0]
                    pos = 64 + header_size
                    name = read_cstring(data[pos:]) + b'.fsb'

                    names[crc64(name)] = name.decode('utf-8')
                    continue
                elif data[:3] == b'CFX':  # gfx
                    data = decompress(data[8:])

                else:
                    continue

            found_names = []

            mo = file_pattern.findall(data)
            if mo:
                for m in mo:
                    if b'<gender>' in m[0]:
                        found_names.append(m[0].replace(b'<gender>', b'Male'))
                        found_names.append(m[0].replace(b'<gender>', b'Female'))
                    elif b'.efb' in m[0]:
                        found_names.append(m[0])
                        found_names.append(m[0].replace(b'.efb', b'.dx11efb'))  # .fxo might also be usable as dx11efb
                    elif b'<' in m[0] or b'>' in m[0]:
                        found_names.append(m[0].replace(b'>', b''))

                    else:
                        found_names.append(m[0])

                for n in found_names:
                    names[crc64(n)] = n.decode('utf-8')

    print('Done!')
    return names


def merge_namelists(path1: Path, path2: Path) -> List[str]:
    """
    :param path1:
    :param path2:
    """

    print(f'Merging "{path1}" and "{path2}"')

    nameset1 = set(path1.read_text().strip().split('\n'))
    nameset2 = set(path2.read_text().strip().split('\n'))
    out_set = list(nameset1.union(nameset2))

    return sorted(out_set)


def write_names(names: Dict[int, str], path: Path, out_dir: Path = Path('.')) -> None:
    """
    :param names:
    :param path:
    :param out_dir:
    """

    makedirs(out_dir, exist_ok=True)
    with path.open('w') as out_file:
        out_file.writelines([x + '\n' for x in sorted(names.values())])


if __name__ == '__main__':
    parser = ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='command')
    sub_parsers.required = True

    sub_scrape = sub_parsers.add_parser('scrape')
    sub_scrape.add_argument('dir', help='Directory containing pack2s')
    sub_scrape.add_argument('-o', '--output', default='scraped.txt',
                            help='File to dump scraped names')

    sub_merge = sub_parsers.add_parser('merge')
    sub_merge.add_argument('file1')
    sub_merge.add_argument('file2')
    sub_merge.add_argument('-o', '--output', default='merged.txt',
                           help='File to dump merged namelists')

    args = parser.parse_args()
    if args.command == 'scrape':
        dir_path = Path(args.dir)

        data_names = scrape_packs([dir_path / 'data_x64_0.pack2'], limit_files=False)
        all_names = scrape_packs(list(dir_path.glob('*.pack2')))
        write_names({**all_names, **data_names}, Path(args.output))

    elif args.command == 'merge':
        file1_path = Path(args.file1)
        file2_path = Path(args.file2)

        merged_names = merge_namelists(file1_path, file2_path)
        Path(args.output).write_text('\n'.join(merged_names))
