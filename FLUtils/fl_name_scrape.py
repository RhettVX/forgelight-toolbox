import re
from pathlib import Path
from typing import List, Set, Dict
from os import makedirs

from DbgPack import AssetManager
from DbgPack.hash import crc64

# Here is a rough draft of how this is gonna work
# load data.pack2
# Scan every file in the data.pack2
# output new names
# backup current namelist
# then update it with the new names


known_exts = ('DDS TTF TXT adr agr ags apb apx bat bin cdt cnk0 cnk1 cnk2 cnk3 cnk4 cnk5 crc crt cso cur dat db dds'
              'def dir dll dma dme dmv dsk dx11efb dx11rsb dx11ssb eco exe fsb fxd fxo gfx gnf i64 ini jpg lst lua mrn'
              'pak pem playerstudio png prsb psd pssb tga thm tome ttf txt vnfo wav xlsx xml xrsb xssb zone').split()


def scrape_pack(path: Path) -> Dict[int, str]:
    """

    :param path: Path to pack file to scrape
    :return: List of scraped names
    """

    names = {}
    file_pattern = re.compile(bytes(r'([><\w,-]+\.(' + r'|'.join(known_exts) + r'))', 'utf-8'))

    print(f'Scraping {path.name}...')
    am = AssetManager([str(path)])
    for a in am:
        found_names = []

        mo = file_pattern.findall(a.data)
        if mo:
            for m in mo:
                if b'<gender>' in m[0]:
                    found_names.append(m[0].replace(b'<gender>', b'Male'))
                    found_names.append(m[0].replace(b'<gender>', b'Female'))
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
        out_file.writelines([x+'\n' for x in names.values()])


if __name__ == '__main__':
    x = scrape_pack(
        Path(r'C:\Users\Rhett\Desktop\forgelight-toolbox\Backups\07-15-19-TEST\Resources\Assets\data_x64_0.pack2'))
    write_names(x, Path('scraped.txt'))
    pass
