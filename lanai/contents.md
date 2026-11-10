# コンテンツ (シナリオ・ステージ) の仕組み

対象: lanai Base v0 + Update v17408。表の形式は [analysis.md §2](analysis.md#2-gs-テーブル-lanai-形式確定)。

『FREE!』のステージ (ストーリーの各話、イベントステージ、試練、クイズなど) は、**1 つずつが「コンテンツ」**として、別々のルートのアーカイブに入っている。コンテンツは次のものを持つ。
- マップ・敵・宝・店などの表
- メッセージ
- **CRO モジュール** (イベントのスクリプト)

本体の code.bin は共通の処理と Script API だけを持つ。

## 1. コンテンツの一覧: master の Contents (確定)

`2135000A` の `contents.bin` (表の名前 `Contents`、127 行 × 8)。

| off | 型 | 内容 |
|---|---|---|
| 0x00 | u32 | コンテンツのアーカイブ (ルートのファイル名。例 `59B00000`) |
| 0x04 | u32 | そのアーカイブの中の TableResource のエントリのハッシュ (全行 `D2490C00`) |

- **行番号 r が、コンテンツ番号**。アーカイブ r には `contents{r:04}.cro` が入っていて、127 行すべてで一致する (例 行 38 → `59B00000` の `contents0038.cro`)。
- コンテンツ 0 (`5EFB0000`) は島・町 (マップ `M02`・`H01`) のスクリプトの本体 (CRO 164 KB)。1 以降がステージ。

## 2. コンテンツのアーカイブの中身

例 `59B00000` (コンテンツ 38、37 エントリ)。どのコンテンツもほぼ同じ構成。

| type | エントリ | 内容 |
|---|---|---|
| 12 | AreaInfo, BattleFieldContents, CannonParameter, CecLampIgnore, **ContentsDef**, DebugMapJump, DesignedMap, FishingPoint, layout_contents, MapCamera, MapChara, MapData, MapDataResource, MapEnv, MapGroup, MapPartsType, MapResource, MapSurfaceIgnore, **MonsterGroup**, PlantPoint, Shop, ShopItem, **TreasureGroup** | コンテンツの中だけで使う表 (24 個前後) |
| 3 | **TableResource** | このアーカイブの表のエントリのハッシュの一覧 (26 行 × 4。読み込む表の一覧と推定) |
| 3 | 名前なし 3 個 | マップの配置らしきバイナリ (例 `D01001B01` の文字列を含む)。未解析 |
| 1 | **`contentsNNNN.cro`** | イベントのスクリプト (§4) |
| 1 | `d01_EventObject.bin` (表の名前 `D01_EventObject`、0x64 × n) / `d01_StaticEvent.bin` | マップのイベントの配置 |
| 11 | `d01_msg` (message / voice) | このコンテンツの会話 |
| 11 | MapPartsCaveB / MapPartsRuinsB / MapPartsTemple … | マップの部品 (67 × 0x40) |
| 1 | **MapStage** | ステージの定義 1 行 (§3) |
| 12 | MessageContents (message / voice) | |
| 6 | `Stage_symbol01.arc` | ステージ選択の絵 (レイアウト) |

### 2.1 ContentsDef (4 × 4 B)

| 行 | 値 | 内容 |
|---|---|---|
| 0, 1 | コンテンツ番号 | |
| 2 | CRO のエントリのハッシュ | 例 コンテンツ 38 = `2917F400` (= `contents0038.cro`) |
| 3 | 1 | 意味は未確認 |
| 4 以降 | (一部のコンテンツだけ) | 例 コンテンツ 97 は `6, 0x4C4B40, 0x1E, 0x64, 0xC7`。未解析 |

## 3. ステージの定義: MapStage と MapStageIntegration

コンテンツの `MapStage` (1 行 × 0x40) と、master の **MapStageIntegration** (132 行 × 0x4C) が同じ内容を持つ。

MapStageIntegration は MapStage の +0x00〜+0x33 に、次の 3 欄を足したもの。
- +0x34: コンテンツ番号
- +0x38: アーカイブ
- +0x3C: TableResource のハッシュ

MapStage の +0x34〜+0x3F は、MapStageIntegration の +0x40〜+0x4B に移る。

| off (MapStage) | 型 | 内容 | 確度 |
|---|---|---|---|
| 0x00 | u32 | 0x64 刻みの値 (並び順と推定) | 推定 |
| 0x04 | u32 | ステージの絵のアーカイブのハッシュ (`578F1C00` = `Stage_symbol01.arc` など) | 確定 |
| 0x08 | u32 | 0x1A0 / 0x1A1 | 未確認 |
| 0x0C | u32 | **MessageMapStage の行 ID** (ステージ名・ミッション・説明) | 確定 |
| 0x10 / 0x14 / 0x18 | 文字列 | `stage_name` / `mission_name` / `exp_note` (コンテンツ側はどれも「なし」) | 確定 |
| 0x1C | u32 | 未確認 (例 0x11〜0x19、0x15D〜、0x7D0) | |
| 0x24 | u8 | 分類と推定 (3 = 本編、0x16 = イベント系、0x1A = 一部) | 推定 |
| 0x38 | u16 | コンテンツ番号 | 確定 |
| **0x3A** | u16 | **始まりの MapGroup** (コンテンツの `MapGroup` の行)。[§3.3](#33-ステージの始まり-最初のマップと入口) | **確定** |
| **0x3D** | u8 | **ステージに入るのに要るスタミナ** | **確定 (§3.1)** |
| 0x3E | u8 | 0x65 または 0 | 未確認 |

### 3.1 スタミナの値の確認
ゲーム内のクイズ (`5EB00000` の MessageQuiz) が、ステージに要るスタミナを問う。正解の選択肢 (最初の選択肢) と、MapStage +0x3D を比べた。

| ステージ (MessageMapStage) | コンテンツ | クイズの正解 | +0x3D |
|---|---|---|---|
| 4.ウッキー大騒動 (`80000015`) | 4 | 20 | 0x14 = 20 |
| 10.異世界へ通じる場所 (`8000001B`) | 10 | 50 | 0x32 = 50 |
| 1.甘い誘惑 (`80000012`) | 1 | 「10 である」(○×問題) | 0x05 = 5 (×が正解と見られる) |

スタミナの回復は [stamina.md](stamina.md)。

### 3.3 ステージの始まり (最初のマップと入口)

アドレスは Update の code.bin。

- ステージ選択から入る処理 (`@0x253308`〜) は、ステージ枠 (`FUN_002C1D2C` の 0x158 B の枠) を引いて `FUN_002E7814` を呼ぶ。`ScriptMap::ChangeMapContents` (`0x454DE0`) も同じ。
- `FUN_002E7814` はセーブの値 0x27 / 0x28 に枠の +0x130 / +0x134 を、**0x29 (今の MapGroup、`FUN_0031EB38` が読む) に枠の +0x148** を入れ、0x2A〜0x2C を 0 にする。
- 枠は `FUN_001D6CD4` が MapStage から作る。**枠 +0x148 = MapStage +0x3A** (`@0x1D6E40`、MapStageIntegration では +0x46)。枠 +0x130 / +0x134 は枠の初期化 (`@0x2C1BE8`) で 0 になり、MapStage からは入らない。0x27 / 0x28 が 0 のときに MapGroup の最初のマップを使う処理は**追っていない**。
- データで照合した (ROM の 126 ステージ。MapGroup 0 の行 4 件を除く): **MapStage +0x3A の MapGroup の +0x14 / +0x18 (最初のマップのハッシュ / 地点 ID) は、126 件すべてで同じコンテンツのマップ表のマップ (ワールドマップではない) を指し、地点 ID はそのマップの区画 3 の出入口にある**。`DebugMapJump` の行 0 がある 68 件中 66 件はこれと同じ値 (違う 2 件はコンテンツ 3・69 で、デバッグ用の別の入口と推定)。
- したがって、ステージの始まりを変えるには MapStage +0x3A (MapStageIntegration +0x46 も) と、その MapGroup の +0x14 / +0x18 を書く (推定。ゲーム内では未確認)。MapGroup の +0x14 / +0x18 はほかの場面 (グループに入るときなど) でも読む可能性がある。

### 3.2 MessageMapStage (master、135 × 0x14)
欄 `stage_name` (+0x04)、`voice` (+0x08)、`stage_mission` (+0x0C)、`stage_exp` (+0x10)。+0x00 は 0 または 0xF。説明文の中で、表の差し込みタグ ([§2.2](analysis.md#22-メッセージ-確定)) を使ってアイテム名やモンスター名を引く (例 `[ItemData:0x800000C7:name]`)。

## 4. CRO と CRR

### 4.1 CRO
- `contentsNNNN.cro` は nn::ro の CRO (マジック `CRO0`、モジュール名 `contentsNNNN`)。アーカイブの中にあるので、ゲームはファイルではなくメモリーから読み込む。
- 中身はイベントのクラスで、RTTI の名前が残っている。
  - **マップ名 + EventObject の種類 + 番号**: 例 `D01001B01Npc0201`、`D01001B02Door002`、`D01001F01Gimmick001`
  - ステージ共通: 例 `D01Intro`、`D01BossEvent`、`D01BossWin`
- 本体から取り込む (import) のは Script API。例:
  - `ScriptChara::MoveTo`
  - `ScriptMenu::StartMessage`
  - `ScriptFlag::SetScriptBitFlag`
  - `ScriptCamera::MoveEyeAndTarget`
  - `ScriptSound::Play`
  - `StageResult::StageOpenAct`
  - `IntroCommon::Execute`

  コンテンツ 75 では、呼び先のクラスごとの数は ScriptChara 23、ScriptMap 15、ScriptMenu 9、ScriptCamera 9、ScriptSystem 8、ScriptFlag 6。本体のシンボル表が `app/lanai.crs`。
- RPG3 ではイベントのスクリプトを本体の「動作の生成」関数が作っていた ([oahu/events.md](../oahu/events.md))。lanai ではそれが CRO に分かれたので、**新しいコンテンツのイベントは CRO を作れば足せる**見込み。

### 4.2 CRO の関数の表 (フック)

- 127 個の CRO はどれも **indexed export が 41 個**ある。本体は `FUN_002E7E4C(状態, 番号)` (中で `0x4639CC` → nn::ro の番号でのアドレス引き) で番号の関数を取り出し、あれば呼ぶ。呼ぶ所は 46 か所で、番号は 0〜0x28。
- `mov r0, #0; bx lr` だけの関数を「空」とすると、13〜19・33・37・39 は 127 個すべてで空でない (共通の処理)。
- **番号 3 = 最初のイベント**。`FUN_00182324` (フィールドの場面のオブジェクトの初期化。モード `*0x4EB760 +8` が 3 か 0x1D のとき) が番号 3 を呼び、戻り値のイベントのオブジェクトを +0x0C に置く。125 個の CRO で空でない。例 コンテンツ 1: `ScriptMap::GetCurrentMapGroupID() == 1` かつ `ScriptFlag::GetScriptBitFlag(0x24)` が 0 なら `IntroCommon(0xA2B01CE4)` を基にした `D01Intro` を作る。そうでなく `GetScriptByteFlag(0x49) == 2` なら `CommonHeroMsg` を作る。どの場面で呼ぶか (マップに入るたびか) は未確認。
- 番号 0x1F / 0x20 は EventObject の出る・消える条件の差し替え ([map.md §7.1](map.md#71-eventobject-の欄-100-b))。ほかの番号の役目は未解析。
- **コンテンツ 99「あみだクジ（仮）」と 125「EVCK38（未定）」の CRO は、共通の番号しか持たない** (イベントのクラスなし、12 KB)。Update の `.crr/contents0099.crr` に登録されているので、CRO を作らずに「イベントのないステージ」を作るひな形に使える見込み (Panana #216 の追加の作業で使う。ゲーム内では未確認)。
- 写した CRO は元のステージと同じフラグ (例 0x24) を読み書きする。元のステージで開始の演出を見たあとは、写しでも出ない。

### 4.3 CRR
- `.crr/contentsNNNN.crr` (マジック `CRR0`) が、対応する CRO の **先頭 0x80 バイトの SHA-256** を持つ。コンテンツ 38 で確認した。Update の CRR は Update の CRO と一致し、Base の CRR とは一致しない。
- `.crr/` は Base に 47 個、Update に 127 個ある。Update の `.crr/` は patchList.bin に載っていないが、Update の CRO に合うのは Update の CRR だけなので、ゲームは Update 側を読んでいると判断する。読み込みの処理は未確認。
- CRR には RSA 署名がある。署名を確認しない環境 (RO の検査を外したカスタムファームウェアなど) でなければ、作り直した CRR は通らない見込み。実機・Azahar では未確認。

## 5. 新しいコンテンツを足すには (提案・未検証)

過去作のステージやモンスターを移すために必要になるものの見込み。

1. 新しいルートのアーカイブ (version 10)。§2 の表・CRO・EventObject・メッセージを入れる。
2. master の Contents に 1 行足す (アーカイブ + TableResource のハッシュ)。行番号がコンテンツ番号になる。
3. MapStageIntegration と MessageMapStage に行を足す。
4. CRO を作り、その CRR を `.crr/` に置く。
5. 配り方は、Update の RomFS に新しいアーカイブを足し、patchList.bin に載せる ([RPG3 の Update 方式](../roms/oahu-update.md#22-mod-を-update-として配る-タイトル-0004000e000ef000))。または、チェックインで配る表 (`bonus_tbl`、[checkin.md](checkin.md)) からステージを開く。

どの表の行数を本体が固定で持っているか (配列の大きさ) は未確認。
