# 再編と照合の記録

2026-10-08。再編前の基準は naauao [`27cc7ec6682589c764906ada88e78f5d04d57cc2`](https://github.com/sweshelo/naauao/tree/27cc7ec6682589c764906ada88e78f5d04d57cc2)。参照実装の照合は Panana [`c48b0baaffab5d021625183dce4ec69e62afc37f`](https://github.com/sweshelo/panana/tree/c48b0baaffab5d021625183dce4ec69e62afc37f) を用いた。ROMを今回取得して再確認した識別値・ハッシュ・局所解析は [roms/verification.md](../roms/verification.md) に記録する。

## 配置を変えた理由

旧ルートの文書と `reference/` は基本的にKahara専用だったが、その配置では作品が識別しづらかった。またゲーム本来の仕様、Panana独自の追加パッチ、初期設計時の実装状況が混在していた。ゲーム仕様を作品ごとに、ROM操作と共通形式を目的ごとに分け、実装管理の記録を `integrations/panana/` に切り出した。

`integrations/panana/` は情報を失わず移行できるよう残した履歴資料であり、今後の実装タスクの完了状況を管理する場所ではない。実装管理はPanana側で行う。

## 旧パスからの移行

| 旧パス | 新しい入口・分割先 |
|---|---|
| `analysis.md` | [kahara/analysis.md](../kahara/analysis.md)（itemData、ショップ、メッセージ、セーブ、フィールド、コードへ分割）、[共通形式](formats.md)、[ROM](../roms/kahara.md)、[実装履歴](../integrations/panana/analysis.md) |
| `battle.md` / `action-performance.md` / `monster-motion.md` / `item-effects.md` / `shrine.md` | 同名ファイルを [kahara/](../kahara/README.md) へ。UI・実装履歴は [連携資料](../integrations/panana/kahara-battle.md) |
| `map.md` / `worldmap.md` / `encounters.md` | 同名ファイルを [kahara/](../kahara/README.md) へ |
| `events.md` | [ゲーム仕様](../kahara/events.md) / [追加イベントMOD](../integrations/panana/event-mods.md) |
| `event-list.md` | [抽出解析](../kahara/event-list.md) / [Panana UI](../integrations/panana/event-list.md) |
| `new-map.md` | [ゲームの表・保存制約](../kahara/new-map.md) / [PNMP拡張設計・実装](../integrations/panana/new-map.md) |
| `map-editor-design.md` | [初期設計の履歴](../integrations/panana/map-editor-design.md) |
| `reference/*.md` | [kahara/reference/](../kahara/reference/README.md) |
| `oahu/analysis.md` §1–3 | [ROM識別・展開](../roms/oahu.md) / [更新差分](../roms/oahu-update.md)。§4以降は [元の文書](../oahu/analysis.md) |
| `oahu/map.md` | [マップ](../oahu/map.md) / [イベント](../oahu/events.md) / [モデル](../oahu/map-models.md) |
| `oahu/story.md` | [仕組み](../oahu/story.md) / [個別段階表](../oahu/reference/story-stages.md) |
| `oahu/sound.md` §4 | [masterのテーブル読み手](../oahu/master-readers.md) |
| `oahu/panana-compat.md` | [連携設計の履歴](../integrations/panana/panana-compat.md) |
| `oahu/update.md` / `oahu/tools/` | [roms/oahu-update.md](../roms/oahu-update.md) / [roms/tools/](../roms/README.md) |

旧パスの複製を残すとエージェントが古い仕様を読むため、入口と相互リンクを更新した。Panana等の親リポジトリから参照する際は、サブモジュール更新とともに新パスへ変更する必要がある。

## 照合・訂正

| 対象 | 問題と対応 | 根拠 |
|---|---|---|
| Kaharaモデル表 | master +0x39Cを扉用とする旧説明を訂正。大型セルモデルと扉は別表 | [map.md](../kahara/map.md) のROM局所逆アセンブル |
| Kaharaドロップ率 | 「単位未調査」と効果説明の断定が混在。段階→分母表と補正式・丸めを確認 | [battle.md §2.1](../kahara/battle.md)、[ROM検証](../roms/verification.md) |
| Oahuセーブ0x49 | 「8bit × 196」は要素内の繰り返しを欠落。196要素 × 8bit値2個に修正 | [story.md §3.1](../oahu/story.md)、実データと復元関数 |
| PNMP +0x14 | 行配列そのものではなく m × u32 の行ポインタ配列。フックは13命令+リテラル1語=56B | [Panana実装との照合](../integrations/panana/new-map.md) |
| 新規マップのY範囲 | 保存領域の40行と実行時セル配列を同一視していた。エディタ制限30×30と解析済み範囲を区別 | [kahara/new-map.md](../kahara/new-map.md) |
| vendor.bin | 旧追加方針の「ショップ」という説明がShopItem解析と不一致 | [kahara/items.md](../kahara/items.md)、[shops.md](../kahara/shops.md) |
| MonsterParameter +0x4A bit3 | 戦闘文書では意味未確認だったがモーション文書に後続解析あり | [monster-motion.md](../kahara/monster-motion.md) へ統一 |
| Oahuイベント条件 | 「+0x08の後ろに2値追加」という位置説明が表と不整合 | [events.md](../oahu/events.md) の出現・消滅それぞれ2値という配置へ整理 |
| Oahu Shop ID | 44行なのに「44まで」という曖昧な記述 | [shops.md](../oahu/shops.md) の0x2C以上→0と整合する0〜43へ |
| Oahuストーリー | 「常に前にしか進まない」はクリア後の再選択記録と矛盾 | [story.md](../oahu/story.md) で通常進行と再選択を区別 |
| 古い未実装記述 | 音・ストーリー・ほこら等の過去の実装状況が仕様の未解析と混在 | [Panana連携資料](../integrations/panana/README.md) へ分離 |
| CIAの版・起動 | ファイル名の版とTMDを区別。eShop終了から最終版を推定しない。内部ハッシュと実機起動を区別 | [ROM資料](../roms/README.md) |
| 同梱GSツール | 旧外部ツールのreplaceと同梱read-onlyツールを区別。Kaharaの空ZIPを処理できるよう修正 | [ツール案内](../roms/README.md)、[ROM検証](../roms/verification.md) |

## 保全と限界

- Kaharaの参照表11ファイルは、元のMarkdown表5,492行（ヘッダーを含む）を行単位で一致確認した。表の意味を今回すべて再解析したという意味ではない。
- ローカルのリンク・見出しアンカー・READMEからの到達性は `python3 scripts/check_docs.py` で確認する。
- 実行時描画、戦闘全体のドロップ頻度、改変CIAの実機・Azaharでの起動は今回確認していない。
- イベント中の直書きメッセージ件数は走査対象・数え方の異なる記録を区別して残している。生成器の欠落など、再現条件が揃わない点は [kahara/event-list.md](../kahara/event-list.md) と各表の出典を参照する。
- 「確定」「未解析」は本文の対象範囲に従う。上表にない仕様を再編作業だけで新たに確定とはしていない。
