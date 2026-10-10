#!/usr/bin/env python3
"""GS table (lanai / RPG Free, header 0x40) reader.

usage:
  gstable.py info  <file> [...]          # name / rows / row size / named fields
  gstable.py dump  <file> [maxrows]      # rows as u32 words; relocated fields as text
  gstable.py text  <file> <offset>       # one message (tag-aware) at a file offset

Only the lanai layout is handled (kahara / oahu tables use the older header).
Messages: UTF-16LE, tag = 0x0001, code, nargs, args (type 2 = u32, type 3 = u16 len +
ASCII padded to u16). Ruby is 0x38 base 0x39 reading 0x3A (each with nargs 0).
"""
import struct, sys


def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def u16(b, o): return struct.unpack_from('<H', b, o)[0]


def cstr(b, o):
    return b[o:b.index(b'\0', o)].decode('ascii', 'replace')


def parse(d):
    if len(d) < 0x40:
        return None
    (rows, rsz, pool, pool_size, data, data_size, ids, ids_size, schema, schema_size,
     reloc, reloc_n, extra, name_off, name_end, _) = struct.unpack_from('<16I', d, 0)
    if pool != 0x40 or rows * rsz != data_size or data > len(d) or reloc > len(d):
        return None
    try:
        name = cstr(d, pool + name_off)
    except ValueError:
        return None
    return dict(
        name=name, rows=rows, rsz=rsz, data=data, extra=extra,
        ids=[u32(d, ids + 4 * i) for i in range(ids_size // 4)] if ids else [],
        fields=[(cstr(d, u32(d, schema + 8 * i)), u32(d, schema + 8 * i + 4))
                for i in range(schema_size // 8)],
        relocs=[u32(d, reloc + 4 * i) for i in range(reloc_n)])


def message(d, o):
    out = []
    while o + 1 < len(d):
        c = u16(d, o)
        if c == 0:
            break
        if c == 1:
            code, n = u16(d, o + 2), u16(d, o + 4); o += 6; args = []
            for _ in range(n):
                ty = u16(d, o); o += 2
                if ty == 2:
                    args.append('0x%X' % u32(d, o)); o += 4
                elif ty == 3:
                    ln = u16(d, o); o += 2
                    args.append(d[o:o + 2 * ln].split(b'\0')[0].decode('ascii', 'replace')); o += 2 * ln
                else:
                    args.append('?%d' % ty); break
            if n == 0 and code in (0x38, 0x39, 0x3A):
                out.append('{|}'[code - 0x38])
            elif code == 0x37:
                out.append('[%s]' % ':'.join(args))
            else:
                out.append('<%X %s>' % (code, ','.join(args)))
            continue
        out.append('\\n' if c == 0xA else ('{U%04X}' % c if c < 0x20 or 0xD800 <= c < 0xF900 else chr(c)))
        o += 2
    return ''.join(out)


def dump(path, maxrows=None):
    d = open(path, 'rb').read(); t = parse(d)
    if not t:
        print(path, ': not a lanai GS table'); return
    names = {off: n for n, off in t['fields']}; rel = set(t['relocs'])
    print(f"## {t['name']} rows={t['rows']} rsz=0x{t['rsz']:X} fields={t['fields']}")
    for r in range(t['rows'] if maxrows is None else min(maxrows, t['rows'])):
        base = t['data'] + r * t['rsz']; parts = []
        for o in range(0, t['rsz'] - 3, 4):
            v = u32(d, base + o)
            parts.append(f'{names.get(o, "+%X" % o)}="{message(d, v)}"' if base + o in rel else f'{v:08X}')
        if t['rsz'] % 4:
            parts.append(d[base + t['rsz'] - t['rsz'] % 4:base + t['rsz']].hex())
        rid = f" id={t['ids'][r]:08X}" if r < len(t['ids']) else ''
        print(f'{r:5}{rid} ' + ' '.join(parts))


def main():
    cmd = sys.argv[1]
    if cmd == 'info':
        for p in sys.argv[2:]:
            t = parse(open(p, 'rb').read())
            print(p, 'not a table' if not t else
                  f"{t['name']} rows={t['rows']} rsz=0x{t['rsz']:X} fields={t['fields']} relocs={len(t['relocs'])}")
    elif cmd == 'dump':
        dump(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else None)
    elif cmd == 'text':
        print(message(open(sys.argv[2], 'rb').read(), int(sys.argv[3], 0)))


if __name__ == '__main__':
    main()
