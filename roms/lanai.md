# 電波人間のRPG FREE! (lanai) の ROM 識別・展開

対象は日本版の Base TitleVersion 0 と Update TitleVersion 17408 (17.0.0)。ファイル名から版を推定せず、TMD と ExHeader を読む。数値は 2026-10-10 に同梱ツールで実測した。

## 1. ROM 基本情報

| | Base | Update |
|---|---|---|
| タイトル ID (TMD) | `0004000000125D00` | `0004000E00125D00` |
| TitleVersion (TMD) | 0 | 17408 (= 17.0.0) |
| 製品コード | CTR-N-JF7J | CTR-U-JF7J |
| ExHeader の名前 | 空 (0 埋め) | 空 (0 埋め) |
| ExHeader の remaster version (+0x0E) | 0 | 0x11 (17) |
| 暗号 | なし (NoCrypto) | なし |
| ExeFS | `.code` (LZ) / banner / icon | `.code` (LZ) / icon (banner なし) |
| RomFS | 0xDAD7000 (約 218 MB、ファイル 284 個) | 0x67AB000 (約 104 MB、ファイル 333 個) |
| ルートの 8 桁ファイル | 124 個 | 185 個 (`patchList.bin` に 184 個) |
| コンテンツ 1 | 電子説明書 (CTR-P-CTAP) | 同じ |

- **内部名は `lanai` と判断した。** ExHeader の名前は空だが、RomFS の `app/lanai.crs`、master の `extdata_lanai.icn`、デバッグ文言の `LanaiTool`、RTTI の `22LanaiAntennaEventFirst` に出てくる。kahara (RPG2)・oahu (RPG3)・honolulu と同じくハワイの地名。
- ExHeader のセクション (展開後の code.bin は base 0x100000 のフラットバイナリとして読める):

| | Base | Update |
|---|---|---|
| text | 0x00100000 (0x34550C) | 0x00100000 (0x399900) |
| ro | 0x00446000 (0x46D88) | 0x0049A000 (0x48848) |
| data | 0x0048D000 (0x198A4) | 0x004E3000 (0x19A68) |
| bss | 0x11C02C | 0x11FEAC |
| code.bin (展開後) | 3,829,760 B | 4,182,016 B |

- 実際に動くのは Update の code.bin。本資料のアドレスは特記がなければ **Update (TitleVersion 17408) の code.bin** を指す。

## 2. 展開手順

RPG3 と同じく `patchList.bin` による差分方式 ([RPG3 の差分選択](oahu-update.md#ゲームによる差分選択と配布方式)) なので、`ctr.py merge` がそのまま使える。

```
python3 roms/tools/ctr.py info    base.cia update.cia
python3 roms/tools/ctr.py extract base.cia   out/base
python3 roms/tools/ctr.py merge   base.cia update.cia out/merged
python3 roms/tools/gsarc.py catalog out/merged/romfs        # version 10 のアーカイブ
python3 roms/tools/gsarc.py unpack  <archive> <outdir>
python3 roms/tools/gstable.py info|dump <table>               # lanai 形式の GS テーブル
python3 roms/tools/lanaicode.py dec <16 文字のコード>          # コード入力のデコード
```

- `merge` は「patchList.bin にないので無視」として `.crr/`、`app/`、`sound/`、`proctex_files/`、`012A000A` を警告する。ただし Update の `.crr/` は Update の CRO に合わせた内容 ([コンテンツ](../lanai/contents.md#4-cro-と-crr)) なので、Base 側の `.crr/` は古い。解析には Update の `.crr/` を使う。
- `012A000A` (電波人間の作成の表) は Update の RomFS にあるが patchList に載っていない。Base の同名ファイルとの差は未確認。

## 3. 検証値

| 対象 | SHA-256 |
|---|---|
| Base CIA (233,538,560 B) | `bb43c8f49f9072464cf2aa86fe3a8c4e5d3be4bed966fe4005dd39e14af6060e` |
| Update CIA (112,845,824 B) | `e85a12409311c233a874e327d02ead5f9ee7e1b9fba81b41862e1a1a74aaa09d` |
| Base code.bin (展開後) | `074fc7ec94ec809292adb48379469072397db17d3afbc6a19d4c6d46ce70b726` |
| Update code.bin (展開後) | `20ff48ba6bd19d3ee966df7e234a10afb44ad585f73612bc2ff9acac9e78a041` |

ゲームデータの仕様は [lanai の索引](../lanai/README.md)。
