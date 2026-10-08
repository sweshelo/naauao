# kahara: ROM の識別と展開

対象は『電波人間のRPG2』日本版。解析文書の入口は [kahara/analysis.md](../kahara/analysis.md)。

## ROM 基本情報
- CIA: `00040000000A7900.cia` / 製品コード CTR-N-JD2J / TitleVersion 1.1.0 (1040)
- 暗号化なし (NCCH Crypto: None)、ExeFS `.code` は LZ 圧縮 → 展開済み `extracted/exefs/code.bin`
- ExHeader: 内部名 `kahara`、SD アプリ
  - text 0x00100000 (0x3BF01C) / ro 0x004C0000 (0x50484) / data 0x00511000 (0xD4D3C) / bss 0x59778
  - 展開後 code.bin はセクションが連続しているので base 0x100000 のフラットバイナリとして読める
  - CPU は ARM11 (ARMv6K)。**Thumb-2 / MOVW は無い**

## 本リポジトリの展開ツール

復号済み CIA を入力する。リポジトリのルートで実行する例:

```sh
python3 roms/tools/ctr.py info 00040000000A7900.cia
python3 roms/tools/ctr.py extract 00040000000A7900.cia out/kahara
python3 roms/tools/gsarc.py catalog out/kahara/romfs
python3 roms/tools/gsarc.py unpack out/kahara/romfs/56562135 out/kahara/master
```

ROM 本体・展開データ・セーブは追跡対象にしない。GPG の復号は CIA の復号とは別工程。配布物名・鍵・保存先は解析仕様に含めない。

## 旧 ctrtool / Panana での展開例

元の記録 (下記 `tools/gsarc.py` は外部 Panana のコマンド):

```
ctrtool --contents=extracted/contents 00040000000A7900.cia
ctrtool --exheader=exheader.bin --exefsdir=exefs --romfsdir=romfs --decompresscode contents.0000.00000006
python tools/gsarc.py extracted/romfs extracted/romfs_unpacked
```


各相対パスは実際の展開先に合わせる。特に 2 行目の入力は 1 行目で出力された `extracted/contents.0000.00000006`、`exefs` / `romfs` は出力先であり、元の例は作業ディレクトリの切り替えを省略している。

## Luma3DS での適用
- Rosalina/Luma 設定で「Enable game patching」を有効化
- `/luma/titles/00040000000A7900/romfs/56562135` … 差し替えアーカイブ (LayeredFS、ルートのハッシュ名で配置)
- `/luma/titles/00040000000A7900/code.ips` (または code.bps / 展開済み code.bin 丸ごと) … コードパッチ
- 注意: パッチは本 CIA (v1.1.0) の code.bin 基準。実機の導入版が異なる場合はアドレスを再確認すること
