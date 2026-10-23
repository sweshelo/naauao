# 戦闘の背景と BGM (RPG FREE!)

対象: Base v0 + Update v17408。アドレスは Update の code.bin (Ghidra と同じ 0x100000 起点)。表は master `2135000A` とコンテンツのアーカイブ ([contents.md](contents.md))。RPG3 の背景 (mapResource +0x10) と BGM (mapData [5]) の決め方は [RPG3 の音 §3.5](../oahu/sound.md) で、FREE! とは仕組みが違う (FREE! は**背景と BGM を 1 行で一緒に決める**)。

確度: **確定** = コードで読み方を確かめ、データとも合う / **推定** = コードかデータの片方だけ、または意味の解釈 / **未確認** = 値を見ただけ。ゲームを動かしての確認はしていない。

## 1. まとめ

| | 戦闘の背景 | 戦闘の BGM |
|---|---|---|
| ふつうの戦闘 (歩いてのエンカウント) | 群れ (MonsterGroup) の **+0x00** が指す BattleField の行の +0x00 / +0x04 | 同じ行の **+0x08** |
| ボス戦 (区画 8 種類 0 + 動作の型 0x8000000C) | 同じ (群れの +0x00) | 同じ |
| ワールドマップ | 足元の WorldmapParts の +0x08 (BattleField の行番号) | 同じ行の +0x08 |

- 群れの **+0x69 bit3** が 1 ならコンテンツの `BattleFieldContents`、0 なら master の `BattleField` から引く。
- モンスターごとの BGM・背景はない。

## 2. BattleField / BattleFieldContents (12 B / 行、確定)

| off | 型 | 内容 | 確度 |
|---|---|---|---|
| +0x00 | u32 | 背景のモデルのアーカイブ (`0x52120000` か `0xF0F40000`) | 確定 (データ) / モデルを読む関数は未特定 |
| +0x04 | u32 | そのアーカイブのエントリのハッシュ (`btmp_*.bch`、種別 4) | 確定 (データ) |
| +0x08 | u32 | **戦闘の BGM = SoundData の行番号** | **確定** (`FUN_002ED9F8` → `FUN_00473154`) |

- master `BattleField` (ホルダー master +0xFF0、表 +0xFF4): **26 行**、行 ID あり。
- コンテンツの `BattleFieldContents` (ホルダー +0x1018、表 +0x101C。読み込み済みかを `FUN_003106F8` で見る): 127 コンテンツにあり、1〜30 行。**ほとんどが 3 行 1 組で、同じ背景に BGM 2 / 3 / 4 (`BGM_BATTLE_NORMAL` / `BOSS` / `GOAL`)**。例外は BGM 5 (arena、9 件) と 731 / 732 (同じ曲の別の行、計 5 件)。行 ID は 0x80000001 から (0x80000000 の行はない)。
  - 例 (コンテンツ `59B00000`): 行 ID 80000001〜3 = ruinsB × BGM 2 / 3 / 4、80000007〜9 = caveB × 2 / 3 / 4。

### 2.1 背景のモデル (btmp)

エントリの名前は、エントリの 0x180 B のヘッダーにある UTF-16 のパス (`rom:/cg/model/map/map_parts/<名前>/<名前>.bch`)。

| アーカイブ | エントリ (ハッシュ 名前) |
|---|---|
| `52120000` (version 10、22 エントリ) | 8D63D000 btmp_01_caveA、A09DD800 btmp_02_caveB、1825D400 btmp_03_towerA、4BDEC000 btmp_04_forestA、8CA98400 btmp_05_volcanoA、3AFEFC00 btmp_06_ruinsA、580A4800 btmp_07_ruinsB、E76B3400 btmp_08_iceA、81EE5400 btmp_09_relic、560C5C00 btmp_10_temple、FEDF0C00 btmp_10_templeB、80B4F000 btmp_11_caveC、5B800400 btmp_11_opnforest、422CC400 btmp_12_flat、7FD5D400 btmp_13_sand、4B8F1400 btmp_14_sea、A08CFC00 btmp_15_arena、F8B91800 btmp_16_caveD、21306000 btmp_17_towerB、8A645000 btmp_18_hell、9212B800 btmp_19_snow、1125C400 btmp_20_snowfst |
| `F0F40000` (エフェクトのアーカイブ。末尾 8 件が btmp) | 57B86800 btmp_00_photo、0785FC00 btmp_04_forestB、F646FC00 btmp_04_forestB_n、81EE5400 btmp_09_relic、FEDF0C00 btmp_10_templeB、2FB36800 btmp_10_templeC、1125C400 btmp_20_snowfst、6A634800 btmp_21_rain |

### 2.2 master BattleField の全 26 行

| 行 | 行 ID | アーカイブ | 背景 | +0x08 (BGM) |
|---|---|---|---|---|
| 0 | 80000000 | 52120000 | btmp_01_caveA | 2 BGM_BATTLE_NORMAL |
| 1 | 80000001 | 52120000 | btmp_15_arena | 5 BGM_BATTLE_KAHARA |
| 2 | 80000016 | 52120000 | btmp_15_arena | 6 BGM_BATTLE_OAHU |
| 3 | 80000002 | 52120000 | btmp_14_sea | 2 |
| 4 | 80000003 | 52120000 | btmp_12_flat | 2 |
| 5 | 80000004 | 52120000 | btmp_11_opnforest | 2 |
| 6 | 80000005 | 52120000 | btmp_13_sand | 2 |
| 7 | 80000006 | 52120000 | btmp_19_snow | 2 |
| 8 | 80000007 | F0F40000 | btmp_20_snowfst | 2 |
| 9 | 80000008 | 52120000 | btmp_02_caveB | 2 |
| 10 | 80000009 | 52120000 | btmp_11_caveC | 2 |
| 11 | 8000000A | 52120000 | btmp_16_caveD | 2 |
| 12 | 8000000D | 52120000 | btmp_04_forestA | 2 |
| 13 | 80000010 | 52120000 | btmp_06_ruinsA | 2 |
| 14 | 80000011 | 52120000 | btmp_07_ruinsB | 2 |
| 15 | 80000012 | F0F40000 | btmp_09_relic | 2 |
| 16 | 80000013 | 52120000 | btmp_10_temple | 2 |
| 17 | 80000014 | F0F40000 | btmp_10_templeB | 2 |
| 18 | 8000000B | 52120000 | btmp_03_towerA | 2 |
| 19 | 8000000C | 52120000 | btmp_17_towerB | 2 |
| 20 | 80000015 | 52120000 | btmp_08_iceA | 2 |
| 21 | 8000000E | 52120000 | btmp_05_volcanoA | 2 |
| 22 | 8000000F | 52120000 | btmp_18_hell | 2 |
| 23 | 80000017 | 52120000 | btmp_15_arena | 676 BGM_BATTLE_HONOLULU |
| 24 | 80000018 | F0F40000 | btmp_21_rain | 2 |
| 25 | 80000019 | F0F40000 | btmp_00_photo | 2 |

## 3. 行を決める関数 (確定)

- **`FUN_002B4170(戦闘の状態, 種類, 行)`**: 種類を +0x119、BattleField の行を +0x114 に入れる。行が NULL のとき:

  | 種類 | 行 |
  |---|---|
  | 2 | master BattleField の行 2 (arena / BGM 6) |
  | 3 / 5 / 6 | 行 1 (arena / BGM 5) |
  | 4 | 行 0x17 (arena / BGM 676) |
  | 0 / 1 (既定) | 今の群れ (+0x110) の **+0x00** で引く。+0x69 bit3 = 0 なら master BattleField、1 ならコンテンツの BattleFieldContents (読み込まれていなければ引かない) |
  | それでも NULL | master BattleField の行 0 (caveA / BGM 2) |

- **`FUN_00269EB0(状態, 群れ)` / `FUN_004221BC(状態, 表, 行)`**: 群れの +0x69 bit3 で表を選び、+0x00 (または引数の行) を行 ID なら `FUN_001325DC` で番号にし、範囲外なら 0 にして行を引き、`FUN_002B4170` に渡す。
- **BGM は `FUN_002ED9F8(状態, BGM)`**: BGM が 0 なら `FUN_00473154` = +0x114 の行 (NULL なら BattleField の行 0) の **+0x08**。同じ曲が鳴っていれば鳴らし直さない (`FUN_002D76FC`)。鳴らすのは `FUN_002B3F9C` → `FUN_00319194(音のオブジェクト, SoundData の行, −1, 0)`。
  - 戦闘の初期化 `FUN_00178350` (`@0x17850C`) が `FUN_002ED9F8(状態, 0)` を呼ぶので、**最後に鳴るのは BattleField の行の +0x08** (経路の途中で別の曲を鳴らしても、戦闘が始まるとこれに変わる)。

### 3.1 経路ごと (確定)

| 経路 | 背景の行 (+0x114) | BGM |
|---|---|---|
| 歩いてのエンカウント `FUN_0020FA08` (`FUN_002103C8` から) | `FUN_00422D34` で群れを決めたあと `FUN_002B4170(状態, 0, NULL)` (`@0x20FBB0`) → **群れの +0x00** | `FUN_002ED9F8(状態, 0)` (`@0x20FBBC`) → 行の +0x08 |
| 同上、マップの種類 (`*(+0x7C)+1`) が 2 (ワールドマップと推定) | `FUN_004221BC(状態, 0, FUN_0045BB50(...))` (`@0x20FC48`): 足元の **WorldmapParts (master +0xFC8) の +0x08 = BattleField の行番号** (3 sea / 4 flat / 5 opnforest / 6 sand / 7 snow / 8 snowfst) | 同じ |
| もう 1 つのエンカウント `FUN_001DAB34` (`FUN_001DA29C` から。移動の演出のあと) | 変えない (マップに入ったときの値) | `@0x1DAD60`: MapData +0x06 を鳴らす → 戦闘の初期化で行の +0x08 に変わる |
| マップに入るとき `FUN_0021B37C` (`@0x21B5BC`〜`@0x21B608`) | MapData +0x0B の **MapResource の +0x10** が 0 でなければ `FUN_004221BC(状態, 1, +0x10)` (コンテンツの BattleFieldContents の行 ID)、0 なら `FUN_002B4170(状態, 0, NULL)` | − |
| 群れを指定する戦闘 `FUN_002E2828(群れ, BGM)` / `0x4548CC` / `0x454940` | `FUN_00269F84` + `FUN_00269EB0` → 群れの +0x00 | 引数 (0 なら行の +0x08) |
| `FUN_002A37D4(0 / 1 / 2)` (`@0x2A3838`〜) | 種類 2 / 3 / 4 (行 NULL → 上の表) | `FUN_002B3F9C(6 / 5 / 0x2A4)`。パーティを `FUN_00439DF8` / `FUN_0032E678` / `FUN_0047354C` から読むので対戦系と推定 |
| `0x4552F0` / `0x45557C` | 種類 6 (引数 < 0 なら master の行 1、そうでなければ BattleFieldContents の行) / 種類 5 | 0 → 行の +0x08 |

- `0x4548CC` / `0x454940` / `0x4552F0` / `0x45557C` は Ghidra が関数にしなかった所で、code.bin の中に呼び出しもポインタもない。**コンテンツの CRO (スクリプト) から呼ぶと推定**。BGM を引数で渡せるのはこの経路だけ。
- MapResource +0x10 の実データ: 388 行中 215 行が行 ID (全件その BattleFieldContents にある)、173 行が 0。歩いてのエンカウントは群れで引き直すので、MapResource +0x10 が効くのは `FUN_001DAB34` の経路など、群れで引き直さない戦闘 (推定)。
- MonsterGroup +0x69 のほかのビット: bit0 (`FUN_00473034`)、bit1 (`FUN_002F99FC`)、bit2 (`FUN_002F0894`) は戦闘の初期化でフラグ (+0x3A78A bit0) などに使う。**BGM・背景には使わない** (確定: 読み手を全部見た)。

### 3.2 MonsterGroup +0x00 が 0 / 0x80000000 のとき (確定)

- 表の検索 `FUN_0031C038` は、ID が見つからない・番号が範囲外のとき行 0 を返す。`FUN_00269EB0` / `FUN_004221BC` も `0x80000000` ちょうどは番号として扱い、範囲外 → 0。
  - **bit3 = 0**: master BattleField の行 0 = btmp_01_caveA + BGM 2 (`BGM_BATTLE_NORMAL`)。マップや MapData からは取らない。
  - **bit3 = 1**: そのコンテンツの BattleFieldContents の**行 0** (行 ID 0x80000000 の行はないので)。
- 実データ (127 コンテンツの MonsterGroup 871 行): bit3 = 1 かつ行 ID が 729 行 (うち 722 行はその BattleFieldContents にある。7 行はない → 行 0)、0x80000000 かつ bit3 = 0 が 142 行 (各コンテンツの行 0 の空の群れ 127 行を含む)、行 ID かつ bit3 = 0 が 1 行。値 0 の行はない。

## 4. ボス戦 (区画 8 種類 0 + 動作の型 0x8000000C)

[重要オブジェクト §1.1](key-objects.md) の戦闘。

- 区画 8 のハンドラ `CollisionEvent` (RTTI `14CollisionEvent`、vtable 0x4D3640) の vtable[4] = 動作の生成 **`FUN_0045B2D8`** が、型 0x8000000C で **`CollisionEncountCommon`** (RTTI `22CollisionEncountCommon`、vtable 0x4D63E8、コンストラクター `0x25AE64`) を作る。+0x0C = 引数 1 & 0xFFFF、+0x0E = 引数 2 & 0xFFFF、+0x10 / +0x14 / +0x18 = 引数 3 / 4 / 5。(確定)
- 範囲に入ったときの処理 (vtable[3] = `0x2E281C`) は **`FUN_002E2828(+0x0C, 0)`** だけ。群れ = コンテンツの MonsterGroup (+0x106C) の行 (引数 1 は番号でも ID でも引ける)、背景 = 群れの +0x00 と +0x69 bit3、BGM = 0 → その行の +0x08。(確定)
  - **ボス戦の BGM・背景は群れの +0x00 が指す BattleFieldContents の行で決まる**。ボスの群れは 3 行 1 組のうち BGM 3 (`BGM_BATTLE_BOSS`) の行を指すと推定 (組の形から。66 件の照合はしていない)。
- 勝ったときのフラグ (引数 2): vtable[4] (`0x25AE40`) が、+0x0E が 0 でなければ `FUN_002FF114(+0x0E, 2)` を呼ぶ。(コードは確定 / 戦闘のあとに呼ばれること、2 = 立てる、は推定)
- **引数 3〜5** (vtable[2] = `FUN_0025AD2C`): 0 でないものごとに `FUN_002AC740(引数)` でマップのキャラクターを探し、`FUN_002A3B1C(キャラ, 引数 2)` でそのキャラの +0xB4 に勝ちのフラグを入れ、`FUN_002AA598(キャラ, 群れ)` で群れの中からキャラの見た目 (MonsterDesign) と合うモンスターを探して `FUN_002A3A70` でモーションを再生する。→ **引数 3 = 戦闘と組になるマップのキャラクター (区画 5 のボスの姿) の番号**と推定 (流れは確定、何の通し番号かは未確認)。BGM・背景には関係しない (確定)。

## 5. SoundData (master、896 行 × 8 B)

| off | 型 | 内容 | 確度 |
|---|---|---|---|
| +0x00 | u32 | sound.bcsar のアイテム ID (`0x01nnnnnn`)。行 0 / 49 は 0 | 確定 (BGM の行。BCSAR の文字列で照合) |
| +0x04 | u8 | 種類らしき値: 3 = BGM (49 行)、2 = ME (24)、1 (8)、0 / 4 / 8 / 0x10 = 効果音 | 推定 |
| +0x05 | u8 | 0x1A (全行) | 未確認 |
| +0x06 | u16 | 0 (全行) | 未確認 |

- **BGM の行 (種類 3)**: 1 TITLE、2 BATTLE_NORMAL、3 BATTLE_BOSS、4 BATTLE_GOAL、5 BATTLE_KAHARA、6 BATTLE_OAHU、7 BATTLE_HONOLULU、8 / 9 (5 / 6 と同じ曲)、10 OLD_ANTENNA_OAHU、11〜16 MENU_* (CATCH / RESULT / MUSEUM / HOKORA / HOUSE / FUREAI)、17〜38 MAP_* (17 MY_ISLAND_OUT、18 MY_ISLAND_IN、19 WORLDMAP、20 SEA、21 VILLA_1、22 VILLA_2、23 HOME、24 FAIRY、25 SHOP、26 COLISEUM、27 CAVE_OAHU、28 EVIL、29 RUINS、30 TOWER、31 ICE、32 FOREST、33 SHINDEN、34 VOLCANO、35 PALACE、36 DARK、37 CAVE_KAHARA、38 MYSTIC)、39 EVENT_ELEGY、40 ENDING、41 / 42 FISHING_1 / 2、43〜48 OLD_* (DENPAISLAND_HONOLULU / KAHARA / OAHU、VILLA_TOKAI_OAHU、DESERT_OAHU、WORLDMAP_OAHU)、**676 BATTLE_HONOLULU**。名前の `BGM_` は省いた。
- 種類 1 の行 730 TITLE、731 BATTLE_NORMAL、732 BATTLE_BOSS、779 GOAL、780 HONOLULU、781 KAHARA も同じ BGM を指す (BattleFieldContents で 731 / 732、MapData +0x04 で 781 を使う)。種類 1 と 3 の違いは未確認。
- 行 50 以降に BGM のアイテム ID を種類 0 / 4 で持つ行がある (74〜87 など)。sound.bcsar の音は 686 個なのに SoundData は 0x01000359 まで指すので、**種類 0 / 4 / 8 / 0x10 の行の ID は sound.bcsar の番号とずれている可能性がある** (効果音の名前の対応は未確認)。BGM の欄で選ぶ候補は種類 3 (と 1) の行が安全。

## 6. マップの音 (MapData +0x04 / +0x06 / +0x08)

[マップ §6.2](map.md#62-mapdata-16-b--行確定推定) の表を更新した欄。

| off | 型 | 内容 | 確度 |
|---|---|---|---|
| **+0x04** | **u16** | **フィールドの BGM = SoundData の行**。`FUN_0031E9BC` (`@0x31EAF8` 付近) が `FUN_0031C038(+0x16FC, 行)` の u16 +0x04 を返す。その前に `FUN_00314550(…, 0x3A)` (セーブの値 0x3A) が 0 でなければそれを返す (曲の上書き。推定)。0 のときは MapGroup (+0x1774) +0x2E の下位 3 ビットが 2 なら 19 / 20 (`BGM_MAP_WORLDMAP` / `BGM_MAP_SEA`)、3 / 5 なら別の処理、それ以外が MapData +0x04 | **確定** (コード + 値 17〜48 = BGM_MAP_* など、781 も BGM) |
| **+0x06** | u16 | **エンカウントの経路 `FUN_001DAB34` で戦闘の前に鳴らす曲** (`@0x1DAD60` → `FUN_0031E98C`)。値 0 / 2 / 3 / 4 / 5。戦闘の初期化で BattleField の行の +0x08 に置き換わる | 読む所は確定 / 「戦闘の曲」はデータからの推定 |
| **+0x08** | u16 | **エンカウントの効果音の行**。`@0x3E67BC` → `FUN_001A0AC4` (0 なら 0x6B)。値 0x6B〜0x6F = SoundData 107〜111 (`SE_ILD_CHANGE` / `SE_FLD_ALERT` / `SE_FLD_FORMATION` / `SE_FLD_ENCOUNT1` / `2`) | 読む所は確定 / 用途は推定 |

- 以前の「+0x04 を読む所はない」は、行のポインタを `FUN_00122FF4` 経由で引く `FUN_0031E9BC` を見落としていた。+0x04 は u8 でなく u16 (+0x05 が 3 の行が 3 つあり、u16 で 781)。
- 値の度数 (127 コンテンツの MapData): +0x04 は 0 が 49、21 / 27 / 32 などが多い。+0x06 は 2 が 239、0 が 58、5 が 14、3 が 10、4 が 4。+0x08 は 107 が 200、108 が 111。

## 7. 未確認

- BattleField の +0x00 / +0x04 からモデルを読み込む関数 (+0x114 の行の +0 / +4 を読む所)。
- `FUN_002A37D4` の 3 つの場面。CRO から呼ぶ戦闘 (`0x454940` など) を使うコンテンツと、その BGM の値。
- SoundData +0x04 の種類 1 と 3 の違い、効果音の行の ID と sound.bcsar の対応。
- ボスの群れ 66 件が本当に BGM 3 の行を指すか (データの照合)。
