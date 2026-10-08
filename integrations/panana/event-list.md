# Panana のイベント一覧実装

> 対象: 電波人間のRPG2 (`kahara`) v1.1.0。分類: Panana 実装記録 (最新状態の保証ではない)。
> 根拠: [再編前の解析記録](https://github.com/sweshelo/naauao/blob/27cc7ec6682589c764906ada88e78f5d04d57cc2/event-list.md) と本文に記す関数・実データ。従来の「確定」は元の解析で確認した範囲を指し、今回の再編で ROM 全体を再検証した意味ではない。
> アドレスは特記なき限り実行時/Ghidra アドレス (code.bin の位置 = アドレス − `0x100000`)。RPG3 には適用しない。

イベントデータ・条件表・限定実行器の解析手法は [kahara/event-list.md](../../kahara/event-list.md)。本書は Panana 固有の UI と実装管理を保存する。節番号は旧文書に対応する。

## 5. Panana での作り (panana#30)

- `src/game/arm.ts`: 実行器。`src/game/scripts.ts`: 振り分け ([kahara/event-list.md §3.1](../../kahara/event-list.md) の表だけ持つ) と、クラスのメッセージ・完了させる行。`src/game/conditions.ts`: 出現条件の種類。`src/game/eventlist.ts`: 行ごとにまとめる。
- ページ `#/events/ダンジョン.行`: 場所 (マップへのリンク)、出現条件の文、行の欄のメッセージ、スクリプトのクラス・処理の関数・完了させる行 (その行へのリンク)・メッセージ (メッセージのページへのリンク)、「この行を完了させるスクリプト」。
- 振り分けの表 (区画とレコードの種類 → 動作の生成) だけはコードの定数として持つ。ほかは ROM から読むので、code.ips で変えたコードにも追従する。

次に編集を作るときの手がかり:
- 出現条件は +0x4B / +0x4C / +0x00 / +0x04 を変えるだけで編集できる ([kahara/event-list.md §4](../../kahara/event-list.md) の表から選ぶ)。
- スクリプトの「完了させる行」は行番号でつながっているので、行番号を変えるとつながりが切れる ([kahara/events.md §5](../../kahara/events.md))。新しいつながりは汎用スイッチ ([イベント拡張 MOD §7](event-mods.md)) のような MOD が要る。
- スクリプトが進行・フラグをどう書き換えるか (セーブ変数の書き込み) はまだ拾っていない ([kahara/event-list.md §6](../../kahara/event-list.md))。
