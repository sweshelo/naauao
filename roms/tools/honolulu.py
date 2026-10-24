#!/usr/bin/env python3
"""honolulu (初代) の master の表とマップを読み解いて表示する (読み取り専用)。

usage:
  honolulu.py monsters  <master_dir> <2713402F_dir>      # monsterBattleParameter の展開
  honolulu.py groups    <master_dir> <2713402F_dir>      # monsterGroup / monsterFixGroup
  honolulu.py chests    <master_dir>                      # itemGroup
  honolulu.py maps      <code.bin> <A90C8038_dir>         # マップ → 区画 2 つの大きさ

<master_dir> などは gsarc.py unpack の出力先。メッセージは master の *_JP.gsmb から引く。
欄の位置は honolulu/monsters.md・map.md の表と同じ (根拠の関数はそちら)。
"""
import glob, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsmb  # noqa: E402


def u16(b, o): return struct.unpack_from('<H', b, o)[0]
def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def bits(w, lo, n): return (w >> lo) & ((1 << n) - 1)


def table(d, name):
    b = open(glob.glob(os.path.join(d, f'*_{name}.bin'))[0], 'rb').read()
    rows, rsz, off = u32(b, 0), u32(b, 4), u32(b, 0x10)
    return [b[off + i * rsz:off + (i + 1) * rsz] for i in range(rows)]


def messages(master):
    m = {}
    for p in glob.glob(os.path.join(master, '*_JP.gsmb')):
        m.update(gsmb.load(p)[1])
    return lambda i: gsmb.text(m[i]) if i in m else f'#{i}'


def battle_param(r):
    """monsterBattleParameter の 1 行 (0x34 B) を FUN_00205BE8 の読み方で展開する。"""
    w = [u32(r, 4 * k) for k in range(13)]
    return dict(
        lv=bits(w[0], 0, 7),
        hp=(bits(w[4], 8, 15), bits(w[0], 7, 15)),
        atk=(bits(w[0], 22, 10), bits(w[5], 0, 10)),
        dfn=(bits(w[1], 0, 10), bits(w[5], 10, 10)),
        spd=(bits(w[1], 10, 10), bits(w[5], 20, 10)),
        drops=[(bits(w[1], 23, 9), bits(w[1], 20, 3)), (bits(w[2], 3, 9), bits(w[2], 0, 3))],
        gold=bits(w[2], 12, 16), exp=w[3] & 0xFFFF,
        status=bits(w[3], 18, 5), target=bits(w[4], 6, 2),
        skills=[u16(r, 0x20 + 2 * k) for k in range(5) if u16(r, 0x20 + 2 * k)],
        design=r[0x2C], line=u16(r, 0x1E), direct=u16(r, 0x1C), next=r[0x33])


def cmd_monsters(master, arc):
    msg = messages(master)
    md = table(arc, 'monsterData'); it = table(master, 'itemData'); sk = table(master, 'monsterAttackSkill')
    item = lambda i: msg(u32(it[i], 0)) if 0 < i < len(it) else '-'
    print('| 行 | 名前 | Lv | HP | こうげき | ぼうぎょ | すばやさ | 経験値 | お金 | ドロップ (率) | ワザ (monsterAttackSkill) | 次の形態 |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for i, r in enumerate(table(master, 'monsterBattleParameter')[1:], 1):
        p = battle_param(r)
        rng = lambda t: f'{min(t)}〜{max(t)}' if t[0] != t[1] else str(t[0])
        name = msg(u32(md[p['design']], 0)) if p['design'] < len(md) else '?'
        drops = '<br>'.join(f'{item(a)} ({c})' for a, c in p['drops'] if a)
        skills = ' '.join(str(s) for s in p['skills'])
        print(f"| {i} | {name} | {p['lv']} | {rng(p['hp'])} | {rng(p['atk'])} | {rng(p['dfn'])} | {rng(p['spd'])} "
              f"| {p['exp']} | {p['gold']} | {drops} | {skills} | {p['next'] or ''} |")


def cmd_groups(master, arc):
    msg = messages(master)
    md = table(arc, 'monsterData'); bp = table(master, 'monsterBattleParameter')
    name = lambda i: msg(u32(md[bp[i][0x2C]], 0)) if 0 < i < len(bp) else str(i)
    for i, r in enumerate(table(master, 'monsterGroup')):
        a = [f'{name(u16(r, 4 * k))}(重み {r[4 * k + 2]}, {r[4 * k + 3]})' for k in range(5) if u16(r, 4 * k)]
        b = [f'{name(u16(r, 0x14 + 4 * k))}({r[0x16 + 4 * k]}, {r[0x17 + 4 * k]})' for k in range(5) if u16(r, 0x14 + 4 * k)]
        print(i, 'A:', ', '.join(a), '| B:', ', '.join(b), '| 型の重み', list(r[0x28:0x2D]), '+0x2D', r[0x2D])
    for i, r in enumerate(table(master, 'monsterFixGroup')):
        print('fix', i, [name(u16(r, 4 * k)) for k in range(5) if u16(r, 4 * k)], '+0x14', r[0x14])


def cmd_chests(master):
    msg = messages(master); it = table(master, 'itemData')
    for i, r in enumerate(table(master, 'itemGroup')):
        e = [(u16(r, 4 + 4 * k), u16(r, 6 + 4 * k)) for k in range(8)]
        print(i, hex(u32(r, 0)), ', '.join(f'{msg(u32(it[a], 0))}×{c}' for a, c in e if a))


def cmd_maps(code, mapdir):
    d = open(code, 'rb').read()
    b = open(glob.glob(os.path.join(mapdir, '*_A2C14C00_*'))[0], 'rb').read()
    n = u32(b, 0); db = {u32(b, 4 + 12 * i): u32(b, 12 + 12 * i) for i in range(n)}
    s = 0x2FF6D8 - 0x100000
    for k in range(0x62):
        a, c = u32(d, s + 8 * k), u32(d, s + 8 * k + 4)
        print(f'{k:2} {a:08X} {db.get(a, "?"):>5} B  {c:08X} {db.get(c, "?"):>5} B')


if __name__ == '__main__':
    cmd, *args = sys.argv[1:] or ['-h']
    f = {'monsters': cmd_monsters, 'groups': cmd_groups, 'chests': cmd_chests, 'maps': cmd_maps}.get(cmd)
    if not f:
        print(__doc__); sys.exit(1)
    f(*args)
