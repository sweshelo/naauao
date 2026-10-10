# ROM の識別・展開・検証

このディレクトリは CIA / NCCH / ExeFS / RomFS の操作、入力 ROM の版、検証条件を扱う。ゲーム内のデータ仕様は [common](../common/README.md)、[kahara](../kahara/README.md)、[oahu](../oahu/README.md)、[lanai](../lanai/README.md) を参照。

| 目的 | 文書 |
|---|---|
| RPG2 の入力 ROM と展開 | [kahara.md](kahara.md) |
| RPG3 Base / Update の識別と展開 | [oahu.md](oahu.md) |
| RPG3 の差分選択、マージ、CIA 再構築 | [oahu-update.md](oahu-update.md) |
| RPG FREE! Base / Update の識別と展開 | [lanai.md](lanai.md) |
| 今回再確認した範囲と保留事項 | [verification.md](verification.md) |

## 同梱ツール

リポジトリルートをカレントディレクトリとして実行する。Python 3 を使用し、`armdis.py` のみ `capstone` が必要。これらは復号済みダンプ用の解析用スクリプトで、すべての CIA / GS ファイルの変種への対応を保証しない。

| スクリプト | 用途・範囲 |
|---|---|
| [tools/ctr.py](tools/ctr.py) | CIA 情報表示、展開、内部ハッシュ検証。`merge` は RPG3 の patchList 方式用 |
| [tools/ctrbuild.py](tools/ctrbuild.py) | RomFS / ExeFS / NCCH / CIA の組み立て。`applied` / `update` は RPG3 用 |
| [tools/gsarc.py](tools/gsarc.py) | GS アーカイブの一覧・展開。RPG3 用に作成、RPG2 と共通の 28-byte エントリ配置を読む。RPG FREE! の version 10 (ヘッダー 0x18) にも対応。`replace` は未実装 |
| [tools/gstable.py](tools/gstable.py) | RPG FREE! (lanai) 形式の GS テーブルの一覧・行の表示・メッセージ (タグつき) の表示 |
| [tools/lanaicode.py](tools/lanaicode.py) | RPG FREE! のコード入力 (16 文字) のデコード・エンコード |
| [tools/gsmb.py](tools/gsmb.py) | GSMB メッセージの参照 |
| [tools/armdis.py](tools/armdis.py) | ARM モードの code.bin を base 0x100000 として逆アセンブル |
| [tools/testmod.py](tools/testmod.py) | RPG3 のアイテム名変更の試料を手元のダンプから生成 |

`ctr.py verify` はデータハッシュの検証で、RSA 署名・インストール可否・起動成功を保証しない。元のファイルを保存し、抽出先には新しい空ディレクトリを使う。ROM、抽出したゲームデータ、認証情報はリポジトリに含めない。
