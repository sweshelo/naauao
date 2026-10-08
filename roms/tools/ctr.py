#!/usr/bin/env python3
"""Minimal CIA / NCCH / ExeFS / RomFS reader for decrypted (NoCrypto) 3DS dumps.

usage:
  ctr.py info  <file.cia>                 # CIA/TMD/NCCH/ExHeader summary
  ctr.py extract <file.cia> <outdir>      # exheader.bin, exefs/*, romfs/ (code is decompressed)
  ctr.py verify <file.cia>                # TMD content hashes, NCCH ExHeader/ExeFS/RomFS hashes, IVFC levels
  ctr.py merge <base.cia> <update.cia> <outdir>
      # what the game sees with the update installed: update exheader/exefs (code.bin),
      # base RomFS with every root file listed in the update's patchList.bin taken from the update
      # (the game opens those as patch:/XXXXXXXX, the rest as rom:/XXXXXXXX; docs: roms/oahu-update.md)
"""
import os, struct, sys

def u16(b, o): return struct.unpack_from('<H', b, o)[0]
def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def u64(b, o): return struct.unpack_from('<Q', b, o)[0]
def u16be(b, o): return struct.unpack_from('>H', b, o)[0]
def u32be(b, o): return struct.unpack_from('>I', b, o)[0]
def u64be(b, o): return struct.unpack_from('>Q', b, o)[0]
def align(x, a): return (x + a - 1) // a * a

SIG = {0x10000: 0x200, 0x10001: 0x100, 0x10002: 0x3C, 0x10003: 0x200, 0x10004: 0x100, 0x10005: 0x3C}
def sig_skip(t): return align(4 + SIG[t], 0x40)

class Cia:
    def __init__(self, path):
        self.f = open(path, 'rb')
        h = self.f.read(0x20)
        self.hdr_size, _, _, self.cert_size, self.tik_size, self.tmd_size, self.meta_size, self.content_size = \
            struct.unpack_from('<IHHIIIIQ', h, 0)
        self.f.seek(0x20); self.index_bits = self.f.read(0x2000)
        cert = align(self.hdr_size, 64); tik = align(cert + self.cert_size, 64)
        tmd = align(tik + self.tik_size, 64); self.content_off = align(tmd + self.tmd_size, 64)
        self.f.seek(tik); t = self.f.read(self.tik_size)
        th = sig_skip(u32be(t, 0))
        self.tik_title_key_enc = t[th + 0x7F: th + 0x8F]
        self.f.seek(tmd); t = self.f.read(self.tmd_size)
        th = sig_skip(u32be(t, 0))
        self.title_id = u64be(t, th + 0x4C)
        self.title_version = u16be(t, th + 0x9C)
        n = u16be(t, th + 0x9E)
        rec = th + 0xC4 + 64 * 0x24
        self.contents = []
        off = self.content_off
        for i in range(n):
            r = rec + i * 0x30
            cid, idx, typ, size = u32be(t, r), u16be(t, r + 4), u16be(t, r + 6), u64be(t, r + 8)
            self.contents.append(dict(id=cid, index=idx, type=typ, size=size, offset=off, sha256=t[r + 0x10:r + 0x30].hex()))
            off += align(size, 0x40)

    def read(self, off, n):
        self.f.seek(off); return self.f.read(n)

class Ncch:
    def __init__(self, cia, base):
        self.cia, self.base = cia, base
        h = cia.read(base, 0x200)
        assert h[0x100:0x104] == b'NCCH', 'not NCCH'
        self.h = h
        self.content_size = u32(h, 0x104) * 0x200
        self.partition_id = u64(h, 0x108)
        self.maker = h[0x110:0x112].decode()
        self.version = u16(h, 0x112)
        self.program_id = u64(h, 0x118)
        self.product_code = h[0x150:0x160].rstrip(b'\0').decode()
        self.exh_size = u32(h, 0x180)
        self.flags = h[0x188:0x190]
        mu = 0x200
        self.plain = (u32(h, 0x190) * mu, u32(h, 0x194) * mu)
        self.logo = (u32(h, 0x198) * mu, u32(h, 0x19C) * mu)
        self.exefs = (u32(h, 0x1A0) * mu, u32(h, 0x1A4) * mu)
        self.romfs = (u32(h, 0x1B0) * mu, u32(h, 0x1B4) * mu)
    @property
    def nocrypto(self): return bool(self.flags[7] & 4)
    def read(self, off, n): return self.cia.read(self.base + off, n)
    def exheader(self): return self.read(0x200, 0x800)
    def exefs_files(self):
        off, size = self.exefs
        if not size: return {}
        h = self.read(off, 0x200); out = {}
        for i in range(10):
            name = h[i * 16:i * 16 + 8].rstrip(b'\0').decode()
            if not name: continue
            fo, fs = u32(h, i * 16 + 8), u32(h, i * 16 + 12)
            out[name] = (off + 0x200 + fo, fs)
        return out

def blz_decompress(data):
    # 3DS ExeFS .code backward LZ (footer: u32 bufTopAndBottom, u32 originalBottom)
    data = bytearray(data)
    top_bottom, add = u32(data, len(data) - 8), u32(data, len(data) - 4)
    bottom_len = top_bottom & 0xFFFFFF; hdr_len = top_bottom >> 24
    out = bytearray(len(data) + add); out[:len(data)] = data
    src = len(data) - hdr_len; dst = len(out); end = len(data) - bottom_len
    while src > end:
        flags = data[src - 1]; src -= 1
        for _ in range(8):
            if src <= end: break
            if flags & 0x80:
                src -= 2; v = data[src] | data[src + 1] << 8
                n = ((v >> 12) & 0xF) + 3; d = (v & 0xFFF) + 3
                for _ in range(n):
                    dst -= 1; out[dst] = out[dst + d]
            else:
                src -= 1; dst -= 1; out[dst] = data[src]
            flags <<= 1
    return bytes(out)

def romfs_list(ncch):
    """Yield (path, abs_offset_in_cia_file, size) for every file in the NCCH RomFS (IVFC level 3)."""
    off, _ = ncch.romfs
    ivfc = ncch.read(off, 0x60)
    assert ivfc[:4] == b'IVFC', ivfc[:4]
    master_size = u32(ivfc, 0x08)
    l3_size_blk = u32(ivfc, 0x4C)  # level 3 block size log2
    l3 = off + align(0x60 + master_size, 1 << l3_size_blk)
    h = ncch.read(l3, 0x28)
    dmeta_o, dmeta_s = u32(h, 0x0C), u32(h, 0x10)
    fmeta_o, fmeta_s = u32(h, 0x1C), u32(h, 0x20)
    data_o = u32(h, 0x24)
    dm = ncch.read(l3 + dmeta_o, dmeta_s); fm = ncch.read(l3 + fmeta_o, fmeta_s)
    def name(b, o, n): return b[o:o + n].decode('utf-16le')
    def walk_dir(d, prefix):
        child, f = u32(dm, d + 8), u32(dm, d + 12)
        while f != 0xFFFFFFFF:
            nl = u32(fm, f + 0x1C)
            p = prefix + name(fm, f + 0x20, nl)
            yield p, ncch.base + l3 + data_o + u64(fm, f + 8), u64(fm, f + 16)
            f = u32(fm, f + 4)
        while child != 0xFFFFFFFF:
            nl = u32(dm, child + 0x14)
            yield from walk_dir(child, prefix + name(dm, child + 0x18, nl) + '/')
            child = u32(dm, child + 4)
    yield from walk_dir(0, '')

def info(path):
    c = Cia(path)
    print(f'CIA {os.path.basename(path)}  title {c.title_id:016X}  version {c.title_version} '
          f'({c.title_version >> 10}.{(c.title_version >> 4) & 0x3F}.{c.title_version & 0xF})')
    for ct in c.contents:
        print(f'  content {ct["index"]} id {ct["id"]:08X} type {ct["type"]:04X} size 0x{ct["size"]:X}')
        n = Ncch(c, ct['offset'])
        print(f'    NCCH {n.product_code} program {n.program_id:016X} nocrypto={n.nocrypto} flags={n.flags.hex()} '
              f'exefs=0x{n.exefs[1]:X} romfs=0x{n.romfs[1]:X}')
        if n.exh_size:
            e = n.exheader()
            name = e[:8].rstrip(b'\0').decode()
            print(f'    ExHeader name {name!r}  compressed_code={bool(e[0xD] & 1)}  sd_app={bool(e[0xD] & 2)}')
            for lbl, o in (('text', 0x10), ('ro', 0x20), ('data', 0x30)):
                print(f'      {lbl} addr 0x{u32(e, o):08X} size 0x{u32(e, o + 8):X}')
            print(f'      bss 0x{u32(e, 0x3C):X}')
            deps = [u64(e, 0x40 + i * 8) for i in range(48)]
            print('      deps', ' '.join(f'{d:016X}' for d in deps if d))
        for k, (o, s) in n.exefs_files().items(): print(f'    exefs {k} 0x{s:X}')

def extract(path, outdir):
    c = Cia(path); n = Ncch(c, c.contents[0]['offset'])
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, 'exheader.bin'), 'wb').write(n.exheader())
    os.makedirs(os.path.join(outdir, 'exefs'), exist_ok=True)
    compressed = bool(n.exheader()[0xD] & 1)
    for k, (o, s) in n.exefs_files().items():
        d = c.read(n.base + o, s)
        if k == '.code' and compressed:
            d = blz_decompress(d); k = 'code.bin'
        open(os.path.join(outdir, 'exefs', k.lstrip('.') or k), 'wb').write(d)
    if n.romfs[1]:
        for p, o, s in romfs_list(n):
            fp = os.path.join(outdir, 'romfs', p); os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, 'wb').write(c.read(o, s))

def verify(path):
    import hashlib
    def sha(b): return hashlib.sha256(b).digest()
    c = Cia(path); ok = True
    def check(label, cond):
        nonlocal ok
        print(('ok   ' if cond else 'FAIL ') + label); ok &= bool(cond)
    for ct in c.contents:
        check(f'content {ct["index"]} sha256 = TMD', sha(c.read(ct['offset'], ct['size'])).hex() == ct['sha256'])
        n = Ncch(c, ct['offset']); h = n.h
        check(f'content {ct["index"]} NCCH size = TMD', n.content_size == ct['size'])
        if n.exh_size: check('  exheader hash', sha(n.exheader()[:0x400]) == h[0x160:0x180])
        if n.exefs[1]:
            check('  exefs superblock hash', sha(n.read(n.exefs[0], u32(h, 0x1A8) * 0x200)) == h[0x1C0:0x1E0])
            eh = n.read(n.exefs[0], 0x200)
            for i, (k, (o, s)) in enumerate(n.exefs_files().items()):
                check(f'  exefs {k} hash', sha(c.read(n.base + o, s)) == eh[0x200 - 0x20 * (i + 1):0x200 - 0x20 * i])
        if n.romfs[1]:
            ro = n.romfs[0]
            check('  romfs superblock hash', sha(n.read(ro, u32(h, 0x1B8) * 0x200)) == h[0x1E0:0x200])
            iv = n.read(ro, 0x60); msize = u32(iv, 8)
            lv = [(u64(iv, 0x0C + i * 0x18), u64(iv, 0x14 + i * 0x18)) for i in range(3)]
            l3 = ro + align(0x60 + msize, 0x1000)
            l1 = align(l3 + lv[2][1], 0x1000); l2 = align(l1 + lv[0][1], 0x1000)
            def level_ok(hashes, data_off, size):
                for k in range(0, size, 0x1000):
                    blk = n.read(data_off + k, min(0x1000, size - k)); blk += b'\0' * (0x1000 - len(blk))
                    if sha(blk) != hashes[k // 0x1000 * 32:k // 0x1000 * 32 + 32]: return False
                return True
            check('  ivfc master -> L1', level_ok(n.read(ro + 0x60, msize), l1, lv[0][1]))
            check('  ivfc L1 -> L2', level_ok(n.read(l1, lv[0][1]), l2, lv[1][1]))
            check('  ivfc L2 -> L3', level_ok(n.read(l2, lv[1][1]), l3, lv[2][1]))
    print('ALL OK' if ok else 'ERRORS')

def merge(base, update, outdir):
    import shutil
    extract(update, os.path.join(outdir, '_update'))
    extract(base, os.path.join(outdir, '_base'))
    up = os.path.join(outdir, '_update'); bp = os.path.join(outdir, '_base')
    pl = os.path.join(up, 'romfs', 'patchList.bin')
    d = open(pl, 'rb').read(); names = ['%08X' % u32(d, 4 + i * 4) for i in range(u32(d, 0))]
    shutil.move(os.path.join(up, 'exheader.bin'), os.path.join(outdir, 'exheader.bin'))
    shutil.move(os.path.join(up, 'exefs'), os.path.join(outdir, 'exefs'))
    shutil.move(os.path.join(bp, 'romfs'), os.path.join(outdir, 'romfs'))
    for n in names:
        shutil.copyfile(os.path.join(up, 'romfs', n), os.path.join(outdir, 'romfs', n))
    extra = sorted(set(os.listdir(os.path.join(up, 'romfs'))) - set(names) - {'patchList.bin'})
    shutil.rmtree(up); shutil.rmtree(bp)
    print('patched from update:', ' '.join(names))
    if extra: print('WARNING: update RomFS files not in patchList.bin (ignored by the game):', ' '.join(extra))

if __name__ == '__main__':
    if sys.argv[1] == 'info':
        for p in sys.argv[2:]: info(p)
    elif sys.argv[1] == 'extract':
        extract(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'verify':
        for p in sys.argv[2:]: verify(p)
    elif sys.argv[1] == 'merge':
        merge(sys.argv[2], sys.argv[3], sys.argv[4])
