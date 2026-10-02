# RPG3 (oahu) の BGM・効果音

RPG3 の音の形式と、BGM・効果音が**どこで決まるか** (マップ・ダンジョンの戦闘・決まった戦闘・コード) をまとめる。アドレスは Update (v4096) の code.bin。RPG2 (kahara) の音は `encounters.md` §4・§5。

## 1. 形式
- **RPG2 と同じ。** RomFS の `sound/sound.bcsar` (CSAR) に音 611 個の名前・種類・波形・シーケンスがあり、BGM と ME は `sound/stream/*.bcstm` (DSP ADPCM、クルーザーの 2 曲だけ PCM8) のストリーム。Panana の `src/sound/` (CSAR・CWAR・CBNK・CSEQ・CSTM の読み込みと再生) がそのまま使える (ストリーム・波形・シーケンスの 3 種類とも再生を確認)。
  - ストリームのファイル名は音の名前と違うことがある (音 `BGM_VILLA_DESERT` → `BGM_DESERT.dspadpcm.bcstm`)。CSAR のファイル表がパスを持つので、名前から組み立てずにファイル表を引く。
  - `sound/voice/` は音声合成 (電波人間の名前の読み上げ) のデータ。
- Update の RomFS は音を差し替えない (patchList の 11 アーカイブに音はない)。音は Base だけで読める。

## 2. soundData.bin (master `21350000`、597 行 × 0xC)
RPG2 の soundData (418 行) と同じ並び。行番号がゲームの「音の番号」で、各テーブル・コードはこの行番号で音を指す。

| off | 型 | 内容 |
|---|---|---|
| +0x00 | u32 | サウンドアーカイブのアイテム ID (`0x01nnnnnn` = 音 nnnnnn)。行 0 は 0 |
| +0x04 | u32 | 0x340 (全行同じ) |
| +0x08 | u8 | 音量 (全行 100)。残りの 3 バイトは埋め草の D0 |

- 行 1〜36 が BGM (1 `BGM_TITLE` … 7〜10 `BGM_BATTLE_1〜4` … 24〜31 `BGM_CAVE_*`、32 `BGM_MAOU_TOWER`、35・36 `BGM_FISHING_1/2`)、37〜58 が ME (短い曲)、59 以降が効果音 (`SE_SYS_*`・`SE_FLD_*`・`SE_BTL_*` など)。
- 行 50 と 53 は同じ音 (`ME_FISH_GET_1`)。soundData から指されない音が 16 個ある (`BGM_EVENT_FESTA`、`ME_BANNER`、`SE_BTL_DROP1` など)。
- 音 → soundData の変換は、サウンド管理 (`*0x5A5B08`) の +0x56C に入るコールバック `FUN_001A68DC(行)` (行の +0x00 を返す)。`@0x2135F0` で登録する。

## 3. どこで鳴るか

### 3.1 マップ (mapData、167 行 × 7)
RPG2 と同じく **[4] フィールドの BGM、[5] 戦闘の BGM、[6] 足音** (いずれも soundData の行。[0]〜[3] はタイルセットなどの資源)。

- マップの mapData の行は、マップのキーで mapData の索引 (行のあとの追加領域、ハッシュ → 行) を引いて決まる (`FUN_0048EE20`、結果は `*0x59EE60` +0xF4)。どのマップがどのキーを持つかはマップの解析 (#66) の範囲。
  - 状態 1〜3 (ワールドマップなど) ではキー `0xDAF3A36F` (`@0x556288`) = 行 164 を使う。
- **フィールドの BGM**: `FUN_0024CB8C(mapData[4], マップのキー, …)` が鳴らす行を決める (`@0x24CB3C`、`@0x24CF20`)。ふつうは [4] のままだが、次のときは差し替える。

  | 条件 | 行 |
  |---|---|
  | キー `0xA8654391` (ワールドマップ。全ダンジョンの mapGroup +0x04 がこの値) | 状態 (`FUN_0023BC6C`、`FUN_0021395C(3〜6)`、フラグ 0x59 / 0x5B) により 3 `BGM_WORLDMAP` / 4 `BGM_FUNE` / 5 `BGM_CRUISER_1` / 6 `BGM_CRUISER_2`。名前からは乗り物 (船・クルーザー) と推定 |
  | キー `0x7D6021D8` で `FUN_001EDCF0(0x1E, 2)` が真 | 0x23 `BGM_FISHING_1` |
  | `FUN_002AB0BC(キー)` = 0x16 で `FUN_001ED9B8(3)` が真 | 0x11 `BGM_ELEGY` |

- **戦闘の BGM (ふつうの戦闘)**: マップの行ではなく、**ダンジョンの行の [5]**。ダンジョンに入ると mapGroup +0x2E がセーブ +0x5469 に入り (`@0x24D1B0`)、戦闘を始めるときに mapData[*(+0x5469)][5] を `FUN_00213970` で鳴らす (`@0x25047C`、`@0x2F8D40`)。
  - したがって、ダンジョンが指していない行の [5] は鳴らない可能性が高い (推定)。元のデータではほぼ全行 7 `BGM_BATTLE_1`。8 `BGM_BATTLE_2` はボス再戦の館 (行 96・97)、10 `BGM_BATTLE_4` はコロシアム (行 72・73) と行 164。
- 足音 [6] は 88〜92 (`SE_FLD_STEPS1〜5`)。読み手は `@0x1C3D14` ほか (未確認)。

### 3.2 mapGroup (89 行 × 0x34) の音まわりの欄
| off | 型 | 内容 |
|---|---|---|
| +0x04 | u32 | 0xA8654391 (ダンジョンのある全行。ワールドマップのキーと推定) |
| +0x1C | u32 | 名前 (MessageSystemCommon。例 行 1 = 0x89「ドローンのどうくつ」) |
| +0x2E | u8 | **ダンジョンの mapData の行** (戦闘の BGM はこの行の [5]) |
| +0x2F | u8 | 2 つ目の mapData の行 (町は家の中など。0 = なし。居住島はすべて 24) |

- RPG2 の mapGroup +0x26 / +0x27 に当たる。

### 3.3 決まった戦闘 (ボス戦など)
- **`FUN_0021112C(&群れのハッシュ, BGM)`** (群れは monsterGroup の索引で引く) と **`FUN_00211228(群れの行, BGM)`** が決まった群れとの戦闘を始める。RPG2 の `FUN_002fc790(行, BGM)` に当たる。BGM は `FUN_00213970` で鳴らす。
- **BGM が 0 のときは群れで決まる: monsterGroup +0x32 bit2 (0x04) が立っていれば 8 `BGM_BATTLE_2`、なければ 7 `BGM_BATTLE_1`** (`@0x2111C0`)。bit2 が立っている群れは 22 個 (9・19・20・21・28・42・43・50・63・76・90・91・93・94・95・100・111・112・113・115・116・187。クリムゾンキーパー・ジャシン・ドローンＺ などボス)。
- **モンスターごとの BGM はない。** monsterParameter に音の欄は見つからず、曲は群れのビットか呼び出し側の引数で決まる。
- コードの中の呼び出し (群れはリテラルのハッシュから引いたもの):

  | 呼び出し | BGM | 群れ |
  |---|---|---|
  | `@0x2B8614` | 9 `BGM_BATTLE_3` | 188 はかいりゅう (ハッシュは `0x5668CC` +8) |
  | `@0x2BAE18` / `@0x2BB264` | 0 → 8 | 19 クリムゾンキーパー / 20 フロストキーパー |
  | `@0x2C1524` | 9 | |
  | `@0x2C1934` / `@0x2D1DB0` / `@0x30DFA8` | 0 → 8 | 111 ブラックナイト / 187 ポーン / 76 テンペスター |
  | `@0x2F4478` / `@0x3829C4` | 7 | 116 キラービースト |
  | `@0x358BF0` / `@0x358C28` / `@0x358C60` | 0 → 7 | 73・74・75 (ファイヤーブロックス 1〜3 体) |
  | `FUN_00211228` を 7 / 8 / 9 で呼ぶ 10 か所 (`@0x353968`、`@0x3621D0`、`@0x36AEB4` など。ほかに 0 で呼ぶ 3 か所) | 7〜9 | 呼び出し元の構造体の欄 (+0x14 など) の行 |

### 3.4 コードで決まった BGM
`FUN_00213970(行, …)` (BGM を鳴らす。呼び出し 28 か所) に定数を渡しているところ:

| 行 | 呼び出し | 場面 (推定) |
|---|---|---|
| 0x17 `BGM_ENDING` | `@0x1D7AE8`、`@0x1D8CB8`、`@0x1D9AC8` | エンディング |
| 0x0B `BGM_DENPAISLAND` | `@0x209AA4` | |
| 0x0A `BGM_BATTLE_4` | `@0x2E040C`、`@0x3217E0`、`@0x346730` | 特別な戦闘 (`FUN_00213388(1)` のあと) |
| 0x23 `BGM_FISHING_1` | `@0x24E7BC`、`@0x327E68` | 釣り |

- ほかに、曲の一覧を順に回す処理 (`@0x27E0C0`。+0x0A からの u16 の並び) と、イベントのスクリプトから鳴らすもの (`@0x27EA00` など) がある。スクリプトの中の BGM は未集計。

## 4. マスターの表の読み手
RPG3 のコードは master の表を名前ではなく、マスター (`*0x59F200`) の中の**読み手** (0x1C バイト: +0x04 表の先頭、+0x0C 行、+0x10 行のポインタ、+0x14 状態) で引く。エントリのハッシュ → 読み手のオフセットは `FUN_001D9BBC` (ハッシュの二分探索の分岐) で決まる。これを実行して得た対応 (92 個中 82 個。残りの flagData 系・vendor・innSetting・W01_ground・denpaHash はここでは割り当てない):

| オフセット | 表 | オフセット | 表 | オフセット | 表 |
|---|---|---|---|---|---|
| +0x000 | floorData | +0x310 | treasureGroup | +0x690 | denpaByeEvent |
| +0x01C | animData | +0x32C | mapChara | +0x6AC | denpaRecoverEvent |
| +0x0E0 | actionData | +0x348 | mapCamera | +0x700 | common_SaveDenpaHome |
| +0x0FC | antennaGroup | +0x364 | **mapData** | +0x738 | mapNavi |
| +0x118 | itemData | +0x380 | mapResource | +0x754 | cecLampIgnore |
| +0x134 | levelData | +0x39C | mapExtraRoom | +0x770 | houseRoofColor |
| +0x150 | bodyData | +0x3B8 | mapEffect | +0x78C | npcCollisionSize |
| +0x16C | bodyColorData | +0x3D4 | mapObject | +0x7A8 | mapExit |
| +0x188 | headData | +0x3F0 | mapSaveRestart | +0x7C4 | battleParameter |
| +0x1A4 | headDataRare | +0x40C | scriptCharacterPopupPos | +0x834〜+0x9F4 | createRarityLot・createSelect* (16 個) |
| +0x1C0 | conditionData | +0x498 | mapParts | +0xA2C | monsterEffect |
| +0x1DC | denpaPersonality | +0x4D0 | designedMap | +0xA48 | monsterParameter |
| +0x1F8 | initLevelData | +0x4EC〜+0x524 | plantInfo / plantMap / plantPoint | +0xA64 | **monsterGroup** |
| +0x214 | **soundData** | +0x540〜+0x5B0 | fishData / fishingHook / fishingPoint / fishingRod / fishingLevel | +0xA80 | reBossInfo |
| +0x230 | stereoCamera | +0x5CC | previewParameter | +0xA9C〜+0xAD4 | nagomiHouseList / nagomiCatchList / nagomiTownList |
| +0x24C | font | +0x5E8 | insideInterior | | |
| +0x268 | areaInfoData | +0x604 / +0x620 | worldmapParts / worldmapPort | | |
| +0x284 | denpaCustom | +0x63C / +0x658 / +0x674 | mapAppearPos / mapAppearWorldmap / mapJumpPoint | | |
| +0x2A0 / +0x2BC | actionCamera / statusCommunity | | | | |
| +0x2D8 | **mapGroup** | | | | |
| +0x2F4 | dungeonEnv | | | | |

- 表の読み手の使い方は RPG2 と同じ (`FUN_0022C084(読み手, 行)` で行のポインタ)。ある表を読む関数を探すときは、`*0x59F200 + オフセット` を探すとよい。

## 5. Panana
- `#/sounds` (BGM・効果音) は RPG2 の一覧・試聴の部品 (`pages/sounds` の `SoundView`、`ui/SoundPicker`) をそのまま使い、RPG3 の「使われている場所」(§3) を出す (`src/oahu/sound.ts`、`src/oahu/SoundPage.tsx`)。§3.3・§3.4 のコードの呼び出しは、Update の code.bin を BL / B 命令で走査して見つける (Update がないときは出さない)。

## 6. 未解析
- イベントのスクリプトから鳴らす BGM・ME・効果音 (RPG3 のスクリプト実行器がまだない)。
- マップ (キー) → mapData の行の対応 (#66)。
- ギミック (EventObject) の効果音、アクションの演出の効果音の欄。
- `@0x2E040C` などの特別な戦闘の場面、ワールドマップの状態 4〜6 の正確な条件。
