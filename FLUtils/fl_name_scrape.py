from pathlib import Path
from typing import List

from DbgPack import AssetManager

# Here is a rough draft of how this is gonna work
# load data.pack2
# Scan every file in the data.pack2
# output new names
# backup current namelist
# then update it with the new names


known_exts = ('DDS TTF TXT adr agr ags apb apx bat bin cdt cnk0 cnk1 cnk2 cnk3 cnk4 cnk5 crc crt cso cur dat db dds'
              'def dir dll dma dme dmv dsk dx11efb dx11rsb dx11ssb eco exe fsb fxd fxo gfx gnf i64 ini jpg lst lua mrn'
              'pak pem playerstudio png prsb psd pssb tga thm tome ttf txt vnfo wav xlsx xml xrsb xssb zone').split()


def scrape_pack(path: Path) -> List[str]:
    names = []

    am = AssetManager([str(path)])
    for a in am:
        print(a.name)


if __name__ == '__main__':
    scrape_pack(
        Path(r'C:\Users\Rhett\Desktop\forgelight-toolbox\Backups\07-15-19-TEST\Resources\Assets\data_x64_0.pack2'))
