#!/usr/bin/env python3
"""GS RomFS root archives of oahu (version 7; same 28-byte entry layout as RPG2's version 5).

usage:
  gsarc.py list <archive>                     # entries (hash/type/comp/size/raw/name)
  gsarc.py catalog <romfs_dir> [patch_dir]    # every root archive; patch_dir overrides by patchList.bin
  gsarc.py unpack <archive> <outdir>          # entries as <index>_<hash>_<name>
"""
import io, os, struct, sys, zipfile, zlib

def u32(b, o): return struct.unpack_from('<I', b, o)[0]

def lz10(src):
    assert src[0] == 0x10
    n = u32(src, 0) >> 8; out = bytearray(); i = 4
    while len(out) < n:
        f = src[i]; i += 1
        for b in range(8):
            if len(out) >= n: break
            if f & (0x80 >> b):
                v = src[i] << 8 | src[i + 1]; i += 2
                c = (v >> 12) + 3; d = (v & 0xFFF) + 1
                for _ in range(c): out.append(out[-d])
            else:
                out.append(src[i]); i += 1
    return bytes(out)

def parse(data):
    ver, h, n = struct.unpack_from('<III', data, 0)
    ents = []
    for i in range(n):
        hh, typ, size, off, comp, unk, raw = struct.unpack_from('<7I', data, 12 + i * 28)
        ents.append(dict(index=i, hash=hh, type=typ, size=size, offset=off, comp=comp, unk=unk, raw=raw))
    return ver, h, ents

def unpack(data, e):
    blob = data[e['offset']:e['offset'] + e['size']]
    if e['comp'] == 1:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names = z.namelist()
            # Kahara contains empty ZIP containers (EOCD only, raw_size=0).
            if not names:
                return None, b''
            name = names[0]
            return name, z.read(name)
    if e['comp'] == 6: return None, lz10(blob)
    return None, blob

def name_only(data, e):
    """File name stored in the ZIP local header (no inflate)."""
    if e['comp'] != 1: return None
    o = e['offset']
    if data[o:o + 4] == b'PK\x05\x06': return None
    nl = struct.unpack_from('<H', data, o + 26)[0]
    return data[o + 30:o + 30 + nl].decode('ascii', 'replace')

def patch_list(patch_dir):
    p = os.path.join(patch_dir, 'patchList.bin')
    if not os.path.exists(p): return set()
    d = open(p, 'rb').read(); n = u32(d, 0)
    return {u32(d, 4 + i * 4) for i in range(n)}

def resolve(romfs, patch_dir, name):
    """Path the game opens for root file `name` (rom:/name or patch:/name)."""
    if patch_dir and int(name, 16) in patch_list(patch_dir):
        return os.path.join(patch_dir, name)
    return os.path.join(romfs, name)

def main():
    cmd = sys.argv[1]
    if cmd == 'list':
        d = open(sys.argv[2], 'rb').read(); ver, h, ents = parse(d)
        print(f'version {ver} hash {h:08X} entries {len(ents)}')
        for e in ents:
            print(f"{e['index']:4} {e['hash']:08X} t{e['type']:<3} c{e['comp']} u{e['unk']:<3} size {e['size']:8} raw {e['raw']:8} {name_only(d, e) or ''}")
    elif cmd == 'catalog':
        romfs = sys.argv[2]; pd = sys.argv[3] if len(sys.argv) > 3 else None
        for f in sorted(os.listdir(romfs)):
            p = os.path.join(romfs, f)
            if not os.path.isfile(p) or len(f) != 8: continue
            src = resolve(romfs, pd, f)
            d = open(src, 'rb').read(); ver, h, ents = parse(d)
            names = [name_only(d, e) for e in ents]
            exts = {}
            for nm, e in zip(names, ents):
                k = os.path.splitext(nm)[1] if nm else f'(c{e["comp"]} t{e["type"]})'
                exts[k] = exts.get(k, 0) + 1
            tag = 'patch' if src != p else 'rom'
            print(f'{f} {tag:5} v{ver} n={len(ents):4} size={len(d):9} ' + ' '.join(f'{k}:{v}' for k, v in sorted(exts.items())))
    elif cmd == 'unpack':
        d = open(sys.argv[2], 'rb').read(); ver, h, ents = parse(d); out = sys.argv[3]
        os.makedirs(out, exist_ok=True)
        for e in ents:
            nm, body = unpack(d, e)
            open(os.path.join(out, f"{e['index']:04}_{e['hash']:08X}_{nm or 'bin'}"), 'wb').write(body)

if __name__ == '__main__':
    main()
