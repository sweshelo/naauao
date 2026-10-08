# 電波人間のRPG2 (kahara): RomFS とマスターデータ

対象: 日本版 Title ID `00040000000A7900`、TitleVersion 1040 (1.1.0)。アドレスは展開済み code.bin の仮想アドレス (base `0x100000`)。[解析案内](analysis.md) / [ROM の識別・展開](../roms/kahara.md)。

## RomFS
ルートのファイル名は 32bit ハッシュ (例 `56562135`)。中身は独自コンテナ:

[共通アーカイブ形式](../common/formats.md#gs-アーカイブ)を参照。kahara は version = 5、エントリの +0x14 = `0xFFFFFFFF` (−1)。データはパディング無しで詰めて配置される。

- Panana の `tools/gsarc.py` は展開・差し替え (`replace`) に対応し、無改変リビルドでバイト一致を確認した記録がある。本リポジトリの [roms/tools/gsarc.py](../roms/tools/gsarc.py) は読み取り・展開用で、CLI は異なる。
- comp 1 は deflate 圧縮の 1 ファイル入り ZIP (元のファイル名を含む)、comp 6 は Nintendo LZ10。
- コードは `FUN_003093b0(obj, 0x56562135)` のようにアーカイブをハッシュで開く (`rom:/XXXXXXXX`)

### 主要アーカイブ `56562135` (マスターデータ)
- `itemData.bin` (entry 60), `vendor.bin` (102), `treasureGroup.bin` (30), `flagData.bin` (98)
- `MessageSystemCommon_JP.gsmb` (21) … アイテム名・説明文
- 他 monsterParameter / levelData / createSelectEquip など

GS テーブルのヘッダーは [共通形式](../common/formats.md#gs-テーブル)。行の意味は作品ごとに異なる。

旧解析で GS テーブルの読み取りに使った `tools/gstable.py` は本リポジトリに未収録。ファイル構造は上記の共通形式と、対象テーブルの作品別文書を参照する。
