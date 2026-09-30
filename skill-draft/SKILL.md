---
name: naauao-docs
description: 電波人間RPG2 v1.1.0 ゲーム仕様・データ構造・実装ガイド。マップ・バトル・イベント・アイテム等の編集・MOD開発向け
---

# naauao ゲーム仕様インデックス

## 根本設計ドキュメント (実装ガイド)

| トピック | ファイル | 要点 |
|---------|--------|-----|
| **基本情報** | analysis.md (436行) | ROM構造、RomFS・アーカイブ、GS テーブル形式。†grep ^# |
| **戦闘** | battle.md (357行) | MonsterParameter・状態・AI・ダメージ計算・ボス変身。†grep ^# |
| **アクション演出** | action-performance.md (241行) | actionData・directData・effectData・SE・モーション。†grep ^# |
| **マップ** | map.md (365行) | マップDB・タイル・区画・座標・出入口・タイルセット |
| **敵出現・BGM** | encounters.md (86行) | monsterGroup・エンカウント枠・区画6・BGM・決まった敵 |
| **イベント・ギミック** | events.md (260行) | EventObject種類・状態・スクリプト(0x24)・汎用スイッチMOD・ボス戦MOD |
| **イベント一覧作成** | event-list.md (137行) | Panana実装：ARM実行器・スクリプト振分け・メッセージ抽出・出現条件 |
| **アイテム効果** | item-effects.md (111行) | 道具・装備の効果欄、状態の値合わせ方(6種類)、ドロップ率計算 |
| **ワールドマップ** | worldmap.md (95行) | 区画・地形・入口・座標・エンカウント範囲 |
| **モーション** | monster-motion.md (161行) | アニメ表・再生・スキニング・ミュージアム・戦闘表示 |
| **精霊ほこら** | shrine.md (152行) | さよなら・呼び戻し・記録構造・QR個体・修正案(code.ips) |
| **新マップ追加** | new-map.md (190行) | code.ips方式、区画表・ダンジョン表の拡張、マップDB索引 |
| **マップエディタ設計** | map-editor-design.md (182行) | ブラウザ実装、RomFS処理、CGFX、マップデータ操作 |

## データ参照テーブル (reference/)

| データ | ファイル | 行数 | キー |
|------|--------|------|-----|
| アクション全一覧 | reference/actions.md | 680 | 672行×効果・威力・メッセージ。†grep ^# |
| モンスター全一覧 | reference/monsters.md | 198 | 185行×能力・耐性・ワザ・AI・ボス情報 |
| 装備の効果 | reference/equipment.md | 292 | 284行×欄・効果・状態値 |
| アイテム | reference/items.md | 629 | ID→名前・分類・アクション行・販売店 |
| 条件(状態) | reference/conditions.md | 101 | 94行×範囲・値・効果式 |
| マップ | reference/maps.md | 213 | 205マップ×タイル数・区画サイズ |
| ダンジョン | reference/dungeons.md | 535 | ダンジョンID→マップハッシュ・テレポート・名前 |
| イベント実データ | reference/events.md | 1780 | 全EventObject行、ダンジョン別。†grep ^## |
| スクリプト実行結果 | reference/scripts.md | 641 | 種類0x24の行→クラス・メッセージ・完了行 |
| 宝箱 | reference/treasures.md | 617 | マップ×宝箱→treasureGroup・中身 |
| 店舗 | reference/shops.md | 520 | 店ID→品揃え |

## 重複・問題箇所

- **イベント: 3ファイルの役割重複**
  - event-list.md: Panana での実装 (ARM実行器)
  - events.md: ゲーム仕組み (EventObject・スクリプト構造)
  - reference/events.md: 実データ (全1375行)
  - **問題**: 種類0x24・出現条件の説明が event-list.md §3・4 と events.md §5・5 に重複
  
- **アクション**: action-performance.md と battle.md で actionData の構造が部分的に重複
- **マップ表**: map.md と new-map.md で区画表・ダンジョン表の読み込み処理が重複

## 相互参照

- battle.md ← action-performance.md (actionData効果)、item-effects.md (装備反映)
- events.md ← encounter.md (§5 決まった敵)、event-list.md (§3 振分け実装)
- worldmap.md → map.md (区画)、encounters.md (敵範囲)
- monster-motion.md → reference/monsters.md (MonsterDesign)
- new-map.md → map.md (テーブル構造)

## 大規模ファイルの読み方

| ファイル | 行数 | 推奨方法 |
|---------|------|--------|
| reference/events.md | 1780 | `grep ^##` で見出し取得、必要なダンジョンのセクションを読む |
| reference/actions.md | 680 | `grep ^#` で見出し、または表の範囲指定読み取り |
| reference/scripts.md | 641 | ダンジョン別見出しで検索後、行範囲を指定読み取り |
| reference/treasures.md | 617 | マップ別見出しを検索 |
| battle.md | 357 | §ごとに読み取り (§2〜§4 MonsterParameter 詳細) |
| analysis.md | 436 | セクション別に参照 (§ ROM情報、§ RomFS、§ GS テーブル) |

