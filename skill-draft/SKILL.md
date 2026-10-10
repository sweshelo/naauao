---
name: naauao-docs
description: 電波人間のRPG2 (kahara, 1.1.0)、RPG3 (oahu, Update v4096)、RPG FREE! (lanai, Update v17408) のROM解析仕様を必要な範囲だけ検索する。マップ、イベント、戦闘、アイテム、装備、音、ストーリー、GS形式、ROM展開、MODの制約、FREE!のコンテンツ・チェックイン・コード入力・スタミナの確認に使う。
---

# naauao の検索ルーティング

## 最初に決めること

1. 作品と版を特定する。RPG2 = `kahara` / TitleVersion 1040、RPG3 = `oahu` / Base v0 + Update v4096、RPG FREE! = `lanai` / Base v0 + Update v17408。ファイル名の版ではなくTMDを確認する。未指定なら依頼・入力から特定し、別作品の値を補完に使わない。
2. ゲーム仕様・個別データ・ROM操作・Panana実装のどれが必要かを決める。
3. 下表から1〜2文書を選び、`rg -n '^#{1,4} ' <file>` で見出しを取り、該当節だけ読む。大きな表を全文ロードしない。

以下のパスは **naauaoのルート基準**。このファイルは `skill-draft/` にある。Pananaのサブモジュールなら `<panana>/docs/` をnaauaoルートに読み替える。参照リンクはこのSKILL.mdからの相対パス。

## ルーティング

| 話題 | Kahara | Oahu / 共通 |
|---|---|---|
| 入口・版の識別 | [kahara/README.md](../kahara/README.md)、[roms/kahara.md](../roms/kahara.md) | [oahu/README.md](../oahu/README.md)、[roms/oahu.md](../roms/oahu.md) |
| CIA展開・更新・書き出し | [roms/README.md](../roms/README.md) | [roms/oahu-update.md](../roms/oahu-update.md) |
| GSアーカイブ / GSテーブル / GMSG | [common/formats.md](../common/formats.md)、[kahara/romfs.md](../kahara/romfs.md) | [oahu/analysis.md](../oahu/analysis.md) §4–6 |
| アイテム / 装備 / 店 | [kahara/items.md](../kahara/items.md)、[kahara/item-effects.md](../kahara/item-effects.md)、[kahara/shops.md](../kahara/shops.md) | [oahu/analysis.md](../oahu/analysis.md) §6、[oahu/shops.md](../oahu/shops.md) |
| 戦闘 / AI / 状態 / アクション | [kahara/battle.md](../kahara/battle.md) | [oahu/actions.md](../oahu/actions.md) |
| 演出 / モーション | [kahara/action-performance.md](../kahara/action-performance.md)、[kahara/monster-motion.md](../kahara/monster-motion.md) | [oahu/map-models.md](../oahu/map-models.md)（マップモデル） |
| マップ / 区画 / モデル | [kahara/map.md](../kahara/map.md) | [oahu/map.md](../oahu/map.md)、[oahu/map-models.md](../oahu/map-models.md) |
| イベント / 宝箱 / 条件 / スクリプト | [kahara/events.md](../kahara/events.md)、[kahara/event-list.md](../kahara/event-list.md) | [oahu/events.md](../oahu/events.md) |
| 敵出現 / BGM / SE | [kahara/encounters.md](../kahara/encounters.md) | [oahu/events.md](../oahu/events.md)、[oahu/sound.md](../oahu/sound.md) |
| ワールドマップ / ワープ / 泉 | [kahara/worldmap.md](../kahara/worldmap.md)、[kahara/field.md](../kahara/field.md) | [oahu/map.md](../oahu/map.md) |
| セーブ / QR / ほこら | [kahara/save.md](../kahara/save.md)、[kahara/shrine.md](../kahara/shrine.md) | [oahu/story.md](../oahu/story.md) |
| 物語 / ナビ / 段階 | — | [oahu/story.md](../oahu/story.md)、[oahu/reference/story-stages.md](../oahu/reference/story-stages.md) |
| マップ追加 / コード制約 | [kahara/new-map.md](../kahara/new-map.md)、[kahara/code.md](../kahara/code.md) | [oahu/master-readers.md](../oahu/master-readers.md)（表の読み手） |
| 個別ID・名称・データ一覧 | [kahara/reference/README.md](../kahara/reference/README.md) | Kaharaの表を代用しない |
| PananaのUI・実装履歴・独自拡張 | [integrations/panana/README.md](../integrations/panana/README.md) | 同左。ゲーム仕様を調べるだけなら読まない |

## Lanai (RPG FREE!) のルーティング

FREE! は表・メッセージ・アーカイブの形式が RPG2 / RPG3 と違う。Kahara / Oahu の表で補わない。

| 話題 | 文書 |
|---|---|
| 入口・版の識別・展開 | [lanai/README.md](../lanai/README.md)、[roms/lanai.md](../roms/lanai.md) |
| アーカイブ v10 / GS テーブルの新形式 / メッセージのタグ / master の一覧 | [lanai/analysis.md](../lanai/analysis.md) |
| コンテンツ (ステージ・シナリオ) / CRO・CRR / MapStage | [lanai/contents.md](../lanai/contents.md) |
| スタミナ | [lanai/stamina.md](../lanai/stamina.md) |
| チェックイン / サーバーとの通信 / 配信の表 / オフラインモード | [lanai/checkin.md](../lanai/checkin.md) |
| コード入力 / サポートのコード | [lanai/codes.md](../lanai/codes.md) |
| モンスターの表とモデル | [lanai/monsters.md](../lanai/monsters.md) |

## 検索例

```sh
rg -n '^## ' kahara/reference/events.md
rg -n 'D01B02001' kahara/reference/events.md
rg -n 'キズぐすり' kahara/reference/items.md
rg -n '^#{1,4} ' oahu/story.md
sed -n '20,65p' oahu/story.md
```

`reference/events.md` はダンジョン→マップ→行、`shops.md` は店ID、`scripts.md` は種類0x24の個別行から絞る。実際に検索した行範囲を使い、索引に書いた固定行数に依存しない。

## 根拠の扱い

- `FUN_xxxxxxxx` は指定版の仮想アドレス。RPG3はBaseとUpdateでも異なる。
- 「確定」は元の解析が確認した範囲。推定・未確認・提案と区別し、今回再検証した範囲は [roms/verification.md](../roms/verification.md) を見る。
- 共通ヘッダーから行のフィールドまで共通と推測しない。作品・版・オフセットを回答に添える。
- 生成済み表の生成器は本リポジトリに揃っていない。外部 `tools/` を同梱 `roms/tools/` と混同しない。
- Pananaの過去の「未実装」をゲーム仕様の未解析と読み替えない。拡張イベント0x30/0x31やPNMPは対応パッチを前提にする。
- 曖昧な記述は [再編・検証記録](../common/reorganization.md) と両方の根拠を確認する。未確認の解釈を事実として補わない。
- ROMの取得先・認証・復号情報はリポジトリへ記録しない。
