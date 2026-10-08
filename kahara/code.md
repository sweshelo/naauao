# 電波人間のRPG2 (kahara): code.bin の主要関数

対象: 日本版 Title ID `00040000000A7900`、TitleVersion 1040 (1.1.0)。アドレスは展開済み code.bin の仮想アドレス (base `0x100000`)。[解析案内](analysis.md) / [ROM の識別・展開](../roms/kahara.md)。

## code.bin の主要関数
| アドレス | 内容 |
|---|---|
| 0x002EDC14 | `GetItemRow(id)` 行数でバウンドチェック (テーブル依存) |
| 0x002EDB9C | 所持数取得 (key 0x26 + 0x27) |
| 0x002EDA24 | アイテムフラグ (key 0x70) |
| 0x002EDA90 | 所持上限チェック (+0x2F / 連鎖 +0x2A) |
| 0x00304ADC | セーブ変数読み出し |
| 0x003093B0 | アーカイブをハッシュで読み込み |
| 0x0041F400 | 起動時初期化 (マスターデータ 56562135 読み込み) |

### 全アイテム走査ループ (`cmp rN, #0x2C8` + bls/ble) — 26 箇所
```
1CCD3C 1CD1E4 1CD584 1FEF44 225680 225708 25FEDC 25FF80 266AB8 267E30
2C0B3C 2C64DC 2C6BE0 2CD5D4 2D2E14 2D2EB4 2D3094 2D3104 304134 35840C
3584AC 3586DC 35874C 35B568 35B680 35C1F8
```
(仮想アドレス。code.bin オフセット = アドレス − 0x100000)
すべて `E35x0FB2` (cmp rN,#0x2C8)。テーブルを 749 行に拡張する場合は `E35x0FBB` (#0x2EC) に書き換える。
(0x2ED は ARM 即値で表現不可なので最大 ID は 748)

追加アイテムのパッチ例は [Panana 実装記録](../integrations/panana/analysis.md)。これらのアドレスを oahu に流用しないこと。
