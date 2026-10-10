# 電波人間のRPG FREE! (lanai) 解析メモ

対象: Base v0 + Update v17408 (17.0.0)。ROM の識別と展開は [roms/lanai.md](../roms/lanai.md)。アドレスは Update の code.bin。RPG2 / RPG3 のアドレス・行サイズ・ID は流用しない。

## 1. RomFS

### 1.1 ルートの構成
- ルートのファイルは 8 桁 16 進のハッシュ名。RPG3 と同じく下位 16 ビットで区別し、**`xxxx0000` と `xxxx000A` の 2 種類**がある。`000A` のほうは `_JP` の付いた表やメッセージを持つ (例 `7BF7000A` に `campaignCodeLocal_JP.bin`、`7BF70000` はタイトルのモデルだけ)。言語版の差し替えと推定する。`000A` のアーカイブのハッシュは code.bin に定数として出てこない (`0x7BF7000A` などの即値は 0 件)。
- ほかに `sound/` (sound.bcsar、`stream/`、`voice/`)、`font/`、`shader/`・`shaders/`、`proctex_files/`、`extdata_icon/`、**`.crr/` (CRO の登録)** と **`app/lanai.crs` (本体の CRO 用シンボル)** がある。RPG2 / RPG3 にない `.crr/` と `app/` は、コンテンツを CRO で読み込むため ([コンテンツ](contents.md))。

### 1.2 アーカイブの形式 (version 10、確定)

ヘッダーが 0x18 バイトに伸びた。エントリの 28 バイトは RPG2 / RPG3 と同じ並び ([共通形式](../common/formats.md#gs-アーカイブ))。

| off | 型 | 内容 |
|---|---|---|
| 0x00 | u32 | version = **10** |
| 0x04 | u32 | アーカイブのハッシュ (= ファイル名) |
| 0x08 | u32 | Update で入れ替わったアーカイブは 0x11 (= 17、Update の版と同じ)、Base のものは 0 |
| 0x0C | u16 | +0x08 と同じ値 |
| 0x0E | u16 | コンテンツのアーカイブ ([contents.md](contents.md)) は 0、それ以外は 1 |
| 0x10 | u32 | エントリ数 |
| 0x14 | u32 | 0 |
| 0x18 | 28 B × n | `hash, type, size, offset, comp, unk, raw_size` |

- +0x08 / +0x0E の意味はゲームの読み込み処理で未確認 (観測値のみ)。
- comp: 1 = 1 ファイル入り ZIP (名前入り)、6 = LZ10、0 = 無圧縮。LZ10 の size 0 のエントリもある (中身なし)。
- unk (+0x14): 1 が多い。2 は master の名前なし LZ 表 (メッセージ系) と、各コンテンツの 3 エントリ (`*_msg`、`MapStage`、`MessageContents`) だけ。

| type | 中身 (Update 適用後の全アーカイブ) | 個数 |
|---|---|---:|
| 1 | GS テーブル (.bin)・**CRO (`contentsNNNN.cro`)**・nftr・ctpk など | 737 |
| 2 | フォント (bffnt / bcfnt)・パレット (.act) | 9 |
| 3 | GS テーブル (コンテンツの `TableResource` など) と、マップの配置らしきバイナリ | 442 |
| 4 | BCH (モデル・テクスチャ) | 5366 |
| 5 | `.ptcl` (マジック `SPBD`。eft 系のパーティクル) | 1359 |
| 6 | darc / SARC (レイアウト .arc) | 301 |
| 10 | `.gsc` (背景・マップの場面。`rom:/…` のパスを含む。未解析) | 767 |
| 11 | GS テーブル | 553 |
| 12 | GS テーブル (コンテンツごとの表) | 3047 |
| 13 | BCH (アンテナ・体の模様のテクスチャ) | 14 |

- RPG3 で CGFX だったエフェクトは `.ptcl` に置き換わり、CGFX は見当たらない。モデルは RPG3 と同じ BCH。

## 2. GS テーブル (lanai 形式、確定)

RPG2 / RPG3 の GS テーブル ([共通形式](../common/formats.md#gs-テーブル)) とヘッダーが違う。**表の中に文字列の領域・行 ID・欄の名前・再配置表を持つ**。ゲームは読み込み後に `FUN_0018317C` でオフセットをポインターに直す (+0x3E が 0 のときだけ)。

| off | 型 | 内容 |
|---|---|---|
| 0x00 | u32 | 行数 |
| 0x04 | u32 | 行サイズ |
| 0x08 | u32 | 文字列領域の位置 (常に 0x40) |
| 0x0C | u32 | 文字列領域の大きさ |
| 0x10 | u32 | データの位置 |
| 0x14 | u32 | データの大きさ (行数 × 行サイズ) |
| 0x18 | u32 | 行 ID の表の位置 (0 = なし) |
| 0x1C | u32 | 行 ID の表の大きさ (4 × 行数) |
| 0x20 | u32 | 欄の名前の表の位置 (0 = なし) |
| 0x24 | u32 | 欄の名前の表の大きさ (8 × 欄数) |
| 0x28 | u32 | 再配置表の位置 (無ければファイルの末尾) |
| 0x2C | u32 | 再配置の件数 |
| 0x30 | u32 | 追加の領域の位置 (0 = なし。§2.1) |
| 0x34 | u32 | 表の名前の位置 (文字列領域の先頭から) |
| 0x38 | u32 | 表の名前の終わり (同上。NUL を含む) |
| 0x3C | u16 | 参照数 (読み込み時に増やす。ファイルでは 0) |
| 0x3E | u16 | 再配置済みなら非 0 (ファイルでは 0) |

- **行 ID**: 多くの表は `0x80000000 | 番号` を各行に持つ。ほかの表からの参照もこの形 (例 `0x800000C7`)。ゲームの行の検索 (`FUN_0031C038`) は、値が `0x80000000` 以上なら行 ID の表を引き、未満なら行番号として扱う。
- **欄の名前の表**: `(名前の位置 (ファイル先頭から), 行の中のオフセット)` の組。名前があるのは文字列の欄だけ (例 MapStage: `stage_name` +0x10、`mission_name` +0x14、`exp_note` +0x18)。
- **再配置表**: ポインターにする u32 のファイル位置の一覧。文字列の欄と、欄の名前の表の名前の位置が入る。文字列の欄は、ファイルでは文字列領域の中の位置を持つ。
- 1 文字だけを指す欄もある (CampaignCharacter は 1 行 1 文字で、文字列領域は NUL で区切られていない)。NUL まで読むと隣の文字列まで続く。
- 行の中の 1 バイト・2 バイトの欄の詰め物は 0xD0 (例 `D0D0D039`)。
- 名前がファイル名と違う表がある (例 `mapGroup` の名前が `MapGroup`、`checkin_Rom_JP.bin` の名前が `Checkin_Rom`)。同じ名前の表が 1 つのアーカイブに複数あることもある (`FE74000A` の MessageMenu が 9 個)。

### 2.1 追加の領域 (+0x30)
128 個の表 (例 コンテンツの MonsterGroup) が持つ。8 バイトの `(ハッシュ, 値)` の組の並び。用途は未確認。

### 2.2 メッセージ (確定)

GMSG (`.gsmb`) はなくなった。**文字列はすべて表の文字列領域にある UTF-16LE**。メッセージの表は `message` や `name` / `voice` などの欄を持つ (MessageCommon、MessageMenu、MessageMapStage、ItemData、MonsterParameter など)。

タグは `0x0001, コード, 引数の数 n` に、n 個の引数 (`u16 型` + 値) が続く。型 2 = u32、型 3 = `u16 長さ (u16 単位)` + ASCII (NUL・詰め物込み)。NUL 検索で終わりを決めると、タグの中の 0 で切れる。

| コード | 引数 | 内容 |
|---|---|---|
| 0x38 / 0x39 / 0x3A | なし | ルビ: 0x38 親字 0x39 よみ 0x3A 終わり |
| 0x37 | 3 個 (文字列 表の名前, u32 行 ID, 文字列 欄の名前) | **ほかの表の文字列を差し込む** (例 `ItemData`, `0x800000C7`, `name`) |
| 0x22 | なし | 改ページ (送り待ち) と推定 |
| 0x02〜0x24 | 文字列 1 個 (変数名) | 数値・名前の差し込み (例 `<C stamina>`、`<D rank>`、`<24 week>`) |
| 0x100〜0x13D | なし または 文字列 1 個 | 名前の差し込み・ボタンの絵など (例 `<109 name>` 3290 回、`<133>`) |

- 使われている組み合わせとその回数の一覧は、`gstable.py` の `message()` で数えられる。0x22 / 0x1xx の正確な意味は未確認。
- `voice` の欄は、本文と違うバイナリ (先頭が `C0 DE B0 D0 B0 00` で、すぐ後に本文と同じ文字列が続く) を指す。`sound/voice/` の音声合成用と推定。未解析。
- RPG3 の MessageSystemCommon の ID 範囲のような「ファイルをまたぐ通し番号」はない。メッセージは「表 + 行 ID」で引く。

## 3. master `2135000A` (114 エントリ)

RPG3 の `21350000` に当たる。主な表 (行数 × 行サイズ):

| 表 | 行 × サイズ | メモ |
|---|---|---|
| Contents (`contents.bin`) | 127 × 0x8 | コンテンツのアーカイブ。[contents.md](contents.md) |
| MapStageIntegration | 132 × 0x4C | ステージの一覧 (MapStage + 3 欄) |
| MessageMapStage | 135 × 0x14 | ステージ名・ミッション・説明 |
| FlagData | 178 × 0xC | セーブの値の定義 (行 = キー) |
| FlagDataContents | 6 × 0xC | コンテンツ用のフラグの定義 |
| FlagDataReserve | 104 × 0x4 | |
| ItemDataCore | 3232 × 0x3C | アイテムの数値 |
| ItemData (名前なし LZ) | 3854 × 0x10 | アイテムの名前・voice |
| ActionData | 5017 × 0x2C | |
| MonsterParameter (名前なし LZ) | 1231 × 0x24 | [monsters.md](monsters.md) |
| MonsterParameterMain / Extra / RegularEvent / SpecialEvent | 370 / 184 / 200 / 437 × 0x9C | 同上 |
| MonsterDesign | 570 × 0xA0 | 同上 |
| LevelData | 999 × 0x4 | プレイヤーレベルの必要経験値 (累計) |
| LevelStatusData | 33 × 0x24 | |
| ConditionData (名前なし LZ) | 192 × 0x28 | |
| EffectData | 1578 × 0x2C | |
| SoundData | 896 × 0x8 | |
| MapObject | 784 × 0x30 | |
| UseByDate | 162 × 0x4 | |
| CounterStop | 1 × 0x18 | 上限値 (999,999,999 / 99,999 など) と推定 |
| ParameterCap | 10 × 0x24 | |

ほかに釣り・なごみ・電波人間の作成 (`012A000A`)・家・装備の表がある。全部の一覧は `gsarc.py list` と `gstable.py info` で出る。

### 3.1 そのほかの主なアーカイブ

| アーカイブ | 中身 |
|---|---|
| `A9DF0000` | チェックインの表 (Checkin_Rom、CheckinData、CheckinDeliVersion、CheckinEVCK18 / 19、CheckinJewelBuy、CheckinCheckinCount)、raregetParameter、boostParameter。[checkin.md](checkin.md) |
| `25D60000` | CheckinOffsetTime |
| `307C0000` | `checkin_debug_JP` (`LanaiTool` で選ぶ開発用の文言) |
| `7BF7000A` | コード入力の表 (CampaignCharacter、CampaignCodeLocal、CampaignCodeNetwork、CampaignCodeAddParty …)、lotRareDenpa_Delivery。[codes.md](codes.md) |
| `D4410000` | ランキング (RankingStamina、RankingConfig、RankingPrize …) |
| `FE74000A` | MessageMenu などの UI の文言 |
| `28480000` / `719F0000` | 敵のモデル (`enemy_NN*.bch`) |
| コンテンツ 127 個 | `59Bx` / `5Cxx` / `5Exx` / `5Fxx` / `AFxx`。[contents.md](contents.md) |

## 4. code.bin (Update v17408)

| アドレス | 内容 |
|---|---|
| `FUN_0018317C` | GS テーブルの再配置 (§2) |
| `FUN_0031C038` / `FUN_0031C118` | 表の行を ID か番号で引く / 行数 |
| `FUN_002AF0DC` | base64 のデコード (表 `0x4A61C1`) |
| `FUN_0030FF10` | SHA-256 (nn::crypto。初期値 0x6A09E667 …) |
| `FUN_0027CC6C` / `FUN_0027CBFC` / `FUN_0027CD9C` | HTTP: POST の準備 / POST の欄の追加 / GET。どちらも `auth_token` を付ける ([checkin.md](checkin.md#共通-auth_token)) |
| `FUN_002E7DEC` | スイッチ 0x51[0x2A4] (サービス終了モード) を読む ([checkin.md](checkin.md#6-サービス終了後のオフラインチェックイン)) |
| `FUN_001B53D4` | 16 文字のコードのデコード ([codes.md](codes.md)) |

- RTTI のクラス名 (`10CodeCommon`、`11FlagStamina`、`12ContentsInfo` など) が残っている。型情報 → vtable をたどると、各クラスの関数が見つかる。
- 通信: `la1.denpamen.com` の HTTPS (checkinserver / campaigncodeserver / gameserver / ctr_state / ctr_ec)。nn::boss は「タスクの登録解除」の文字列だけが見え、配信には使っていないと推定。

## 5. RPG3 との違い (まとめ)

| 項目 | RPG3 (oahu) | lanai |
|---|---|---|
| アーカイブ | version 7、ヘッダー 0xC | version 10、ヘッダー 0x18 |
| GS テーブル | 行だけ | 文字列・行 ID・欄の名前・再配置を持つ |
| メッセージ | GMSG、ID 範囲 | 表の中の UTF-16、表 + 行 ID |
| ルビ | 0x2B〜0x2D | 0x38〜0x3A (タグ形式) |
| エフェクト | CGFX | `.ptcl` (SPBD) |
| ステージ | マップ + イベントの表 | **コンテンツごとの CRO** + 表 |
| 遊び方 | 買い切り | スタミナ制。チェックインとコード入力で配信 |

## 6. 未解析
- `.gsc`、type 3 のマップの配置らしきバイナリ (`E4 1C B0 A2 …` で始まるもの)、`.ptcl`、`voice` の欄。
- 表の大半の欄。
- アーカイブの +0x08 / +0x0E とエントリの unk の意味。
