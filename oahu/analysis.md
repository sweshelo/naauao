# 電波人間のRPG3 (oahu) 解析メモ

RPG2 (kahara) のドキュメント (リポジトリのルート) と同じ書き方で、RPG3 の ROM を調べた結果をまとめる。RPG2 と比べた違いは各節の「RPG2 との違い」と §8 にまとめた。Panana の 2/3 両対応の検討は `oahu/panana-compat.md`。

## 1. ROM 基本情報

| | Base | Update |
|---|---|---|
| ファイル | `0004000E000EF000-v0.1.0.cia` | `0004000E000EF000-v4.7.0.cia` |
| タイトル ID (TMD) | `00040000000EF000` | `0004000E000EF000` |
| TitleVersion (TMD) | 0 | 4096 (= 4.0.0。ファイル名の v4.7.0 とは一致しない) |
| 製品コード | CTR-N-JDRJ | CTR-U-JDRJ |
| ExHeader の名前 | `oahu` | `oahu` |
| 暗号 | なし (NCCH flags[7] の NoCrypto) | なし |
| ExeFS | `.code` (LZ) / banner / icon / logo | `.code` / icon / logo (banner なし) |
| RomFS | 0xBFF7000 (約 192 MB、269 ファイル) | 0x627000 (約 6 MB、12 ファイル) |
| コンテンツ 1 | 電子説明書 (CFA, 0x159000) | 同じ |

- 開発コード名は **`oahu`** で確定 (ExHeader の名前)。`honolulu` は RPG3 自身ではなく、master にある `flagDataHonolulu.bin` の名前に出てくる (§4.3)。`kahara` (RPG2 の内部名) と並んでいるので、RPG2 より前の作品 (初代「電波人間のRPG」など) の内部名と推定。
- ExHeader (展開後の code.bin はセクションが連続していて、RPG2 と同じく base 0x100000 のフラットバイナリとして読める):

| | Base | Update |
|---|---|---|
| text | 0x00100000 (0x453CB8) | 0x00100000 (0x4558C0) |
| ro | 0x00554000 (0x401DC) | 0x00556000 (0x4023C) |
| data | 0x00595000 (0x3452C) | 0x00597000 (0x34568) |
| bss | 0x6FEA4 | 0x6F8E8 |
| code.bin (展開後) | 5,021,696 B | 5,029,888 B |

- CPU は RPG2 と同じ ARM11。依存するシステムモジュール (ExHeader の deps) も Base と Update で同じ。
- **実際に動くのは Update の code.bin。** アップデートを入れた状態でゲームが起動するのは Update の NCCH (ExeFS) なので、code.ips やアドレスはすべて Update (TitleVersion 4096) の code.bin を基準にする。

## 2. 展開手順

`oahu/tools/` の Python スクリプトで、ctrtool や boot9 なしで展開できる (どちらも復号済みの CIA が前提)。

```
python3 oahu/tools/ctr.py info  base.cia update.cia            # CIA / TMD / NCCH / ExHeader の要約
python3 oahu/tools/ctr.py extract base.cia   out/base           # exheader.bin, exefs/code.bin (展開済み), romfs/
python3 oahu/tools/ctr.py merge base.cia update.cia out/merged  # ゲームから見える状態 (§3) を 1 つのフォルダに
python3 oahu/tools/gsarc.py catalog out/merged/romfs            # ルートのアーカイブの一覧
python3 oahu/tools/gsarc.py list|unpack <archive> [outdir]
python3 oahu/tools/gsmb.py <file.gsmb> [ID ...]
python3 oahu/tools/armdis.py out/merged/exefs/code.bin <addr> [count]   # capstone が必要
```

- `merge` の出力 (`exheader.bin` / `exefs/code.bin` / `romfs/`) は、RPG2 の `extracted/` と同じ形 (code.bin + RomFS のルートファイル) なので、Panana のフォルダ入力 (`openFolder`) の形にもそのまま合う。
- ROM 本体と展開したデータはリポジトリに入れない。

## 3. Base と Update のマージ (確定)

### 3.1 ゲームのしくみ: `rom:` と `patch:` の 2 段
Update の RomFS は**差分だけ** (アーカイブ 11 個 + `patchList.bin`)。ゲームは Base の RomFS を `rom:`、Update の RomFS を `patch:` にマウントし、ルートファイルごとにどちらを開くかを決める。

- 起動時 (`FUN_00495fd0`、Update の code.bin) に `FUN_002cb430(*0x5A59DC, L"patch:/patchList.bin")` がリストを読む。ファイルが開けなければ何もしない (リストは空のまま)。
  - 置き場所: リソース管理 (`*0x5A59DC`) の +0x80 = ハッシュの配列 (malloc)、+0x84 = 件数。
- `patchList.bin` の形式: `u32 件数, u32 ハッシュ × 件数`。v4096 の中身 (11 件): `21350000 3B630000 A9DF0000 296B0000 97CF0000 7BF70000 619D0000 838B0000 58190000 00910000 6E380000`。
- パスを作る関数 `FUN_0011ad1c(hash)` (Update): ハッシュがリストにあれば `L"patch:/XXXXXXXX"` (0x5A5A1E)、なければ `L"rom:/XXXXXXXX"` (0x5A5A00) を返す。Base の同じ関数 (`FUN_0011acec`) は `rom:/` しか作らない (Base の code.bin には `patch:` の文字列自体がない)。
- つまり**置き換えの単位はルートのアーカイブ 1 個まるごと**。アーカイブの中のエントリ単位の差分ではない。

### 3.2 Update で変わったもの (v0 → v4096)
11 アーカイブとも、エントリ数・ハッシュは Base と同じで、中身が変わったエントリだけが違う。

| アーカイブ | 変わったエントリ |
|---|---|
| 21350000 (master) | font_hamming_14 / 08.nftr、MessageSystemCommon_JP(_IN).gsmb、MessageBattle_JP.gsmb、**actionData.bin**、**monsterGroup.bin**、**conditionData.bin** |
| 00910000 | MessageAntenna_JP.gsmb |
| 296B0000 | font_rr_shadow_16.nftr |
| 3B630000 / 58190000 / 619D0000 / 838B0000 | MessageCommand_JP.gsmb (4 つとも同じ内容。RPG2 と同じく 4 か所に入っている) |
| 6E380000 | MessageNagomi_JP(_IN).gsmb、nagomiCatchItem.bin |
| 7BF70000 | title.arc (タイトル画面のレイアウト) |
| 97CF0000 | m10_EventObject.bin |
| A9DF0000 | MessageField_JP.gsmb |

→ バランス調整 (ワザ・状態・出現する敵)、テキスト修正、イベント 1 か所、タイトル画面。ゲームデータの解析は **Update 側を正**とする。

### 3.3 マージと配り方 (4 通り)

| 方法 | やること | 用途 | 確認 |
|---|---|---|---|
| A. 仮想マージ | Base の RomFS を読み、`patchList.bin` にあるハッシュだけ Update の RomFS から読む。code.bin は Update | 解析・Panana の読み込み | `ctr.py merge` で実装。ゲームのパス選択 (§3.1) と同じ規則 |
| B. LayeredFS (CIA は作り直さない) | Base と Update を両方インストールし、MOD のファイルを `luma/titles/00040000000EF000/romfs/` (Azahar は `load/mods/00040000000EF000/romfs/`) に置く | MOD の配布・実機 | 下記のソースで確認。実機・Azahar での動作は未確認 |
| C. 1 本の CIA に焼く | Base の NCCH の ExHeader と ExeFS を Update のものにし、RomFS を A の結果で作り直して CIA にする (`ctrbuild.py applied`) | アップデートなしで遊べる 1 本にしたいとき | ハッシュまで検証済み、起動は未確認 (`oahu/update.md`) |
| D. MOD を Update として配る | 公式 Update + 変えたアーカイブ + 作り直した patchList.bin で、TitleVersion を上げた Update CIA を作る (`ctrbuild.py update`) | LayeredFS なしで MOD を入れる | 同上 (`oahu/update.md`) |

B と D が MOD の配り方の候補 (D の詳細は `oahu/update.md`)。B について:
- Luma3DS の LayeredFS は、code.bin に `\0patch:` があればそれを「Update の RomFS」のマウント名とみなし、`rom:` と `patch:` の両方のパスを SD の `romfs/` に振り替える (sysmodules/loader `patcher.c` の `updateRomFsMounts`、`romfsredir.s` の `fsRedir`。SD にファイルがなければ元のアーカイブから開く)。フォルダ名はアップデートの ID ではなく、Base のタイトル ID (`00040000000EF000`)。
- Azahar も、Update の NCCH (`0004000E...`) に対して `GetModId` で `0004000E` → `00040000` に読み替え、同じ `mods/00040000000EF000/` を Base と Update の両方の RomFS に重ねる (`src/core/file_sys/ncch_container.cpp`)。`exefs/code.ips` もこのフォルダ。
- どちらの場合も、MOD に入れたアーカイブは `rom:` / `patch:` のどちらで開かれても MOD 側が使われる。**MOD に入れるアーカイブは Update 版を元に作る** (patchList の 11 個は Base 版を元にすると、アップデートの修正が消える)。
- code.ips は Update の code.bin (v4096) のアドレスで書く。

C の注意 (詳細は `oahu/update.md`):
- Update の RomFS だけを使う方法 (アップデートが RomFS を丸ごと持つゲーム向けの一般的な手順) は**使えない**。RPG3 の Update の RomFS は差分だけなので、ほとんどのデータが欠ける。
- 焼いた CIA には `patch:` がないので、`patchList.bin` の読み込みは失敗してリストは空になり、全部 `rom:` から読まれる (§3.1 のコードでは失敗を無視する)。ただし、焼いた CIA と本物の Update を同時に入れると、`patch:` 側 (公式の Update) が優先される。
- 実機・Azahar での起動は未確認。

## 4. RomFS

### 4.1 ルートの構成
- ルートのファイル 176 個は 8 桁 16 進のハッシュ名。**下位 16 ビットが必ず 0** (例 `21350000`)。ほかに `sound/` (sound.bcsar、stream/ の BGM 56 曲 .bcstm、voice/ の音声合成データ)、`shaders/`、`proctex_files/` (水・溶岩などのプロシージャルテクスチャ) がある。
- **RPG2 との違い**: RPG2 のルートは 32 ビットのハッシュ (`56562135` など)。RPG3 の名前は **RPG2 のハッシュの下位 16 ビットを上に寄せたもの**になっている。master: RPG2 `56562135` → RPG3 `21350000`、MessageCommand の 4 アーカイブ: RPG2 `1D37838B / 49A43B63 / 91B0619D / BACF5819` → RPG3 `838B0000 / 3B630000 / 619D0000 / 58190000`。

### 4.2 アーカイブの形式 (確定)
RPG2 の形式 (`analysis.md`「RomFS」) とヘッダー・エントリの並びは同じ。違いは version と +0x14 の値だけ。

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
RPG2 の `56562135` に当たる。GS テーブル (type 9 / 0) 92 個、GMSG 3 個、フォント、共通レイアウトなど。主な GS テーブル (行数 × 行サイズ。RPG2 の値は `analysis.md` / `battle.md` などから):

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
| soundData.bin | 597 × 0xC | |
| flagData.bin | 259 × 0x10 | |
| vendor.bin | (type 0、64488 B) | (type 0) |

- ほかに RPG3 で増えたもの: 釣り (`fishData` / `fishingHook` / `fishingPoint` / `fishingRod` / `fishingLevel`)、植物 (`plantInfo` / `plantMap` / `plantPoint`)、なごみ (`nagomiHouseList` / `nagomiCatchList` / `nagomiTownList`)、電波人間の作成 (`createSelect*` 16 個)、`denpaCustom`、`reBossInfo`、`insideInterior`、`designedMap` など。
- `flagDataHonolulu.bin` (87 × 0x10) / `flagDatakahara.bin` (150 × 0x10) と、それぞれの `flagDataLevel*`: 前作 (honolulu) と RPG2 (kahara) の、名前付きのフラグ表。前作のセーブとの連動に使うと推定 (未確認)。
- GS テーブルのヘッダー (`analysis.md`「GS テーブル形式」) は同じ (+0x00 行数、+0x04 行サイズ、+0x10 データ開始、+0x30 テーブル名)。+0x20 が 0 でないテーブル (mapData、treasureGroup、monsterGroup など) は、行の後ろに追加の領域がある (中身は未解析)。
- **行の中身は RPG2 と違う。** 欄の並びは作り直し (§6)。

### 4.4 マップ・イベントのアーカイブ
- ダンジョン・町ごとに 2 エントリのアーカイブ (`d10_EventObject.bin` + `d10_StaticEvent.bin` など) が 82 組ある。接頭辞: d10〜d90、e01〜e03、f20〜f92、h01、i01〜i24、k01〜k03、m10〜m90、s11〜s70、w01。
- EventObject は **0x58 バイト** (RPG2 は 0x50)。StaticEvent は 4 バイト × n。
- ワールドマップ: master の `W01_ground.bin` (type 0) と `worldmapParts` / `worldmapPort`。

## 5. メッセージ (GMSG)
形式は RPG2 と同じ (`analysis.md`「GMSG (.gsmb) メッセージ」: ヘッダー、ID 範囲、オフセット表、種別コード 1 文字 + 本文 + 0x0000)。違いは ID の振り方とタグ番号。

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

### monsterParameter.bin (201 × 0x70)
- RPG2 と同じくビット詰め。+0x40 = 名前 (例 行 1「はなもぐら」)、+0x44 = 説明。RPG2 では名前は別アーカイブの MonsterDesign にあったが、RPG3 では MonsterParameter が直接メッセージ ID を持つ。

### conditionData.bin (125 × 0x3C)
- +0x00 リソースハッシュ (アイコンと推定)、+0x0C 以降に「しかし どくにはならなかった」などのメッセージ。

## 7. code.bin (Update, v4096)
| アドレス | 内容 |
|---|---|
| `0x5A59DC` | リソース管理のポインタ (+0x80 / +0x84 = patchList) |
| `FUN_0011ad1c` | ルートファイルのパス (`rom:/` か `patch:/`) を作る (§3.1) |
| `FUN_002cb430` | `patch:/patchList.bin` を読む |
| `FUN_002cb4d0` | ハッシュでアーカイブを開く (起動時に `0x21350000` = master を開く、`FUN_00495fd0` 内) |
| `FUN_00495fd0` | 起動時の初期化 (patchList → master の読み込み) |
| `0x5A5A00` / `0x5A5A1E` | `L"rom:/XXXXXXXX"` / `L"patch:/XXXXXXXX"` のバッファ |

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
- 各 GS テーブルの欄 (§6 は一部だけ)、vendor.bin、mapParts などのマップの区画。
- type 8 / 10 の BCH の中身 (マップのパーツ・モデル)。0x180 バイトのヘッダーの意味。
- メッセージのタグの全体 (`0x2B〜0x2D` 以外)。
- flagDataHonolulu / kahara の用途。
- マージ方法 B / C の実機・Azahar での動作確認。
