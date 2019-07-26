import operator
import re
from pathlib import Path
from typing import List, Set, Dict
from os import makedirs
from os.path import splitext
from zlib import decompress
from struct import unpack

from DbgPack import AssetManager
from DbgPack.hash import crc64

# Here is a rough draft of how this is gonna work
# load data.pack2
# Scan every file in the data.pack2
# output new names
# backup current namelist
# then update it with the new names


known_exts = ('DDS TTF TXT adr agr ags apb apx bat bin cdt cnk0 cnk1 cnk2 cnk3 cnk4 cnk5 crc crt cso cur dat db dds '
              'def dir dll dma dme dmv dsk dx11efb dx11rsb dx11ssb eco efb exe fsb fxd fxo gfx gnf i64 ini jpg lst lua mrn '
              'pak pem playerstudio png prsb psd pssb tga thm tome ttf txt vnfo wav xlsx xml xrsb xssb zone').split()


def read_cstring(data: bytes) -> bytes:
    chars = []
    for c in data:
        # print(c)
        if c == 0x0:
            return bytes(chars)
        chars.append(c)


def scrape_packs(paths: List[Path], namelist: List[str] = None, limit_files=True) -> Dict[int, str]:
    """

    :param paths: List of paths to pack files to scrape
    :return: List of scraped names
    """

    names = {}
    file_pattern = re.compile(bytes(r'([><\w-]+\.(' + r'|'.join(known_exts) + r'))', 'utf-8'))

    log_path = Path('log-out.txt')

    # with log_path.open('a') as log_file:

    for path in paths:
        print(f'Scraping {path.name}...')
        am = AssetManager([str(path)], namelist=namelist)
        for a in am:

            # log_file.write(f'\n### Searching in "{a.name}" : {a.name_hash:#018}...\n')

            data = a.data
            # If no name, check file header. If no match, skip this file
            if a.length > 0 and limit_files:
                if data[:1] == b'#':  # flatfile
                    print('In a flatfile')
                elif data[:14] == b'<ActorRuntime>':  # adr
                    print('In adr')
                    mo = re.search(b'<Base fileName="([\\w-]+)_LOD0\\.dme"', data, re.IGNORECASE)
                    if mo:
                        name = mo[1]+b'.adr'
                        names[crc64(name)] = name.decode('utf-8')
                elif data[:10] == b'<ActorSet>':  # agr
                    print('in agr')
                elif data[:5] == b'<?xml':  # xml
                    print('in xml')
                elif data[:12] == b'*TEXTUREPART':  # eco
                    print('in eco')
                elif data[:4] == b'DMAT':  # dma
                    print('In dma')
                elif data[:4] == b'DMOD':  # dme
                    print('in dme')
                elif data[:4] == b'FSB5':  # fsb
                    print('in fsb')
                    header_size = unpack('<I', data[12:16])[0]
                    pos = 64+header_size
                    name = read_cstring(data[pos:])+b'.fsb'

                    names[crc64(name)] = name.decode('utf-8')
                    continue
                elif data[:3] == b'CFX':  # gfx
                    print('in gfx')
                    data = decompress(data[8:])

                else:
                    continue

            found_names = []

            mo = file_pattern.findall(data)
            if mo:
                for m in mo:
                    # log_file.write('- "' + m[0].decode('utf-8') + '"\n')
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


# TODO
def merge_namelists(path1: Path, path2: Path) -> List[str]:
    """

    :param path1:
    :param path2:
    """
    pass


def write_names(names: Dict[int, str], path: Path, out_dir: Path = Path('.')) -> None:
    """

    :param names:
    :param path:
    :param out_dir:
    """

    makedirs(out_dir, exist_ok=True)
    with path.open('w') as out_file:
        out_file.writelines([x+'\n' for x in sorted(names.values())])


if __name__ == '__main__':
    root = Path(r'C:\Users\Rhett\Desktop\forgelight-toolbox\Backups\07-25-19-LIVE\Resources\Assets')
    data_names = scrape_packs([root / 'data_x64_0.pack2'], limit_files=False)
    # write_names(data_names, Path('scraped.txt'))
    all_names = scrape_packs(list(root.glob('*.pack2')))
    write_names({**all_names, **data_names}, Path('scraped-more.txt'))

    print(len(data_names))
    print(len(all_names))

    pass
