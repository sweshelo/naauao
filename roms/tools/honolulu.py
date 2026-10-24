#!/usr/bin/env python3
"""honolulu (初代) の master の表とマップを読み解いて表示する (読み取り専用)。

usage:
  honolulu.py monsters  <master_dir> <2713402F_dir>      # monsterBattleParameter の展開
  honolulu.py groups    <master_dir> <2713402F_dir>      # monsterGroup / monsterFixGroup
  honolulu.py chests    <master_dir>                      # itemGroup
  honolulu.py maps      <code.bin> <A90C8038_dir>         # マップ → 区画 2 つの大きさ
  honolulu.py floors    <master_dir> <A90C8038_dir> [エントリ番号]  # ダンジョンの階の定義 ("261")

<master_dir> などは gsarc.py unpack の出力先。メッセージは master の *_JP.gsmb から引く。
欄の位置は honolulu/monsters.md・map.md の表と同じ (根拠の関数はそちら)。
"261" の記録の読み方は FUN_0025E0EC / FUN_002A66DC と同じ (map.md §4)。
"""
import glob, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gsmb  # noqa: E402


def u16(b, o): return struct.unpack_from('<H', b, o)[0]
def u32(b, o): return struct.unpack_from('<I', b, o)[0]
def bits(w, lo, n): return (w >> lo) & ((1 << n) - 1)


def s16(b, o): return struct.unpack_from('<h', b, o)[0]


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


# "261" の記録: 0x64 の頭 + 9 つの配列 (u32 件数 + 要素)。要素の大きさは FUN_0025E0EC の読み飛ばしと同じ
FLOOR_ARRAYS = [('出口', 20), ('人物', 12), ('特別な宝箱', 12), ('宝箱', 12), ('配列4', 12),
                ('配列5', 6), ('別の部屋', 8), ('群れ', 12), ('配列8', 4)]


def parse_floors(b):
    """"261" ファイルを [(頭 0x64 B, [配列ごとの要素の bytes の list] × 9)] にする。"""
    if b[:4] != b'261\0':
        raise ValueError('not a "261" file')
    o, recs = 8, []
    for _ in range(u32(b, 4)):
        head, arrs = b[o:o + 0x64], []
        o += 0x64
        for _, size in FLOOR_ARRAYS:
            n = u32(b, o)
            arrs.append([b[o + 4 + k * size:o + 4 + (k + 1) * size] for k in range(n)])
            o += 4 + n * size
        recs.append((head, arrs))
    if o != len(b):
        raise ValueError(f'trailing bytes at 0x{o:X}')
    return recs


def keyed(d, name):
    """追加領域 (+0x20) の {キー: 行}。"""
    b = open(glob.glob(os.path.join(d, f'*_{name}.bin'))[0], 'rb').read()
    e = u32(b, 0x20)
    return {u32(b, e + 8 * i): u32(b, e + 8 * i + 4) for i in range(u32(b, 0))} if e else {}


def cmd_floors(master, mapdir, only=None):
    msg = messages(master)
    ig, mg, mc = keyed(master, 'itemGroup'), keyed(master, 'monsterGroup'), keyed(master, 'mapChara')
    csv = open(glob.glob(os.path.join(mapdir, '*_csvMap.bin'))[0], 'rb').read()
    maps = {u32(csv, u32(csv, 0x10) + 4 * i): i for i in range(u32(csv, 0))}
    dd = table(master, 'dungeonData')
    owner = {}
    for i, r in enumerate(dd):
        owner.setdefault(u32(r, 4), []).append(f'{i} {msg(u16(r, 0x10))}')
    pos = lambda x, y: '(乱数)' if x == -9999 else f'({x},{y})'
    key = lambda t, v, p: '-' if v in (0, 0xFFFFFFFF) else f'{p}{t[v]}' if v in t else f'{v:08X}'
    for path in sorted(glob.glob(os.path.join(mapdir, '*_bin'))):
        num, h = os.path.basename(path).split('_')[:2]
        b = open(path, 'rb').read()
        if b[:4] != b'261\0' or (only and int(only) != int(num)):
            continue
        print(f'== {num} {h} dungeonData: {"; ".join(owner.get(int(h, 16), ["なし"]))}')
        ids = {u32(r[0], 0): i for i, r in enumerate(parse_floors(b))}
        for i, (hd, a) in enumerate(parse_floors(b)):
            m = u32(hd, 4)
            print(f'  記録 {i} id {u32(hd, 0):08X} 階 {s16(hd, 0x18)} マップ {maps.get(m, "生成") if m else "生成"}'
                  f' 群れ {key(mg, u32(hd, 8), "mg")} 宝箱 {key(ig, u32(hd, 0xC), "ig")} 大きさ {hd[0x2B]}')
            for e in a[0]:
                print(f'    出口 {u32(e, 0):08X} → 記録 {ids.get(u32(e, 4), "?")} {pos(s16(e, 0x10), s16(e, 0x12))} {e[0xC:0x10].hex(" ")}')
            for t, n in ((a[1], '人物'), (a[2], '特別な宝箱'), (a[3], '宝箱'), (a[7], '群れ')):
                for e in t:
                    k = key(mc, u32(e, 0), 'mc') if n == '人物' else key(mg, u32(e, 0), 'mg') if n == '群れ' else key(ig, u32(e, 0), 'ig')
                    print(f'    {n} {k} {pos(s16(e, 8), s16(e, 10))} {e[4:8].hex(" ")}')


if __name__ == '__main__':
    cmd, *args = sys.argv[1:] or ['-h']
    f = {'monsters': cmd_monsters, 'groups': cmd_groups, 'chests': cmd_chests, 'maps': cmd_maps, 'floors': cmd_floors}.get(cmd)
    if not f:
        print(__doc__); sys.exit(1)
    f(*args)
