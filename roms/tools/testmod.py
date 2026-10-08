#!/usr/bin/env python3
"""A tiny visible MOD for checking the CIA recipes (oahu/update.md): renames item 1 (message 0x4B2
"キズぐすり") in the master archive 21350000.

usage: testmod.py <update.cia> <outdir> [new name]
  -> <outdir>/21350000 (built from the update's master; use as --romfs <outdir> for ctrbuild.py)
"""
import io, os, struct, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ctr, gsarc  # noqa: E402

MSG_ID = 0x4B2


def gsmb_set(data, msg_id, text):
    size, first, last, kind, step, tbl, base = struct.unpack_from('<7I', data, 4)
    n = (last - first) // step + 1
    msgs = []
    for i in range(n):
        o = base + struct.unpack_from('<I', data, tbl + i * 4)[0]
        e = o
        while data[e:e + 2] != b'\0\0': e += 2
        msgs.append(data[o:e])
    i = (msg_id - first) // step
    msgs[i] = msgs[i][:2] + text.encode('utf-16le')  # keep the kind code
    body = bytearray(); offs = []
    for m in msgs:
        offs.append(len(body)); body += m + b'\0\0'
    out = bytearray(data[:base]) + body
    for k, o in enumerate(offs): struct.pack_into('<I', out, tbl + k * 4, o)
    struct.pack_into('<I', out, 4, len(out))
    return bytes(out)


def rebuild(arc, replace):
    """replace: {entry index: (name, body)} — entries are ZIP (comp 1)."""
    ver, h, ents = gsarc.parse(arc)
    hdr = bytearray(arc[:12 + 28 * len(ents)]); body = bytearray(); pos = len(hdr)
    for e in ents:
        if e['index'] in replace:
            name, data = replace[e['index']]
            z = io.BytesIO()
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf: zf.writestr(name, data)
            blob = z.getvalue(); raw = len(data)
        else:
            blob = arc[e['offset']:e['offset'] + e['size']]; raw = e['raw']
        struct.pack_into('<7I', hdr, 12 + e['index'] * 28, e['hash'], e['type'], len(blob), pos, e['comp'], e['unk'], raw)
        body += blob; pos += len(blob)
    return bytes(hdr + body)


def main():
    u = ctr.Cia(sys.argv[1]); un = ctr.Ncch(u, u.contents[0]['offset'])
    name = sys.argv[3] if len(sys.argv) > 3 else 'ＭＯＤぐすり'
    master = next(u.read(o, s) for p, o, s in ctr.romfs_list(un) if p == '21350000')
    _, _, ents = gsarc.parse(master)
    e = next(e for e in ents if gsarc.name_only(master, e) == 'MessageSystemCommon_JP.gsmb')
    nm, body = gsarc.unpack(master, e)
    out = rebuild(master, {e['index']: (nm, gsmb_set(body, MSG_ID, name))})
    os.makedirs(sys.argv[2], exist_ok=True)
    open(os.path.join(sys.argv[2], '21350000'), 'wb').write(out)


if __name__ == '__main__':
    main()
