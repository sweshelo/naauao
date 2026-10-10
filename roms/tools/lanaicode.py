#!/usr/bin/env python3
"""lanai (RPG Free) 16-character code: decode / encode.

Reimplements the decoder at FUN_001B53D4 (Update TitleVersion 17408 code.bin).
See lanai/codes.md for the field layout and how the game uses each field.

usage:
  lanaicode.py dec <code> [...]
  lanaicode.py enc <kind> <payload> [extra] [major.minor.micro]
"""
import hashlib, struct, sys

# CampaignCharacter (archive 7BF7000A): row index = 5-bit value
ALPHABET = 'C341PV0BTXLJYKM8FDHRQ7GNAEW6U592'
M32 = 0xFFFFFFFF


def bitrev(x, n): return int(f'{x:0{n}b}'[::-1], 2)
def mix32(x): return (bitrev((x * 0x43BD527F) & M32, 32) * 0x950C6D7F) & M32
def mix16(x): return (bitrev((x * 0x9FA5) & 0xFFFF, 16) * 0x302D) & 0xFFFF
def unmix32(x): return (bitrev((x * pow(0x950C6D7F, -1, 1 << 32)) & M32, 32) * pow(0x43BD527F, -1, 1 << 32)) & M32
def unmix16(x): return (bitrev((x * pow(0x302D, -1, 1 << 16)) & 0xFFFF, 16) * pow(0x9FA5, -1, 1 << 16)) & 0xFFFF
def rd(b, o): return struct.unpack_from('<I', b, o)[0]
def wr(b, o, v): struct.pack_into('<I', b, o, v)


def to_bytes(code):
    v = 0
    for ch in code.upper():
        v = v << 5 | ALPHABET.index(ch)
    return bytearray(v.to_bytes(10, 'big'))


def to_code(b):
    v = int.from_bytes(b, 'big')
    return ''.join(ALPHABET[v >> 5 * (15 - i) & 31] for i in range(16))


def descramble(b):  # order used by the game
    wr(b, 6, mix32(rd(b, 6))); wr(b, 0, mix32(rd(b, 0))); wr(b, 4, mix32(rd(b, 4)))
    struct.pack_into('<H', b, 8, mix16(struct.unpack_from('<H', b, 8)[0]))
    return b


def scramble(b):
    struct.pack_into('<H', b, 8, unmix16(struct.unpack_from('<H', b, 8)[0]))
    wr(b, 4, unmix32(rd(b, 4))); wr(b, 0, unmix32(rd(b, 0))); wr(b, 6, unmix32(rd(b, 6)))
    return b


def decode(code):
    if len(code) != 16:
        raise ValueError('code must be 16 characters')
    b = descramble(to_bytes(code)); w0 = rd(b, 0)
    return dict(bytes=b.hex(),
                checksum_ok=hashlib.sha256(bytes(b[5:10])).digest()[0] == b[3],
                kind=b[4] & 3,
                version=(b[4] >> 2, w0 & 0x3FF, (w0 >> 10) & 0x3FFF),
                payload=rd(b, 5), extra=b[9])


def encode(kind, payload, extra=0, version=(0, 0, 0)):
    major, minor, micro = version
    b = bytearray(10)
    wr(b, 5, payload); b[9] = extra; b[4] = major << 2 | kind
    wr(b, 0, micro << 10 | minor)
    b[3] = hashlib.sha256(bytes(b[5:10])).digest()[0]
    return to_code(scramble(b))


if __name__ == '__main__':
    if sys.argv[1] == 'dec':
        for c in sys.argv[2:]:
            print(c, decode(c))
    else:
        a = sys.argv[2:]
        ver = tuple(int(x) for x in a[3].split('.')) if len(a) > 3 else (0, 0, 0)
        c = encode(int(a[0], 0), int(a[1], 0), int(a[2], 0) if len(a) > 2 else 0, ver)
        print(c, decode(c))
