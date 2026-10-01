#!/usr/bin/env python3
"""Build 3DS RomFS / ExeFS / NCCH / CIA (NoCrypto) from a dumped CIA as template. See oahu/update.md.

usage:
  ctrbuild.py romfs <dir> <out.romfs>
      # RomFS (IVFC + level 3) from a folder
  ctrbuild.py applied <base.cia> <update.cia> <out.cia> [--romfs DIR] [--code code.bin]
      # one CIA with the update applied: title 00040000000EF000, update ExHeader/ExeFS,
      # base RomFS with the update's patchList files (DIR overrides/adds root files on top)
  ctrbuild.py update <update.cia> <out.cia> --version N [--romfs DIR] [--code code.bin]
      # a new update title (0004000E...) = the official update + DIR's root files
      # (patchList.bin is rewritten to list every root archive in the result)

Signatures (NCCH header, TMD, ticket) are copied from the template and are NOT valid: the CIA
installs on custom firmware with signature patches (Luma3DS + FBI) and on Azahar.
"""
import hashlib, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ctr  # noqa: E402

MU = 0x200
BLOCK = 0x1000


def align(x, a): return (x + a - 1) // a * a
def pad(b, a): return b + b'\0' * (align(len(b), a) - len(b))
def sha(b): return hashlib.sha256(b).digest()


# ---------------------------------------------------------------- RomFS
def _bucket_count(n):
    if n < 3: return 3
    if n < 19: return n | 1
    c = n
    while any(c % p == 0 for p in (2, 3, 5, 7, 11, 13, 17)): c += 1
    return c


def _name_hash(parent, name):
    h = parent ^ 123456789
    for ch in (ord(c) for c in name):
        h = ((h >> 5) | (h << 27)) & 0xFFFFFFFF
        h ^= ch
    return h


class _Dir:
    def __init__(self, name, parent):
        self.name, self.parent, self.dirs, self.files, self.off = name, parent, [], [], 0


def _walk(root):
    """files: {relpath: bytes-or-path}. Returns the dir tree (children sorted like Nintendo's tools: by name)."""
    top = _Dir('', None)
    dirs = {'': top}
    for rel in sorted(root):
        parts = rel.split('/')
        cur = ''
        for p in parts[:-1]:
            nxt = cur + '/' + p if cur else p
            if nxt not in dirs:
                d = _Dir(p, dirs[cur]); dirs[cur].dirs.append(d); dirs[nxt] = d
            cur = nxt
        dirs[cur].files.append((parts[-1], root[rel]))
    return top


def build_level3(files):
    """files: {relative path: bytes}. Returns RomFS level 3 bytes."""
    top = _walk(files)
    # breadth-first order of directories, files in directory order
    order = [top]
    i = 0
    while i < len(order):
        order.extend(order[i].dirs); i += 1
    # directory metadata offsets
    off = 0
    for d in order:
        d.off = off
        off += 0x18 + align(len(d.name) * 2, 4)
    dmeta_size = off
    flist = []
    off = 0
    for d in order:
        for name, data in d.files:
            flist.append([d, name, data, off]); off += 0x20 + align(len(name) * 2, 4)
    fmeta_size = off
    dcount, fcount = _bucket_count(len(order)), _bucket_count(len(flist))
    dhash = [0xFFFFFFFF] * dcount
    fhash = [0xFFFFFFFF] * fcount
    dnext, fnext = {}, {}
    for d in order:
        b = _name_hash(d.parent.off if d.parent else 0, d.name) % dcount
        dnext[d.off] = dhash[b]; dhash[b] = d.off
    for f in flist:
        b = _name_hash(f[0].off, f[1]) % fcount
        fnext[f[3]] = fhash[b]; fhash[b] = f[3]
    # file data
    data = bytearray(); doff = {}
    for f in flist:
        data += b'\0' * (align(len(data), 0x10) - len(data))
        doff[f[3]] = len(data); data += f[2]
    first_file = {}
    for f in flist: first_file.setdefault(id(f[0]), f[3])
    dm = bytearray()
    for d in order:
        sib = 0xFFFFFFFF
        if d.parent:
            sibs = d.parent.dirs; k = sibs.index(d)
            if k + 1 < len(sibs): sib = sibs[k + 1].off
        child = d.dirs[0].off if d.dirs else 0xFFFFFFFF
        nm = d.name.encode('utf-16le')
        dm += struct.pack('<6I', d.parent.off if d.parent else 0, sib, child,
                          first_file.get(id(d), 0xFFFFFFFF), dnext[d.off], len(nm)) + pad(nm, 4)
    fm = bytearray()
    for idx, f in enumerate(flist):
        d = f[0]
        sib = flist[idx + 1][3] if idx + 1 < len(flist) and flist[idx + 1][0] is d else 0xFFFFFFFF
        nm = f[1].encode('utf-16le')
        fm += struct.pack('<IIQQII', d.off, sib, doff[f[3]], len(f[2]), fnext[f[3]], len(nm)) + pad(nm, 4)
    hdr_size = 0x28
    dh_off = hdr_size; dh = struct.pack('<%dI' % dcount, *dhash)
    dm_off = dh_off + len(dh)
    fh_off = dm_off + dmeta_size; fh = struct.pack('<%dI' % fcount, *fhash)
    fm_off = fh_off + len(fh)
    data_off = align(fm_off + fmeta_size, 0x10)
    hdr = struct.pack('<10I', hdr_size, dh_off, len(dh), dm_off, dmeta_size, fh_off, len(fh), fm_off, fmeta_size, data_off)
    out = bytearray(hdr) + dh + dm + fh + fm
    out += b'\0' * (data_off - len(out))
    out += data
    return bytes(out)


def _hash_level(data):
    out = bytearray()
    for i in range(0, max(len(data), 1), BLOCK):
        out += sha(pad(data[i:i + BLOCK], BLOCK))
    return bytes(out)


def build_romfs(level3):
    """IVFC-wrapped RomFS; returns (romfs bytes, hash region size in bytes)."""
    l2 = _hash_level(level3)
    l1 = _hash_level(l2)
    master = _hash_level(l1)
    l1_log = 0
    l2_log = align(l1_log + len(l1), BLOCK)
    l3_log = align(l2_log + len(l2), BLOCK)
    hdr = struct.pack('<4sII', b'IVFC', 0x10000, len(master))
    for lo, ln in ((l1_log, len(l1)), (l2_log, len(l2)), (l3_log, len(level3))):
        hdr += struct.pack('<QQII', lo, ln, 12, 0)
    hdr += struct.pack('<III', 0x5C, 0, 0)  # header 0x5C, padded to 0x60; master hash follows
    out = bytearray(hdr) + master
    out += b'\0' * (align(len(out), BLOCK) - len(out))
    out += level3
    out += b'\0' * (align(len(out), BLOCK) - len(out))
    out += l1
    out += b'\0' * (align(len(out), BLOCK) - len(out))
    out += l2
    out = pad(bytes(out), BLOCK)
    return out, align(0x60 + len(master), MU)


def read_dir(root):
    files = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(dp, f)
            files[os.path.relpath(p, root).replace(os.sep, '/')] = open(p, 'rb').read()
    return files


def romfs_files(cia, ncch):
    return {p: cia.read(o, s) for p, o, s in ctr.romfs_list(ncch)}


# ---------------------------------------------------------------- ExeFS / NCCH
def build_exefs(files):
    """files: list of (name, bytes) in order."""
    hdr = bytearray(0x200); body = bytearray()
    for i, (name, data) in enumerate(files):
        struct.pack_into('<8sII', hdr, i * 16, name.encode(), len(body), len(data))
        struct.pack_into('32s', hdr, 0x200 - 0x20 * (i + 1), sha(data))
        body += pad(data, MU)
    return bytes(hdr) + bytes(body)


def exefs_entries(cia, ncch):
    return [(k, cia.read(ncch.base + o, s)) for k, (o, s) in ncch.exefs_files().items()]


def build_ncch(template, exheader, exefs, romfs, romfs_hash_size, program_id=None):
    """template: Ncch of the source content (header, logo, plain region are copied)."""
    h = bytearray(template.h)
    plain = template.read(template.plain[0], template.plain[1]) if template.plain[1] else b''
    logo = template.read(template.logo[0], template.logo[1]) if template.logo[1] else b''
    out = bytearray(0x200) + pad(exheader, MU)
    def place(blob, a=MU):
        nonlocal out
        out += b'\0' * (align(len(out), a) - len(out))
        o = len(out); out += blob; return o
    lo = place(logo) if logo else 0
    po = place(plain) if plain else 0
    eo = place(exefs)
    ro = place(romfs, BLOCK) if romfs else 0
    out = pad(bytes(out), MU); out = bytearray(out)
    struct.pack_into('<I', h, 0x104, len(out) // MU)
    if program_id is not None:
        struct.pack_into('<Q', h, 0x108, program_id); struct.pack_into('<Q', h, 0x118, program_id)
    h[0x160:0x180] = sha(exheader[:0x400])
    struct.pack_into('<II', h, 0x190, po // MU, len(plain) // MU if plain else 0)
    struct.pack_into('<II', h, 0x198, lo // MU, len(logo) // MU if logo else 0)
    if logo: h[0x130:0x150] = sha(logo)
    struct.pack_into('<III', h, 0x1A0, eo // MU, len(exefs) // MU, 1)
    struct.pack_into('<III', h, 0x1B0, ro // MU, len(romfs) // MU if romfs else 0, romfs_hash_size // MU if romfs else 0)
    h[0x1C0:0x1E0] = sha(exefs[:MU])
    h[0x1E0:0x200] = sha(romfs[:romfs_hash_size]) if romfs else b'\0' * 32
    out[:0x200] = h
    return bytes(out)


# ---------------------------------------------------------------- CIA
def build_cia(template, contents, title_id=None, version=None):
    """template: ctr.Cia; contents: list of bytes (replaces template contents in order, same count)."""
    f = template.f
    def raw(off, n): f.seek(off); return f.read(n)
    cert_off = align(template.hdr_size, 64)
    tik_off = align(cert_off + template.cert_size, 64)
    tmd_off = align(tik_off + template.tik_size, 64)
    cert = raw(cert_off, template.cert_size)
    tik = bytearray(raw(tik_off, template.tik_size))
    tmd = bytearray(raw(tmd_off, template.tmd_size))
    end = template.contents[-1]['offset'] + align(template.contents[-1]['size'], 64)
    meta = raw(end, template.meta_size) if template.meta_size else b''
    th = ctr.sig_skip(struct.unpack_from('>I', tmd, 0)[0])
    kh = ctr.sig_skip(struct.unpack_from('>I', tik, 0)[0])
    if title_id is not None:
        struct.pack_into('>Q', tmd, th + 0x4C, title_id); struct.pack_into('>Q', tik, kh + 0x9C, title_id)
    if version is not None:
        struct.pack_into('>H', tmd, th + 0x9C, version); struct.pack_into('>H', tik, kh + 0xA6, version)
    n = struct.unpack_from('>H', tmd, th + 0x9E)[0]
    assert n == len(contents)
    rec = th + 0xC4 + 64 * 0x24
    for i, c in enumerate(contents):
        r = rec + i * 0x30
        struct.pack_into('>Q', tmd, r + 8, len(c)); tmd[r + 0x10:r + 0x30] = sha(c)
    # content info record 0 covers all chunk records
    tmd[th + 0xC4 + 4:th + 0xC4 + 0x24] = sha(bytes(tmd[rec:rec + 0x30 * n]))
    tmd[th + 0xA4:th + 0xC4] = sha(bytes(tmd[th + 0xC4:th + 0xC4 + 64 * 0x24]))
    body = bytearray()
    for c in contents: body += pad(c, 64)
    hdr = bytearray(raw(0, template.hdr_size))
    struct.pack_into('<Q', hdr, 0x18, len(body))
    out = bytearray(hdr)
    for blob in (cert, bytes(tik), bytes(tmd)):
        out += b'\0' * (align(len(out), 64) - len(out)); out += blob
    out += b'\0' * (align(len(out), 64) - len(out))
    out += body
    out += meta
    return bytes(out)


# ---------------------------------------------------------------- recipes
def _patch_list(names):
    hs = sorted(int(n, 16) for n in names)
    return struct.pack('<I', len(hs)) + b''.join(struct.pack('<I', h) for h in hs)


def _is_root_archive(p): return '/' not in p and len(p) == 8


def _code_exefs(exefs, exheader, code_path):
    """Replace .code with an uncompressed code.bin and clear the ExHeader's compressed flag."""
    if not code_path: return exefs, exheader
    code = open(code_path, 'rb').read()
    exh = bytearray(exheader); exh[0xD] &= ~1
    return [(k, code if k == '.code' else v) for k, v in exefs], bytes(exh)


def applied(base_path, update_path, out_path, overlay=None, code=None):
    b, u = ctr.Cia(base_path), ctr.Cia(update_path)
    bn, un = ctr.Ncch(b, b.contents[0]['offset']), ctr.Ncch(u, u.contents[0]['offset'])
    files = romfs_files(b, bn)
    ufiles = romfs_files(u, un)
    pl = ufiles['patchList.bin']
    for i in range(struct.unpack_from('<I', pl, 0)[0]):
        n = '%08X' % struct.unpack_from('<I', pl, 4 + i * 4)[0]
        files[n] = ufiles[n]
    if overlay: files.update(read_dir(overlay))
    exheader = bytearray(un.exheader())
    struct.pack_into('<Q', exheader, 0x1C8, bn.program_id)  # jump id: the base title
    # update ExeFS (.code / icon / logo) + the base's banner (the update has none)
    ue = dict(exefs_entries(u, un)); be = exefs_entries(b, bn)
    exefs = [(k, ue.get(k, v)) for k, v in be]
    exefs, exheader = _code_exefs(exefs, bytes(exheader), code)
    romfs, hs = build_romfs(build_level3(files))
    ncch = build_ncch(bn, exheader, build_exefs(exefs), romfs, hs)
    manual = b.read(b.contents[1]['offset'], b.contents[1]['size'])
    open(out_path, 'wb').write(build_cia(b, [ncch, manual], version=u.title_version))


def update(update_path, out_path, version, overlay=None, code=None):
    u = ctr.Cia(update_path); un = ctr.Ncch(u, u.contents[0]['offset'])
    files = romfs_files(u, un)
    if overlay: files.update(read_dir(overlay))
    files['patchList.bin'] = _patch_list([p for p in files if _is_root_archive(p)])
    exheader = bytearray(un.exheader())
    struct.pack_into('<H', exheader, 0xE, version >> 10)  # remaster version follows the major version
    exefs, exheader = _code_exefs(exefs_entries(u, un), bytes(exheader), code)
    romfs, hs = build_romfs(build_level3(files))
    ncch = build_ncch(un, exheader, build_exefs(exefs), romfs, hs)
    manual = u.read(u.contents[1]['offset'], u.contents[1]['size'])
    open(out_path, 'wb').write(build_cia(u, [ncch, manual], version=version))


def _opt(name):
    if name in sys.argv:
        i = sys.argv.index(name); v = sys.argv[i + 1]; del sys.argv[i:i + 2]; return v
    return None


if __name__ == '__main__':
    overlay, code, ver = _opt('--romfs'), _opt('--code'), _opt('--version')
    cmd = sys.argv[1]
    if cmd == 'romfs':
        r, _ = build_romfs(build_level3(read_dir(sys.argv[2]))); open(sys.argv[3], 'wb').write(r)
    elif cmd == 'applied':
        applied(sys.argv[2], sys.argv[3], sys.argv[4], overlay, code)
    elif cmd == 'update':
        update(sys.argv[2], sys.argv[3], int(ver, 0), overlay, code)
