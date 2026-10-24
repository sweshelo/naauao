# 電波人間のRPG (honolulu): RomFS・master・メッセージ

対象: 日本版 Base Title ID `0004000000077E00`、TitleVersion 1024 (1.0.0)。アドレスは展開済み code.bin の仮想アドレス (base `0x100000`)。[ROM の識別・展開](../roms/honolulu.md)。

確度の表記: **確定** = 実データとコードの両方で確かめた。**データ** = 実データの形・値・メッセージの対応から読んだ (コードは未確認)。**推定** = 形からの推測。未確認の項目は未確認と書く。

## 1. 全体像

- 入れ物は RPG2 (kahara) と同じ系統。GS アーカイブ version 5、GS テーブル (ヘッダー 0x40 / 0x50 / それ以上)、GMSG。[共通形式](../common/formats.md)。(確定: 同梱ツールでそのまま読める)
- モデルは RPG2 と同じ CGFX (`CGFX` の bcres、テクスチャを含む)。(データ)
- ルートのアーカイブ名の多くが RPG2 と同じハッシュ (`56562135` master、`2713402F`、`470D2848`、`8756A407`、`A90C8038`、`46910AB6`、`469B3DC6` など)。中身の行サイズ・行数・欄は違うので、RPG2 の表の定義を流用しない。
- RPG2 との大きな違い:
  - アイテムに 3D モデルがない。itemData にモデルの欄がなく、道具・装備のモデルのアーカイブ (RPG2 の `1D37838B` の道具のモデル) もない。ふく (服の柄) だけテクスチャを持つ ([items.md](items.md))。
  - 店は拠点の島 (デンパ島) の 1 軒だけで、品揃えはダンジョンの進み具合で切り替わる ([shops.md](shops.md))。
  - モンスターは monsterBattleParameter (master) + monsterData (`2713402F`) の 2 表。RPG2 の MonsterParameter / MonsterDesign とは行サイズが違う。
  - アクション (actionData) の表は master にない。電波人間の「アンテナ」の特技は skillData、モンスターのワザは monsterAttackSkill。
  - マップの一覧はコードの表ではなく csvMap (`A90C8038`) にある (§4)。

## 2. ルートのアーカイブ

`gsarc.py catalog` と中身の先頭 4 バイト・名前から分類した。役割は名前・参照元から読んだもの (データ)。

| アーカイブ | 中身 | 役割 |
|---|---|---|
| `56562135` | 113 エントリ。GS テーブル 53、GMSG 9、フォント、darc (`common.arc`・`status.arc`)、カメラの bcmdl、t2 (LZ) 24 | master (§3) |
| `2713402F` | effectData (379 × 0x28)、directData (530 × 0x12)、monsterData (92 × 0x2C) | エフェクト・演出・モンスターの見た目 |
| `470D2848` | CGFX 152 | モンスターのモデル・テクスチャ (monsterData +0x04 / +0x08 のハッシュがここのエントリ) |
| `8756A407` | CGFX 397 | エフェクト (RPG2 と同じ役割と推定) |
| `A90C8038` | マップ DB `A2C14C00`、csvMap、darc、区画のデータ | マップ (§4) |
| `46910AB6`・`832DA6D7`・`62D28C8A`・`EAE2C0F2`・`A813D747`・`AC6F0948`・`CF71F752`・`84EDE99F` | t8 のエントリ (25〜34 個) | mapResource 行 1〜8 の先頭が指すタイルのモデルのアーカイブ |
| `469B3DC6` | CGFX 9 | マップのテクスチャ (RPG2 と同じ役割と推定) |
| `15BE1AD4`・`3A309010`・`FB501D1A` | CGFX | mapObject の行が指すアーカイブ (置物・オブジェクトのモデル) |
| `B50A5EA9` | CGFX 123 | ふくの柄のテクスチャ (clothData +0x00 のハッシュがここのエントリ) ほか |
| `FB50F315` | `island_base`・`mnmp_build_XX_YY`・`mnmp_island_XX` など 32 | 拠点の島 (デンパ島) と施設の建物、島のミニマップ |
| `38C1B821` | `island.arc` | 島の画面のレイアウト |
| `499887B0` | `inside_01.bcmdl` ほか | 店の中 (店の画面 `FUN_002C7B18` が読み込む) |
| `8DA0CF3F` | `house.arc`・`house_room_00〜10` | 電波人間ハウス |
| `F2DD7C69` | `shrine.arc`・`inside_02` | 精霊のほこら |
| `CD9498CF` | `pc.arc` | パソコン (QR コード) |
| `90EACC05` | MessageAntenna、MessageEventIntro2、`capture_*` | 電波人間キャッチ (アンテナ塔) |
| `6F896E38` | MessageNagomi、nagomiTalkItem、nagomiAction | ハウスの電波人間の会話 |
| `91B0619D`・`8F6A296B` | `battle.arc`・`command.arc`・MessageCommand | 戦闘 |
| `1D37838B` | darc (`antenna001〜125.bclim`)、MessageEvent | アンテナのアイコン (アイテムのモデルではない) |
| `570C7BF7` | `title.arc`・`title_logo` | タイトル |
| `FBADD94C` | MessageStaffroll ほか | スタッフロール |
| `sound/` | `sound.bcsar`、`stream/`、`voice/` | 音 |

## 3. master (`56562135`)

コードは master を表の名前やハッシュで探さず、エントリの順に読み込んだ表を固定のオフセットで引く。表の保持体は 0x1C 間隔に並ぶ (RPG2 と同じ作り)。master のポインタは `*0x31F65C`。

- 確定: shopItemData (エントリ 68) の保持体は master +0x5CC、shopItemGroup (69) は +0x5E8 (`FUN_00230074`・`FUN_001BD0xx` が行の欄を読んで店の処理に使う。[shops.md](shops.md))。
- 推定: 種別 9 / 0 の GS テーブル (エントリ 22 の animData から) を順に並べ、保持体 = master + 0xC4 + 0x1C × (エントリ番号 − 22)。上の 2 つと合う。ほかの表で確かめていない。
- 保持体の +0x04 が表 (ヘッダー付き) を指し、行は `FUN_0020CBB4` で引く。範囲外の行番号は −1 として扱う。

### 3.1 表の一覧 (データ)

| # | エントリ | 表の名前 (ヘッダー) | 行 × 行サイズ | 分かっていること |
|---|---|---|---|---|
| 22 | animData | — | 77 × 0xC | |
| 23〜27 | dungeonBoss / dungeonData / dungeonEnv / dungeonObject / floorData | | 2 × 1 / 18 × 0x18 / 9 × 0x14 / 10 × 0x14 / 27 × 4 | dungeonData: +0x10 名前、+0x12 説明 (推奨レベル) のメッセージ ID。行 1〜11 が 11 のダンジョン |
| 30 | itemGroup | ItemGroup | 186 × 0x24 | 宝箱・ドロップの中身と推定 (未確認) |
| 31 | mapChara | MapChara | 111 × 0x30 | |
| 33 | mapData | MapData | 15 × 0xC | |
| 35 | mapObject | MapObject | 68 × 0x24 | +0x00 アーカイブ、+0x04 モデル (ハッシュ) |
| 36 | mapParts | | 48 × 0x114 | |
| 37 | mapResource | MapResource | 9 × 0x14 | +0x00 タイルのモデルのアーカイブ (§2) |
| 38 | designedMap | DesignedMap | 83 × 0x20 | |
| 39〜41 | menuList / menuItem / menuAction | | 115 × 0x28 / 917 × 0x34 / 81 × 0x14 | メニューの構成 |
| 42〜44 | skillData / skillGroup / skillGroupRare | | 152 × 0x28 / 46 × 0x14 / 45 × 4 | アンテナの特技。skillData +0x00 名前 (例 0x414「アンテナなし」)、+0x04 説明 |
| 45 | monsterFixGroup | MonsterFixGroup | 24 × 0x16 | 固定の敵の組 (ボス戦) と推定 |
| 46 | monsterGroup | MonsterGroup | 58 × 0x2E | 敵の群れ |
| 47 | monsterAttackSkill | MonsterAttackSkill | 233 × 0x24 | モンスターのワザ |
| 48 | monsterBattleParameter | MonsterBattleParameter | 111 × 0x34 | モンスターの能力 (欄は未解析) |
| 49 / 50 | monsterFieldData / monsterEffect | | 90 × 8 / 15 × 0x34 | |
| 51 | itemData | ItemData | 298 × 0x1C | [items.md](items.md) |
| 52 / 53 | clothData / equipData | | 102 × 8 / 198 × 0x18 | ふくの柄 / 装備の効果 ([items.md](items.md)) |
| 54 / 55 | levelData / conditionData | | 99 × 0x54 / 22 × 0x2C | |
| 56〜61 | bodyData / bodyColorData / headData / headDataRare / denpaPersonality / initLevelData | | | 電波人間の体・色・頭・性格 |
| 62 | scenario | Scenario | 205 × 0x2C | +0x24 u16 ダンジョン、+0x26 u16 段階と推定 |
| 63〜65 | bossBgm / soundData / soundDataType | | 18 × 8 / 252 × 0xC / 23 × 4 | |
| 68 / 69 | shopItemData / shopItemGroup | | 753 × 4 / 12 × 0xC | 店 ([shops.md](shops.md)) |
| 70 | nagomiTalkList | | 51 × 0x1C | |
| 71〜74 | denpaHash / denpaCustom / flagData / flagDataLevel | | 25 × 3 / 32 × 0x14 / 87 × 8 / 2 × 8 | 71〜74 は種別 0 |

- `monsterData` (`2713402F`、92 × 0x2C): +0x00 名前のメッセージ ID (行 1 = 0x227「きばコウモリ」)、+0x04 / +0x08 `470D2848` のエントリ (モデル / テクスチャ)、+0x0C / +0x10 f32 (拡大率と推定)。(データ)
- RPG2 の itemData は 713 × 0x30、MonsterParameter は 185 × 0x54。行数も大きさも違う。

## 4. マップ

- マップ DB は RPG2 と同じ形 (`A90C8038` のエントリ `A2C14C00`、`u32 件数` + `{u32 ハッシュ, u32 位置, u32 サイズ}` × 件数、ハッシュの昇順)。194 件、約 80 KB (RPG2 は 2082 件・約 553 KB)。(データ)
- csvMap (`A90C8038`、97 × 4): 各行がマップのハッシュで、97 件すべてがマップ DB にある。行の後ろの追加領域 (+0x20 が非ゼロ) に `{ハッシュ, 番号}` の対がハッシュ順に並ぶ (検索用と推定)。RPG2 のマップ一覧は code.bin の表 (0x4C3AFC) だったので、ここが違う。(データ)
- 区画の数・並び (RPG2 は 1 マップに区画 0〜9) は未確認。194 = 97 × 2 なので、1 マップに 2 つのエントリと推定。
- dungeonData の行 1〜11 = デンパ島のどうくつ・風の森・海底洞窟・魔王の塔・オアシスへの道・しゃくねつ火山・氷の島・闇の遺跡・火口の風穴・ストレンジフォレスト・ガーディアンタワー。行 12〜17 は同じ名前の再訪用と推定。

## 5. 拠点の島と施設

- 拠点はデンパ島の 1 か所。施設は電波人間ハウス・船着場・デンパ島のどうくつ・アンテナ塔・ミュージアム・パソコン・ショップ・精霊のほこら (メッセージ 75〜98)。
- 施設は「〜のもと」のアイテム (へやのもと・パソコンのもと・ミュージアムのもと・いかだ / ふね / クルーザーのもと、メッセージ 688〜695) で建つ・広がると推定。ショップのもと (693) の名前はあるが、itemData の行は見つけていない。
- 他の島 (ダンジョン) へは船着場からワールドマップで行く (メッセージ 92・504〜506)。店は拠点の島にしかない。

## 6. メッセージ (GMSG)

| ファイル | ID の範囲 |
|---|---|
| MessageSystemCommon_JP | 0〜2468 |
| MessageBattle_JP | 2471〜2896 |
| MessageField_JP | 2897〜3299 |
| MessageEventIntro2_JP | 3305〜3323 |
| MessageIslandEvent_JP | 3324〜3338 |
| MessageEvent_JP (`1D37838B`) | 3339〜 |
| MessageNagomi_JP (`6F896E38`)、MessageAntenna_JP (`90EACC05`)、MessageCommand_JP (`91B0619D`)、MessageStaffroll_JP (`FBADD94C`) | それぞれのアーカイブ |

- 各本文の先頭 u16 は種別コードで、0 のものがある (例: 551「きばコウモリ」)。`gsmb.py` の旧版は 0x0000 で本文の終わりを探していたため、種別 0 の本文が空になった。現行版は種別コードとタグの引数を飛ばして読む。
- タグは RPG2 と同じ `0x0001 コード` と `0x0002 種類 ID 0x0000` (差し込み) の形。番号が RPG2 から 2 ずれる:

| 内容 | kahara | honolulu |
|---|---|---|
| ルビ | `0x0001 0x0027` 親字 `0x0001 0x0028` よみ `0x0001 0x0029` | `0x0001 0x0025` / `0x0026` / `0x0027` |
| 別のメッセージの差し込み | `0x0002 0x0026 ID 0x0000` | `0x0002 0x0024 ID 0x0000` |

- `0x0001 0x010C` は店員、`0x0001 0x010D` は精霊の話者と推定 (その人のセリフの先頭に付く)。
- `*_IN` (読み) の本文は UTF-16 ではない別の符号化。未解析。
- 主なメッセージの位置: ダンジョン名 36〜47 (ルビ付き 48〜59)、説明 62〜71、店の画面 116〜149、店員によるアイテムの説明 150〜388、モンスター名 551〜、アイテム名 661〜、アイテムの説明 716〜。

## 7. 未解析・次に調べること

- monsterBattleParameter・monsterAttackSkill・monsterGroup・skillData の欄。RPG2 の MonsterParameter はビット詰めだったので、同じかどうかから確かめる。
- itemGroup (宝箱・ドロップ) と、宝箱の置き場所 (マップの区画) の関係。
- マップの区画の並びとタイルの形式 (RPG2 の区画 0〜9 と比べる)。
- セーブ変数 0x40 (ダンジョンごとの進み具合、[shops.md](shops.md)) の値の意味。scenario との関係。
- Update があるか。
