#!/usr/bin/env python3
"""GMSG (.gsmb) reader. usage: gsmb.py <file.gsmb> [ID ...]   (no IDs = header + first 20)"""
import struct, sys

def load(path):
    d = open(path, 'rb').read()
    magic = d[:4]; size, first, last, kind, step, tbl, base = struct.unpack_from('<7I', d, 4)
    n = 0 if last == 0xFFFFFFFF else (last - first) // step + 1
    msgs = {}
    for i in range(n):
        o = base + struct.unpack_from('<I', d, tbl + i * 4)[0]
        e = o
        while e + 1 < len(d) and d[e:e + 2] != b'\0\0': e += 2
        msgs[first + i * step] = d[o:e]
    return dict(magic=magic, size=size, first=first, last=last, kind=kind, step=step), msgs

def text(raw):
    """Body as text: drops the kind code, shows tags as {tag:X} and inserts as {msg:ID}."""
    u = list(struct.unpack('<%dH' % (len(raw) // 2), raw))
    out = []; i = 1
    while i < len(u):
        c = u[i]
        if c == 1 and i + 1 < len(u): out.append('{tag:%X}' % u[i + 1]); i += 2; continue
        if c == 2 and i + 2 < len(u): out.append('{msg:%X}' % u[i + 2]); i += 4; continue
        if c == 0xA: out.append('\\n')
        elif c < 0x20: out.append('{%02X}' % c)
        else: out.append(chr(c))
        i += 1
    return ''.join(out)

if __name__ == '__main__':
    h, m = load(sys.argv[1])
    ids = [int(x, 0) for x in sys.argv[2:]]
    if not ids:
        print(h, len(m)); ids = list(m)[:20]
    for i in ids:
        print(f'0x{i:04X}', text(m.get(i, b'')))
