---
name: naauao-docs
description: 3DS「電波人間のRPG2」(v1.1.0) と「電波人間のRPG3」(oahu/) の ROM 解析ドキュメント。マップ・ダンジョン・戦闘(ダメージ計算/状態/ボス変身/AI)・モンスター・アイテム・装備・ショップ・宝箱・イベント/ギミック/スクリプト・エンカウント/BGM・演出(actionData/effectData)・ワールドマップ・精霊ほこら・code.ips パッチ・MOD・Panana・マップエディタの実装や仕様確認に使う。Game data structures, RomFS/GS tables, battle formulas, event objects and MOD/patch design for the game; use when editing or reading these specs.
---

# naauao ドキュメント索引

## 使い方の原則
- 全部読まない。下のルーティング表で 1〜2 ファイルに絞り、見出しは `grep -n '^#' <file>` で先に取る。
- 行数の多いファイルは見出しで範囲を決めて `Read` の offset/limit で読む。
- `reference/*.md` は `tools/gen_reference.py` / `gen_scripts.py` 生成の**データ表**（手で直さない）。内部の「docs/xxx.md」表記は、このリポジトリのルート `xxx.md` を指す。
- 関数名 `FUN_xxxxxxxx` は code.bin (3DS ARM) のアドレス。「(確定)」付きの節は検証済み、「未解析/未確認/未調査」節は未確定。

## 設計・仕様（ルート）

| 話題 | ファイル (行) | 内容 |
|---|---|---|
| ROM・全体の解析メモ | analysis.md (436) | ROM/RomFS/展開手順、GS テーブル形式、itemData(713行×0x30)、flagData、actionData(672行×0x3C)、GMSG メッセージと制御コード、Shop/ShopItem、アイテム追加 MOD、code.ips、Azahar/Luma3DS、ワープ記録とテレポーター+、回復の泉 |
| 戦闘 | battle.md (357) | MonsterParameter(185行×0x54)、ボス変身(§3)、行動選択(§4)、状態 conditionData 94件(§5)、計算式(§6: 物理・固定幅・属性倍率・状態付与)、特殊行動(§7)、actionData(§8)、モンスター追加の制約(§9) |
| アクション演出 | action-performance.md (241) | actionData の演出欄(+0x1C〜)、directData(20B)、directDataAddEffect(8B)、effectData(48B)、エフェクトアーカイブ、Panana での扱い |
| モンスターの動き | monster-motion.md (161) | アニメ表・再生・スキニング・図鑑/戦闘表示 |
| アイテム効果 | item-effects.md (111) | 道具・装備の効果欄、状態の値の合わせ方、ドロップ率 |
| マップ構造 | map.md (365) | マップ DB、マップ→区画の表、区画 0(タイル)・3(出入口/階段/ワープ)・4/5/8・7(扉)、mapParts/mapData、EventObject との関係(§6)、宝箱(§9)、自作マップの要件(§7) |
| 新マップ追加 | new-map.md (190) | code.ips で区画表・ダンジョン表を拡張する設計、マップ数依存のセーブ/配列、RomFS の hash 表、1 枚に要るもの、リスク |
| ワールドマップ | worldmap.md (95) | 区画・地形・入口・座標・エンカウント範囲 |
| エンカウントと BGM | encounters.md (86) | 区画 6、monsterGroup(144行×0x2E)、BGM/SE、決まった敵(monsterFixGroup) |
| イベント/ギミックの仕組み | events.md (260) | EventObject の流れ・状態・欄(§1-3)、種類 +0x4D(§4)、スクリプト 種類 0x24(§5)、看板メッセージ(§6)、汎用スイッチ MOD(§7)、ボス戦 種類 0x31(§8) |
| イベント一覧の作り方 | event-list.md (137) | Panana でのイベント一覧: データだけで出せる範囲、0x24 の振り分けと ARM 実行器、クラスからメッセージ/完了行を拾う、出現条件(§4) |
| 精霊ほこら | shrine.md (152) | さよなら/呼び戻し、記録構造、QR 個体、修正案(code.ips) |
| マップエディタ設計 | map-editor-design.md (182) | ブラウザ実装、RomFS 処理、CGFX、マップデータ操作 |

## RPG3 (oahu/)
RPG3 (内部名 oahu、タイトル 00040000000EF000) の解析は `oahu/` にまとめる。ルートの各 md は RPG2 (kahara) 専用。

| 話題 | ファイル | 内容 |
|---|---|---|
| ROM・全体 | oahu/analysis.md | ROM 情報、展開手順、Base + Update のマージ (`rom:` / `patch:`、patchList.bin、LayeredFS)、RomFS とアーカイブ (version 7)、master `21350000` のテーブル一覧、GMSG の ID 範囲、分かった欄、code.bin のアドレス、RPG2 との違い |
| Panana 両対応 | oahu/panana-compat.md | 2 / 3 で共通の層と作り直す層、分け方の案、要検討の点 |
| ツール | oahu/tools/*.py | ctr.py (CIA 展開・マージ)、gsarc.py、gsmb.py、armdis.py。ROM 本体はリポジトリに入れない |

## データ表（reference/）

| データ | ファイル (行) | 列・キー |
|---|---|---|
| アクション | reference/actions.md (680) | # / カテゴリ / 種別 / 範囲 / 属性 / 状態(+0x32) / 量 / +0x16 / 威力 / 場面 / メッセージ。行番号 = actionData 行 |
| 状態 | reference/conditions.md (101) | ID(0x..) / 名前 / 範囲 / 値 / 動けない行動 / +0x32〜0x34 |
| モンスター | reference/monsters.md (198) | 行 / 種族 / Lv / HP〜すばやさ(最小〜最大) / ドロップ / ワザ / 耐性 / ボス / AI |
| アイテム | reference/items.md (629) | ID(=行番号) / 名前 / 分類 / ☆ / 買値 / 売値 / フラグ / アクション / 上限 / 販売店 |
| 装備効果 | reference/equipment.md (292) | ID / 名前 / 欄(首など) / ☆ / 効果1・2(状態ID付き) |
| 店 | reference/shops.md (520) | `## 店 N` 見出しごとに ID/名前/買値/売値 |
| 宝箱 | reference/treasures.md (617) | マップ / セル / イベント行 / フラグ / treasureGroup / 中身(重み) |
| ダンジョン | reference/dungeons.md (535) | ID / 名前 / コード(D01〜) / フラグ / テレポーター / ワープ記録枠 / マップ数 |
| マップ | reference/maps.md (213) | マップ名(D01B01001) / ハッシュ / ダンジョン / 階 / タイル / 範囲 / タイルセット |
| イベント実データ | reference/events.md (1780) | `## N ダンジョン名 (ハッシュ)` が 57 節。行 / 種類 / 枠 / モデル / メッセージ / 参照 |
| スクリプト結果 | reference/scripts.md (641) | 種類 0x24 の行 → 振り分け / クラス / 処理 / 完了 / メッセージ (v1.1.0: 393 行) |

## 大きいファイルの引き方
- reference/events.md: `grep -n '^## ' reference/events.md` でダンジョンの開始行を取り、次の見出しまでを Read。マップ名(例 D01B02001)は `grep -n` で行を特定。
- reference/actions.md / items.md: ID・名前を `grep -n` で直接引く。全文読みは不要。
- reference/scripts.md, treasures.md, shops.md: ダンジョン名・マップ名・`## 店 N` で引く。
- analysis.md: 節が多いので `grep -n '^#'` してから該当節のみ。

## 役割の分担（重なって見えるが別物）
- events.md = ゲームの仕組み / event-list.md = Panana 実装 / reference/events.md = 実データ / reference/scripts.md = 0x24 の解析結果。どれも 0x24 スクリプトに触れるので、仕組みは events.md §5、実装は event-list.md §3、個別の値は reference/scripts.md を見る。
- battle.md §8 は actionData の効果側、action-performance.md は演出側の欄。両方を参照する話題は actionData 全体。
- map.md §1-2 と new-map.md §1 はマップ表の読み取りを両方が説明する（new-map は拡張視点）。読み取りの仕様は map.md を正とする。
- 本ドラフトは見出しと reference の冒頭で作成。各節の細部の重複有無は未検証。

## 主な参照関係
- reference/* の解説元: actions/monsters/conditions → battle.md、items/equipment → analysis.md / item-effects.md、maps/dungeons → map.md、events/scripts → events.md / event-list.md、shops → analysis.md(Shop テーブル)
- battle.md ↔ action-performance.md（actionData）、item-effects.md（装備反映）
- encounters.md → map.md（区画 6）、events.md §8（ボス戦）／worldmap.md → map.md、encounters.md
- new-map.md → map.md（表構造）／monster-motion.md → reference/monsters.md、reference/actions.md
