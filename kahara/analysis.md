# 電波人間のRPG2 (kahara) 解析案内

対象は日本版 Title ID `00040000000A7900`、TitleVersion 1040 (1.1.0)。旧ルート `analysis.md` を主題別に分割した。ここに記載するテーブル行・メッセージ ID・仮想アドレスは kahara 用であり、RPG3 には流用しない。

| 調べたい内容 | 文書 |
|---|---|
| ROM の識別・展開・Luma への配置 | [roms/kahara.md](../roms/kahara.md) |
| GS アーカイブ・GS テーブル・GMSG の共通ヘッダー | [common/formats.md](../common/formats.md) |
| ルートアーカイブと master | [romfs.md](romfs.md) |
| itemData・アイテム使用・追加時の制約 | [items.md](items.md) |
| GMSG の ID 範囲・制御コード・タグ | [messages.md](messages.md) |
| ShopItem・Shop・商品説明 | [shops.md](shops.md) |
| セーブ変数・origin・QR・さよなら | [save.md](save.md) |
| 泉・ワープホール・テレポーター | [field.md](field.md) |
| code.bin の主要関数・アイテム走査 | [code.md](code.md) |
| Panana の MOD・パッチ・ビルド・検証履歴 | [integrations/panana/analysis.md](../integrations/panana/analysis.md) |

## リファレンス表

生成元は旧作業環境の `tools/gen_reference.py` 等。本リポジトリには含まれず、今回照合した Panana コミットにも `tools/` はないため、現在の所在は未確認。本リポジトリだけでは再生成できない。
- [reference/dungeons.md](reference/dungeons.md): ダンジョン ID (var 0x4F) → 名前・コード・テレポーター可否・ワープ記録枠、各マップのハッシュ (var 0x50/0x61) と階
- [reference/items.md](reference/items.md): バニラのアイテム ID → 名前・分類・☆・価格・アクション行・上限・販売店
- [reference/shops.md](reference/shops.md): 店 ID → 品揃え (ID・名前・買値・売値の表)
- [reference/monsters.md](reference/monsters.md): MonsterParameter (ビット詰め) を展開した一覧: 名前・Lv・HP・こうげき・ぼうぎょ・すばやさ・経験値・ゴールド・ドロップ・ワザ・耐性。名前は別アーカイブ 2713402F の MonsterDesign (+0x4C の行、+0 名前 / +4 説明)。実行時はマスター (*0x520448) の +0x94C が MonsterParameter、+0x914 が MonsterDesign
- [reference/actions.md](reference/actions.md): 全アクション (ワザ・アイテム・モンスターの行動・セリフ) のカテゴリ・種別・範囲・属性・状態・量・メッセージ
- [reference/conditions.md](reference/conditions.md): 状態 94 件の名前・範囲・値
- [reference/equipment.md](reference/equipment.md): 装備 284 件の欄・☆・効果 (状態と値)。仕組みは [item-effects.md](item-effects.md)
- 戦闘の仕組み (ボスの変身・セリフ・AI・ダメージ計算・状態): [battle.md](battle.md)
- [reference/maps.md](reference/maps.md): 全 205 マップのタイル数・範囲・タイルセット・区画のサイズ
- [reference/treasures.md](reference/treasures.md): 全マップの宝箱の中身 (区画 4 → EventObject +0x08 → treasureGroup)。ダンジョン名は mapGroup +0x14 の u16 ([map.md](map.md) §10)
- マップのデータ構造 (マップ DB、タイル、出入口、タイルセットとモデル): [map.md](map.md)、ダンプ `tools/mapdump.py`
- マップエディタ (ブラウザ、3D) の設計書: [Panana の設計](../integrations/panana/map-editor-design.md)
- イベント・ギミックの仕組み (種類、状態、スクリプト、汎用スイッチ MOD): [events.md](events.md)、一覧 [reference/events.md](reference/events.md)
- スクリプト (種類 0x24) の行ごとのクラス・メッセージ・完了させる行: [reference/scripts.md](reference/scripts.md)。Panana のイベント一覧の作り方: [実装メモ](../integrations/panana/event-list.md)
- 出現する敵 (区画 6 → monsterGroup) と BGM (mapData → soundData → sound.bcsar): [encounters.md](encounters.md)
