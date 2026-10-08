# 電波人間のRPG3 (oahu) 解析メモ

RPG2 ([kahara](../kahara/README.md)) のドキュメント と同じ書き方で、RPG3 の ROM を調べた結果をまとめる。RPG2 と比べた違いは各節の「RPG2 との違い」と §8 にまとめた。Panana の 2/3 両対応の検討は [Panana連携の検討記録](../integrations/panana/panana-compat.md)。

対象は日本版 Base v0 + Update v4096。アドレスは特記がなければ Update の展開済み `code.bin`（base `0x100000`）。今回の再確認範囲は [検証記録](../roms/verification.md)。

## 1. ROM 基本情報

タイトル ID・版・ExHeader・セクション配置は [ROM 識別](../roms/oahu.md) を参照。

## 2. 展開手順

[CIA の展開・マージ](../roms/oahu.md#2-展開手順) と [同梱ツール](../roms/README.md) を参照。コマンドはリポジトリルートから実行する。

## 3. Base と Update のマージ

[ゲームによる差分選択と配布方式](../roms/oahu-update.md#ゲームによる差分選択と配布方式) に移設した。`patchList.bin` の11アーカイブは Update を使い、`code.bin` も Update を基準にする。旧 §3.1〜§3.3 の関数・表・配布方式は移設先に保全している。

## 4. RomFS

### 4.1 ルートの構成
- ルートのファイル 176 個は 8 桁 16 進のハッシュ名。**下位 16 ビットが必ず 0** (例 `21350000`)。ほかに `sound/` (sound.bcsar、stream/ の BGM 56 曲 .bcstm、voice/ の音声合成データ)、`shaders/`、`proctex_files/` (水・溶岩などのプロシージャルテクスチャ) がある。
- **RPG2 との違い**: RPG2 のルートは 32 ビットのハッシュ (`56562135` など)。RPG3 の名前は **RPG2 のハッシュの下位 16 ビットを上に寄せたもの**になっている。master: RPG2 `56562135` → RPG3 `21350000`、MessageCommand の 4 アーカイブ: RPG2 `1D37838B / 49A43B63 / 91B0619D / BACF5819` → RPG3 `838B0000 / 3B630000 / 619D0000 / 58190000`。

### 4.2 アーカイブの形式 (確定)
RPG2 の形式 ([kahara/romfs.md](../kahara/romfs.md)) とヘッダー・エントリの並びは同じ。違いは version と +0x14 の値だけ。

| off | 型 | 内容 |
|---|---|---|
| 0x00 | u32 | version = **7** (RPG2 は 5) |
| 0x04 | u32 | アーカイブハッシュ (= ファイル名) |
| 0x08 | u32 | エントリ数 |
| 0x0C | 28B × n | `hash, type, size, offset, comp, unk, raw_size`。unk は **1** (RPG2 は −1) |

- comp 1 = 1 ファイル入り ZIP (元のファイル名入り)、comp 6 = LZ10、0 = 無圧縮。RPG2 と同じ。
- エントリのハッシュは下位 8 ビットが 0。**同じ名前のファイルはハッシュも RPG2 と同じ** (例 MessageSystemCommon_JP.gsmb = `49607C00`、両作で一致)。
- 種類 (type) と中身 (Update 適用後の全アーカイブで、先頭のマジックから分類):

| type | 中身 | RPG2 との違い |
|---|---|---|
| 0 | 生のバイナリ (flagData 系、vendor.bin、W01_ground.bin など) / ctpk / nftr | |
| 1 | フォント (nftr / bcfnt)、パレット (.act) | |
| 2 | **BCH (H3D)** のモデル・テクスチャ (2468 個。マップ・ギミック・町・モンスター (`enemy_03`)・電波人間の顔・家具・魚・カメラなど) | RPG2 の type 2 は CGFX。**モデルの形式が変わった** |
| 3 | CGFX (1155 個。ほぼ戦闘などのエフェクト `fx_*` / `tx_fx_*`。822 個が A4070000) | RPG2 のエフェクト (`8756A407`) と同じ系統 |
| 4 | darc (レイアウト .arc) | |
| 5 | シェーダー (.bch / .shbin) | |
| 6 | GMSG (.gsmb) | 同じ |
| 8 | 0x180 バイトのヘッダー + **BCH** (666 個中 646 個。マップのパーツと推定。残り 20 個はヘッダーの長さが違う) | RPG2 のマップの t8.bin は 0x180 + CGFX |
| 9 | GS テーブル (.bin) | 同じ |
| 10 | BCH (master に 125 個) | |

- 3D モデルは **BCH** (Nintendo の H3D 形式。SPICA / Ohana3DS が対応)、エフェクトは CGFX。

### 4.3 master アーカイブ `21350000` (288 エントリ、Update で差し替え)
RPG2 の `56562135` に当たる。GS テーブル (type 9 / 0) 92 個、GMSG 3 個、フォント、共通レイアウトなど。主な GS テーブル (行数 × 行サイズ。RPG2 の値は [kahara/items.md](../kahara/items.md) / [kahara/battle.md](../kahara/battle.md) などから):

| テーブル | RPG3 | RPG2 |
|---|---|---|
| itemData.bin | 1191 × 0x40 | 713 × 0x30 |
| actionData.bin | 1126 × 0x30 | 672 × 0x3C |
| monsterParameter.bin | 201 × 0x70 | 185 × 0x54 |
| conditionData.bin | 125 × 0x3C | 94 件 |
| monsterGroup.bin | 190 × 0x3E | 144 × 0x2E |
| treasureGroup.bin | 283 × 0x50 | |
| mapGroup.bin (テーブル名 "D10") | 89 × 0x34 | |
| mapData.bin | 167 × 0x7 (+ 追加領域 0x4E0) | |
| mapObject.bin | 510 × 0x38 | |
| levelData.bin | 199 × 0x5C | |
| soundData.bin | 597 × 0xC | 418 × 0xC ([sound.md](sound.md)) |
| flagData.bin | 259 × 0x10 | |
| vendor.bin | (type 0、64488 B) | (type 0) |

- ほかに RPG3 で増えたもの: 釣り (`fishData` / `fishingHook` / `fishingPoint` / `fishingRod` / `fishingLevel`)、植物 (`plantInfo` / `plantMap` / `plantPoint`)、なごみ (`nagomiHouseList` / `nagomiCatchList` / `nagomiTownList`)、電波人間の作成 (`createSelect*` 16 個)、`denpaCustom`、`reBossInfo`、`insideInterior`、`designedMap` など。
- `flagData.bin` はセーブの値の定義表 (行 = キー、ビット数と要素の数)。ストーリーの進行度 (キー 0x74) とナビの表 `mapNavi.bin` は [story.md](story.md)。
- `flagDataHonolulu.bin` (87 × 0x10) / `flagDatakahara.bin` (150 × 0x10) と、それぞれの `flagDataLevel*`: 前作 (honolulu) と RPG2 (kahara) の、名前付きのフラグ表。前作のセーブとの連動に使うと推定 (未確認)。
- GS テーブルのヘッダー ([共通 GS テーブル形式](../common/formats.md#gs-テーブル)) は同じ (+0x00 行数、+0x04 行サイズ、+0x10 データ開始、+0x30 テーブル名)。+0x20 が 0 でないテーブル (mapData、treasureGroup、monsterGroup など) は、行の後ろに追加の領域がある (中身は未解析)。
- **行の中身は RPG2 と違う。** 欄の並びは作り直し (§6)。

### 4.4 マップ・イベントのアーカイブ
- ダンジョン・町ごとに 2 エントリのアーカイブ (`d10_EventObject.bin` + `d10_StaticEvent.bin` など) が 82 組ある。接頭辞: d10〜d90、e01〜e03、f20〜f92、h01、i01〜i24、k01〜k03、m10〜m90、s11〜s70、w01。
- EventObject は **0x58 バイト** (RPG2 は 0x50)。StaticEvent は 4 バイト × n。
- マップ DB (`B68E0000` / `A2C14C00`)、マップ表 (`B68E0000` / `5405E800`)、区画と EventObject の欄は [map.md](map.md)。
- ワールドマップ: master の `W01_ground.bin` (type 0) と `worldmapParts` / `worldmapPort`。

## 5. メッセージ (GMSG)
形式は RPG2 と同じ ([共通 GMSG 形式](../common/formats.md#gmsg-メッセージ): ヘッダー、ID 範囲、オフセット表、種別コード 1 文字 + 本文 + 0x0000)。違いは ID の振り方とタグ番号。

| ファイル | ID (本文) | 入っているアーカイブ |
|---|---|---|
| MessageSystemCommon_JP | 0–8657 | 21350000 |
| MessageBattle_JP | 30000–31282 | 21350000 |
| MessageField_JP | 40000–42678 | A9DF0000 |
| MessageNagomi_JP | 60000–61471 | 6E380000 |
| MessageAntenna_JP | 70000–70631 | 00910000 |
| MessageCommand_JP | 80000–80502 | 3B630000 / 58190000 / 619D0000 / 838B0000 |
| MessageStaffroll_JP | 90000–90137 | D94C0000 |
| MessageCodeFilter_JP | 100000–100014 | 91470000 |
| MessageEvent_JP | 空 (last = 0xFFFFFFFF) | 838B0000 |

- `_IN` (読み) は SystemCommon / Event / Field / Nagomi / Antenna にある。
- **RPG2 との違い**: ID は 10000 刻みの区切りから始まる (RPG2 は詰めて通し番号)。ファイルの間に大きな空きがあるので、MOD でメッセージを足すときは各ファイルの末尾を伸ばすだけで ID がぶつからない (検索の規則が RPG2 と同じなら。未確認)。
- 漢字にルビが付く。ルビのタグは **0x2B 親字 0x2C よみ 0x2D** (RPG2 は 0x27 / 0x28 / 0x29)。名前などの差し込みタグ (0x104 / 0x106 / 0x10D など) は番号が RPG2 と近いが、対応は未確認。
- **別のメッセージの差し込みは `0x0002 0x002A ID 0x0000`** (確定。RPG2 は `0x0002 0x0026 ID 0x0000`)。ナビの見出し ([story.md](story.md) §1) の多くが場所の名前 (MessageSystemCommon_JP) をこれで差し込む。RPG2 の 0x26 のまま読むと、`*` (0x2A) と ID の文字が本文に混ざって見える。

## 6. GS テーブルの欄 (分かった範囲)

### itemData.bin (1191 × 0x40、ID = 行番号)
| off | 型 | 内容 |
|---|---|---|
| 0x00 | u32 | 買値 |
| 0x04 | u32 | 売値 |
| 0x08 / 0x0C | u32 | 未確認 (0x1A0/0x1A1、数値) |
| 0x10 | u32 | フラグ (0xA0xxxxxx。RPG2 の +0x08 に当たると推定) |
| 0x14 | u32 | 名前 (例 0x4B2「キズぐすり」) |
| 0x18 | u32 | 説明 (メニュー用と推定) |
| 0x1C〜0x24 | u32 × 3 | 説明 (口調違い。RPG2 の +0x14〜+0x1C に当たると推定) |
| 0x28 | u32 | リソースハッシュ |
| 0x30 | u16 × 2 | 並びの番号 (推定) |
| 0x34 | u32 | アクションの行 (道具。例 キズぐすり = 0x10B) |

### actionData.bin (1126 × 0x30)
- +0x00 ビットフィールド、+0x08 名前、+0x0C 以降に使ったとき・結果のメッセージ (MessageBattle の 30000 台)。RPG2 (0x3C) より 12 バイト短く、並びが違う。
- 欄の全体と、系統 (+0x2C) ごとの +0x18 / +0x1A の意味は [actions.md](actions.md)。

### monsterParameter.bin (201 × 0x70)
- RPG2 と同じくビット詰め。+0x40 = 名前 (例 行 1「はなもぐら」)、+0x44 = 説明。RPG2 では名前は別アーカイブの MonsterDesign にあったが、RPG3 では MonsterParameter が直接メッセージ ID を持つ。

### ShopItem・Shop (店)
- `3B630000` と `E3C10000` に同じ中身で入っている。ShopItem は 782 × 0x10 (RPG2 の 8 バイトにジュエルの値段と「1 回だけ」の番号が増えた)、Shop は 44 × 0x38 (部屋のモデル・店員・支払いの種類)。詳しくは [shops.md](shops.md)。

### conditionData.bin (125 × 0x3C)
- +0x00 リソースハッシュ (アイコンと推定)、+0x0C 以降に「しかし どくにはならなかった」などのメッセージ。

## 7. code.bin (Update, v4096)
| アドレス | 内容 |
|---|---|
| `0x5A59DC` | リソース管理のポインタ (+0x80 / +0x84 = patchList) |
| `FUN_0011ad1c` | ルートファイルのパス (`rom:/` か `patch:/`) を作る ([差分選択](../roms/oahu-update.md)) |
| `FUN_002cb430` | `patch:/patchList.bin` を読む |
| `FUN_002cb4d0` | ハッシュでアーカイブを開く (起動時に `0x21350000` = master を開く、`FUN_00495fd0` 内) |
| `FUN_00495fd0` | 起動時の初期化 (patchList → master の読み込み) |
| `0x5A5A00` / `0x5A5A1E` | `L"rom:/XXXXXXXX"` / `L"patch:/XXXXXXXX"` のバッファ |

- master の表は、マスター (`*0x59F200`) の中の 0x1C バイトの読み手で引く。表 → 読み手のオフセットは `FUN_001D9BBC` で決まる (一覧は [master-readers.md](master-readers.md))。
- RPG2 と同じエンジン (アーカイブ・GS テーブル・GMSG の形式とエントリハッシュが共通) だが、**アドレスは全部別**。RPG2 の `FUN_` 名は使えない。
- Base と Update でもアドレスが少しずれている (例: パスを作る関数 Base `0x11ACEC` / Update `0x11AD1C`、text が 0x1C08 増えた)。

## 8. RPG2 との違い (まとめ)
| 項目 | RPG2 (kahara) | RPG3 (oahu) |
|---|---|---|
| 配布 | CIA 1 本 (v1.1.0 は全部入り) | Base + Update (Update の RomFS は差分、`patch:`) |
| ルートの名前 | 32 ビットハッシュ | 下位 16 ビット << 16 |
| アーカイブ | version 5、unk = −1 | version 7、unk = 1 (並びは同じ) |
| エントリのハッシュ | 同じ名前なら同じ値 | |
| GS テーブル / GMSG の入れ物 | 同じ | 同じ |
| 行の中身 | | サイズも並びも違う (§4.3、§6) |
| メッセージ ID | 通し番号 | 10000 刻みの区切り |
| ルビのタグ | 0x27〜0x29 | 0x2B〜0x2D |
| 3D モデル | CGFX | BCH (H3D)。エフェクトだけ CGFX |
| EventObject | 0x50 | 0x58 |

## 9. 未解析
- 各 GS テーブルの欄 (§6 は一部だけ)、vendor.bin。マップの区画と mapParts・type 8 のヘッダーは [map.md](map.md) (残りは同 §7)。
- type 10 の BCH の中身。
- メッセージのタグの全体 (`0x2B〜0x2D` 以外)。
- flagDataHonolulu / kahara の用途。
- マージ方法 B / C の実機・Azahar での動作確認。
