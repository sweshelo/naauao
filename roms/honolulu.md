# honolulu: ROM の識別と展開

対象は『電波人間のRPG』(初代) 日本版の Base。解析文書の入口は [honolulu/README.md](../honolulu/README.md)。

## 1. ROM 基本情報

`python3 roms/tools/ctr.py info` で読んだ値 (2026-10 に確認)。

| | Base |
|---|---|
| タイトル ID (TMD) | `0004000000077E00` |
| TitleVersion (TMD) | 1024 (1.0.0) |
| 製品コード | CTR-N-JD8J |
| ExHeader の名前 | `honolulu` |
| 暗号 | なし (NoCrypto) |
| ExeFS | `.code` (LZ 圧縮) / banner / icon / logo |
| RomFS | ルートに 45 個のハッシュ名のアーカイブ + `sound/`・`shaders/`・`extdata_icon/` |
| コンテンツ 1 | 電子説明書 (CFA, 0xA9000) |

- ExHeader: text 0x00100000 (0x1FEBF8) / ro 0x002FF000 (0x1B198) / data 0x0031B000 (0x14A84) / bss 0x4B244。展開後の code.bin はセクションが連続していて、RPG2 と同じく base 0x100000 のフラットバイナリとして読める (2,293,760 B)。
- CPU は ARM11。依存するシステムモジュール (deps) は 30 個。
- Update はこの資料の時点で入手していない。Update があるかどうかは未確認。アドレスはこの Base の code.bin 基準。
- 内部名 `honolulu` は ExHeader の名前で確定。RPG3 の master に `flagDataHonolulu.bin` がある ([roms/oahu.md](oahu.md#1-rom-基本情報)) のは、初代のデータを参照する機能のためと推定 (未確認)。

## 2. 展開

```sh
python3 roms/tools/ctr.py info honolulu-base.cia
python3 roms/tools/ctr.py extract honolulu-base.cia out/honolulu
python3 roms/tools/gsarc.py catalog out/honolulu/romfs
python3 roms/tools/gsarc.py unpack out/honolulu/romfs/56562135 out/honolulu/master
```

- アーカイブはすべて GS アーカイブ version 5 (RPG2 と同じ。ヘッダー 0x0C、28 B のエントリ、+0x14 = 0xFFFFFFFF)。同梱の `gsarc.py` でそのまま読める。
- master のルート名は **`56562135` で RPG2 と同じ**。ルートのファイル名だけで作品を判定すると RPG2 と取り違える。タイトル ID か ExHeader の名前で判定する。
- 復号済み CIA を入力する。ROM・展開データはリポジトリに入れない。
