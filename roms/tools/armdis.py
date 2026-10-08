#!/usr/bin/env python3
"""Disassemble code.bin (flat, base 0x100000, ARM mode). usage: armdis.py code.bin START [COUNT]"""
import struct, sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
BASE = 0x100000
def main():
    d = open(sys.argv[1], 'rb').read()
    start = int(sys.argv[2], 16); n = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    md = Cs(CS_ARCH_ARM, CS_MODE_ARM); md.skipdata = True
    for ins in md.disasm(d[start - BASE:start - BASE + n * 4], start):
        extra = ''
        if ins.mnemonic.startswith('ldr') and '[pc, #' in ins.op_str:
            off = int(ins.op_str.split('#')[-1].rstrip(']'), 0)
            a = ins.address + 8 + off
            if BASE <= a < BASE + len(d):
                v = struct.unpack_from('<I', d, a - BASE)[0]; extra = f'  ; =0x{v:08X}'
        print(f'{ins.address:08X}: {ins.mnemonic:8} {ins.op_str}{extra}')
main()
