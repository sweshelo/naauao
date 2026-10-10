# 再編時の検証記録

検証日: 2026-10-08。既存記述の移設と、今回 ROM から得た観測を区別する。入力・展開データ・生成 CIA はリポジトリ外に置いた。以下は入力の識別情報と解析結果であり、入手先やアクセス情報は含めない。

## 1. 入力の識別

`ctr.py info` で TMD / NCCH / ExHeader を読み、3 本とも NoCrypto を確認した。

| 対象 | TMD Title ID | TitleVersion | 製品コード | ExHeader 名 | CIA サイズ (B) |
|---|---|---|---|---|---:|
| kahara | `00040000000A7900` | 1040 (1.1.0) | CTR-N-JD2J | kahara | 168719360 |
| oahu Base | `00040000000EF000` | 0 | CTR-N-JDRJ | oahu | 205927424 |
| oahu Update | `0004000E000EF000` | 4096 (4.0.0) | CTR-U-JDRJ | oahu | 10867712 |

SHA-256（CIA 全体）:

```text
kahara      611e206ad82a32f57a3da5206512ddad42ef9f2b898c667353d1bbbfa13cb7d3
oahu Base   f97e3b122cc6439a5cabd41fc7fa94652a2206ba7b03ba15d4f37fa8ceaf24a4
oahu Update a126789b905e1e5e6370068ae7ff04cdc1306b6662c4177f632cdb92ce4628eb
```

展開した `code.bin`:

| 対象 | サイズ (B) | SHA-256 |
|---|---:|---|
| kahara | 5136384 | `453387393c02e564e6bda88ca4066e14cf65c2a87aa87ae8ce0dfd010d37fd13` |
| oahu Base | 5021696 | `a44eec5d36a9e69dd1fc5ab458786200ec2830885d8b376839b4047eab214c14` |
| oahu Update | 5029888 | `e560eac34b5721991134e0cf4fdea5e957c227e02b4f872263beeafa138c3fd4` |

ExHeader の text / ro / data / bss は [kahara.md](kahara.md) と [oahu.md](oahu.md) の記録に一致した。以降の関数アドレスは kahara 1040 または oahu **Update 4096** のフラットなコード（base `0x100000`）を指す。

## 2. コンテナと GS テーブル

| 対象 | RomFS のファイル総数（再帰） | ルート GS アーカイブ数 | GS version | master | master エントリ数 |
|---|---:|---:|---:|---|---:|
| kahara | 209 | 118 | 5 | `56562135` | 282 |
| oahu Base | 269 | 176 | 7 | `21350000` | 288 |
| oahu Update | 12 | 11 | 7 | `21350000` | 288 |

master の GS ヘッダーから行数・行サイズを実測した。下表の oahu は Base / Update が同じ値である（内容まで同一という意味ではない）。

| テーブル | kahara | oahu |
|---|---|---|
| itemData | 713 × 0x30 | 1191 × 0x40 |
| actionData | 672 × 0x3C | 1126 × 0x30 |
| monsterParameter | 185 × 0x54 | 201 × 0x70 |
| conditionData | 94 × 0x3C | 125 × 0x3C |
| monsterGroup | 144 × 0x2E | 190 × 0x3E |
| treasureGroup | 591 × 0x28 | 283 × 0x50 |
| mapGroup | 58 × 0x2C | 89 × 0x34 |
| mapData | 91 × 0x7 | 167 × 0x7 |
| mapObject | 323 × 0x2C | 510 × 0x38 |
| levelData | 99 × 0x54 | 199 × 0x5C |
| soundData | 418 × 0xC | 597 × 0xC |
| flagData | 150 × 0x10 | 259 × 0x10 |

`*_EventObject.bin` も全件走査し、kahara の 55 テーブルはすべて行幅 0x50、oahu Base の 88 テーブルおよび Update の 1 テーブルはすべて 0x58 だった。両作で同じテーブル名やエントリハッシュを持っていても、行レイアウトを共用できない。

## 3. oahu の差分と CIA ツール

Update の `patchList.bin` は 48 B、先頭 u32 は 11、続くハッシュは次の順序だった:

```text
21350000 3B630000 A9DF0000 296B0000 97CF0000 7BF70000
619D0000 838B0000 58190000 00910000 6E380000
```

全 11 アーカイブについて、Base / Update 間でエントリ数とエントリハッシュの並びが一致することを確認した。展開後エントリを比較した変更一覧も [oahu-update.md](oahu-update.md)「Update で変わったもの」の記録と一致した。master で変更された GS テーブルは `actionData.bin` / `monsterGroup.bin` / `conditionData.bin`。

今回実行した検証:

- 入力 CIA 3 本の `ctr.py verify`: TMD コンテンツ SHA-256、NCCH サイズ、ExHeader、ExeFS、RomFS superblock、IVFC 3 段がすべて `ok` / `ALL OK`。
- `ctrbuild` の構築関数で、元の `patchList.bin` の順序を保持して Update を再構築: **CIA 全体が入力とバイト一致**。
- `ctrbuild.py update ... --version 4096`: 内部ハッシュがすべて一致。CLI は `patchList.bin` をハッシュ順に作り直すので、同じ版番号でも入力 CIA とのバイト一致にはならない。
- `ctrbuild.py applied` の出力: 内部ハッシュがすべて一致し、RomFS の **269 ファイルすべて**が `ctr.py merge` の出力と一致。
- `gsarc.py catalog`: kahara 118 アーカイブ、oahu Base + Update の差分選択を完走。

kahara の `38C1B821` に、comp=1 / raw=0 / size=24 の**空 ZIP**（EOCD `PK\x05\x06` のみ）があった。従来の `name_only` は local header を想定して範囲外を読み、`unpack` も最初の ZIP メンバーが存在する前提だった。空 ZIP を名前なし・空データとして扱うよう修正後、catalog の完走と 0 B ファイルへの展開を実データで確認した。

これらは構造・内部ハッシュ・データ内容の検証である。RSA 署名の有効性、実機・Azahar でのインストールと起動は今回検証していない。

## 4. 記述の矛盾に対する局所解析

### kahara: master +0x39C は扉の表か

[map.md](../kahara/map.md) の大型セルモデルと扉の参照先を、コードから区別した。

- `FUN_001C97F8`: `0x1C9958`〜`0x1C9960` でセル +8 の位置を作り、`0x1C99E0` でその +4（セル +0x0C）を読む。`0x1C99F8` で master +0x39C を参照し、`0x1C9CF0` / `0x1C9CFC` で行を選択・取得する。
- 扉側の `FUN_002EFFA0`: `0x2F00B8` で EventObject +0x46 を読み、`0x2F0420` で master +0x3D4（mapObject）を参照する。

master +0x39C を扉のモデル表とする旧記述は採用しない。

### oahu: flag 0x49 は 1 要素 8 bit か、2 B か

Update master の `flagData.bin` 行 0x49 は次の 16 B:

```text
00 00 00 00 00 00 00 00 C4 00 02 20 02 D0 D0 D0
```

+8 の要素数は 196、+0x0B は 0x20（読み出し幅 8 bit）、+0x0C は 2。`FUN_004A261C` は `0x4A26C8` / `0x4A26D4` で +0x0B >> 2 を幅とし、`0x4A26FC` で +0x0C を取得する。`0x4A270C` / `0x4A2710` で **幅 × 個数 × 要素番号**をビット位置へ加算し、`0x4A2718`〜`0x4A2738` で個数回読み、出力へ `strb` する。

したがって **196 要素 ×（8 bit 値 2 個）**。単一の 8 bit 値が 196 個、という記述では不足する。`FUN_004EF1A4` は `0x4EF1F0` / `0x4EF1F4` で 2 B を読み、1 B 目の下位 5 bit と 2 B 目を 13 bit 左シフトした値を個体参照へ組み込む。[story.md](../oahu/story.md) と [map-models.md](../oahu/map-models.md) は同じデータの異なる読み手を記述していた。

### kahara: ドロップ率の単位と補正

`FUN_00283E68` は `0x283F70` / `0x283F88` / `0x283FA0` で状態 ID 0x50 / 0x51 / 0x52 の値を取得する。9 枠のループで `floor(枠番号 / 3)` に応じた補正値を使う。率の段階は `FUN_00289138` が実行時データ +0x44 から u16 で読み、0x10 は抽選をスキップする。

`0x284074` の読み出し先は battleParameter の行データ +0x10C + 段階 × 2。その分母表（u16 × 16）は:

```text
1, 3, 4, 6, 8, 12, 16, 32, 64, 128, 256, 512, 1024, 4096, 8192, 16384
```

分母を B、補正値を b とすると、b が負のとき D=1。それ以外は倍精度で

```text
p = 1 - pow(1 - 1 / B, b * 0.01)
D = max(1, ARM の vcvt.s32.f64 による 1 / p の整数化)
```

を計算する（`0x284068`〜`0x2840A4`）。`0x2840E4` / `0x2840E8` は乱数 u32 と D の積の上位 32 bit が 0 なら当選する。したがって整数化後の分母 D による抽選であり、単に元の確率へ b% を掛ける処理ではない。乱数の一様性を仮定した厳密な確率は `ceil(2^32 / D) / 2^32` となる。

呼出し先 `FUN_0044E4D0` は Unicorn 上で ROM の命令列を実行し、(0.5, 2)、(0.75, 0.5)、(0.9, 1.2)、(2, 3) がそれぞれ `pow` と一致した。さらに `0x284048`〜`0x2840AC` を実 ROM の分母表・定数で局所実行した:

| 段階 | B | b | 得られた D |
|---|---:|---:|---:|
| 1 | 3 | 100 | 3 |
| 1 | 3 | 150 | 2 |
| 1 | 3 | 200 | 1 |
| 7 | 32 | 100 | 32 |
| 7 | 32 | 200 | 16 |
| 0 | 1 | 100 | 1 |
| 1 | 3 | -1 | 1 |
| 1 | 3 | 0 | 2147483647 |

最後の b=0 は Unicorn の ARM 浮動小数点変換で得た値であり、JavaScript の `Infinity` をそのまま分母にする実装とは一致しない。実機上の抽選・報酬配分・補正値の取り得る全範囲は今回の局所検証に含めない。

## 5. 再現の入口

復号済み入力を用意し、出力をリポジトリ外に指定する。コマンドはリポジトリルートから実行する例:

```sh
sha256sum /path/to/kahara.cia /path/to/base.cia /path/to/update.cia
python3 roms/tools/ctr.py info /path/to/kahara.cia /path/to/base.cia /path/to/update.cia
python3 roms/tools/ctr.py verify /path/to/kahara.cia /path/to/base.cia /path/to/update.cia
python3 roms/tools/ctr.py extract /path/to/kahara.cia /tmp/kahara-extracted
python3 roms/tools/ctr.py merge /path/to/base.cia /path/to/update.cia /tmp/oahu-merged
python3 roms/tools/gsarc.py catalog /tmp/kahara-extracted/romfs
python3 roms/tools/gsarc.py catalog /tmp/oahu-merged/romfs
python3 roms/tools/armdis.py /tmp/kahara-extracted/exefs/code.bin 00283E68 240
python3 roms/tools/armdis.py /tmp/oahu-merged/exefs/code.bin 004A261C 73
```

`ctr.py verify` の既存実装は表示された `FAIL` / `ERRORS` も確認する（終了コードだけでは失敗を検出できない）。同梱 `gsarc.py` のコマンドは `list` / `catalog` / `unpack` で、旧 Panana の `replace` コマンドとは別物である。

## 6. lanai (RPG FREE!) の初回解析 (2026-10-10)

入力の識別値・版は [lanai.md](lanai.md)。`ctr.py verify` は Base / Update とも `ALL OK`。今回同梱ツールに加えた対応と、照合に使った根拠:

| 項目 | 方法 | 結果 |
|---|---|---|
| アーカイブ version 10 | `gsarc.py` (ヘッダー 0x18 に対応) で全 224 個のルートのアーカイブを展開 | エントリ 12,599 個を展開できた |
| GS テーブルの新形式 | `gstable.py` で全エントリを解析 | 4,317 個が表として読め、再配置・欄の名前が一致 |
| コンテンツの番号 | master の Contents の行 r とアーカイブの `contents{r:04}.cro` | 127 行すべて一致 |
| CRR | `.crr/contents0038.crr` に `SHA-256(CRO 先頭 0x80)` があるか | Update の CRR にはある、Base の CRR にはない |
| スタミナ | MapStage +0x3D とクイズの正解 | 2 問で一致、1 問は○×問題と矛盾しない |
| コード入力 | `lanaicode.py dec A4J8Y13ML7TAWWE1` / `enc 0 49 0 1.17.0` | チェック一致・版 1.17.0・行 49。エンコードで同じ 16 文字に戻る。乱数 2000 件の往復も一致 |

エミュレータ・実機での動作確認はしていない。関数の意味の多くはコードの読み取りによる ([lanai の確度の目安](../lanai/README.md#確度の目安))。

```sh
python3 roms/tools/ctr.py merge /path/to/free-base.cia /path/to/free-update.cia /tmp/lanai-merged
python3 roms/tools/gsarc.py catalog /tmp/lanai-merged/romfs
python3 roms/tools/gstable.py info <展開したエントリ>
python3 roms/tools/lanaicode.py dec A4J8Y13ML7TAWWE1
python3 roms/tools/armdis.py /tmp/lanai-merged/exefs/code.bin 001B53D4 300
```
