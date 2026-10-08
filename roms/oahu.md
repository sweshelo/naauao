# RPG3 (oahu) の ROM 識別・展開

対象は Base TitleVersion 0 と Update TitleVersion 4096。ファイル名からタイトルや版を推定せず、TMD と ExHeader を読む。以下の数値は既存解析記録の移設であり、今回の再検証状況は [検証記録](verification.md) に分けて記す。

## 1. ROM 基本情報

| | Base | Update |
|---|---|---|
| 入力名 (任意) | `base.cia` | `update.cia` |
| タイトル ID (TMD) | `00040000000EF000` | `0004000E000EF000` |
| TitleVersion (TMD) | 0 | 4096 (= 4.0.0) |
| 製品コード | CTR-N-JDRJ | CTR-U-JDRJ |
| ExHeader の名前 | `oahu` | `oahu` |
| 暗号 | なし (NCCH flags[7] の NoCrypto) | なし |
| ExeFS | `.code` (LZ) / banner / icon / logo | `.code` / icon / logo (banner なし) |
| RomFS | 0xBFF7000 (約 192 MB、269 ファイル) | 0x627000 (約 6 MB、12 ファイル) |
| コンテンツ 1 | 電子説明書 (CFA, 0x159000) | 同じ |

- 開発コード名は **`oahu`** で確定 (ExHeader の名前)。`honolulu` は RPG3 自身ではなく、master にある `flagDataHonolulu.bin` の名前に出てくる ([マスターデータ](../oahu/analysis.md))。`kahara` (RPG2 の内部名) と並んでいるので、RPG2 より前の作品 (初代「電波人間のRPG」など) の内部名と推定。
- ExHeader (展開後の code.bin はセクションが連続していて、RPG2 と同じく base 0x100000 のフラットバイナリとして読める):

| | Base | Update |
|---|---|---|
| text | 0x00100000 (0x453CB8) | 0x00100000 (0x4558C0) |
| ro | 0x00554000 (0x401DC) | 0x00556000 (0x4023C) |
| data | 0x00595000 (0x3452C) | 0x00597000 (0x34568) |
| bss | 0x6FEA4 | 0x6F8E8 |
| code.bin (展開後) | 5,021,696 B | 5,029,888 B |

- CPU は RPG2 と同じ ARM11。依存するシステムモジュール (ExHeader の deps) も Base と Update で同じ。
- **実際に動くのは Update の code.bin。** アップデートを入れた状態でゲームが起動するのは Update の NCCH (ExeFS) なので、code.ips やアドレスはすべて Update (TitleVersion 4096) の code.bin を基準にする。

## 2. 展開手順

`roms/tools/` の Python スクリプトで、ctrtool や boot9 なしで展開できる (どちらも復号済みの CIA が前提)。

```
python3 roms/tools/ctr.py info  base.cia update.cia            # CIA / TMD / NCCH / ExHeader の要約
python3 roms/tools/ctr.py extract base.cia   out/base           # exheader.bin, exefs/code.bin (展開済み), romfs/
python3 roms/tools/ctr.py merge base.cia update.cia out/merged  # ゲームの差分選択を反映した解析用フォルダ
python3 roms/tools/gsarc.py catalog out/merged/romfs            # ルートのアーカイブの一覧
python3 roms/tools/gsarc.py list <archive>
python3 roms/tools/gsarc.py unpack <archive> <outdir>
python3 roms/tools/gsmb.py <file.gsmb> [ID ...]
python3 roms/tools/armdis.py out/merged/exefs/code.bin <addr> [count]   # capstone が必要
```

- `merge` の出力は `exheader.bin` / `exefs/code.bin` / `romfs/`。比較対象の Base / Update は別途保持する。`merge` は RPG3 の `patchList.bin` に対応した処理で、他作品に自動適用しない。
- ROM 本体と展開したデータはリポジトリに入れない。


更新差分・CIA 再構築は [oahu-update.md](oahu-update.md)、ゲームデータは [oahu/analysis.md](../oahu/analysis.md) を参照。
