# 3DS のアップデートの仕組みと、CIA の書き出し

目的: RPG3 の **Update を適用済みの CIA** を書き出すこと、**MOD を Update として配る**こと。既存の解析記録では、どちらも作り方を特定し、ツール (`roms/tools/ctrbuild.py`) で実データから作れるところまで確認した。実機・Azahar での起動は未確認 (§5)。

## 1. 3DS のアップデートの仕組み

- アップデートは**別のタイトル**として入る。タイトル ID の上位が `00040000` → `0004000E` に変わるだけで、下位 (`000EF000`) は同じ。中身は普通の CIA (チケット・TMD・NCCH)。
- 起動するとき、システムは同じ下位 ID の Update が SD にあれば、**ExHeader と ExeFS (code.bin) を Update の NCCH から**読む。RomFS は 2 つとも見える:
  - Base の RomFS = SelfNCCH アーカイブのパス種別 0 (`RomFS`)
  - Update の RomFS = パス種別 5 (`UpdateRomFS`)
  - Azahar の実装 (`loader/ncch.cpp` の `overlay_ncch` と `ReadUpdateRomFS`、`file_sys/archive_selfncch.cpp`)。Update がないとき、Azahar は種別 5 を Base の RomFS で代用する。
- **RomFS をどう使うかはゲーム次第。** Update の RomFS に全部を入れて Base を使わないゲームもあるが、RPG3 は差分方式: Base を `rom:`、Update を `patch:` にマウントし、`patch:/patchList.bin` にあるルートファイルだけ `patch:` から読む (本書「ゲームによる差分選択と配布方式」3.1、`FUN_0011ad1c`)。
- Update の ExHeader は Base とほぼ同じで、違うのは remaster version (+0x0E: 0 → 4)、jump ID (+0x1C8: Update のタイトル ID)、セクションのサイズ、署名つきの部分。ARM11 のプログラム ID (+0x200) は Base のまま (`00040000000EF000`)。
- 本書で解析した公式 Update は TitleVersion 4096。eShop の販売終了だけから、更新の最終版や将来の上書き可能性は断定しない。異なる版を扱う場合は TMD と実データを確認する。

## 2. 2 つの CIA の作り方

### 2.1 Update 適用済みの CIA (タイトル 00040000000EF000)
| 部分 | 中身 |
|---|---|
| NCCH ヘッダー | Base のもの (製品コード CTR-N-JDRJ、プログラム ID は Base)。サイズ・ハッシュは作り直し |
| ExHeader | **Update のもの**、jump ID だけ Base のタイトル ID に戻す |
| ExeFS | **Update の .code / icon / logo** + Base の banner (Update には banner がない) |
| RomFS | Base の RomFS に、Update の `patchList.bin` にある 11 アーカイブを Update 版で上書き。`patchList.bin` 自体は入れない |
| CIA | Base の CIA のチケット・証明書・TMD・メタを使い、コンテンツの SHA-256 とサイズを入れ直す。TitleVersion は 4096。コンテンツ 1 (電子説明書) はそのまま |

- 入れた状態では Update がないので `patch:/patchList.bin` が読めず、リストは空 → 全部 `rom:` から読む。中身はマージ済みなので、Update を入れた状態と同じデータになる。
- **公式の Update は消しておく。** 残っていると ExeFS と 11 アーカイブが公式 Update 側から読まれる (中身が公式どおりなら害はないが、MOD を焼いた場合は 11 アーカイブ分が公式に戻る)。
- MOD を焼くこともできる (`--romfs` のフォルダのファイルを RomFS に上書き、`--code` で code.bin を差し替え)。ただし 200 MB の CIA を毎回配ることになる。

### 2.2 MOD を Update として配る (タイトル 0004000E000EF000)
| 部分 | 中身 |
|---|---|
| NCCH / ExHeader / ExeFS | 公式 Update のもの。code.bin を変えるときは無圧縮の code.bin を入れ、ExHeader の圧縮フラグ (+0x0D bit0) を落とす |
| RomFS | 公式 Update の 11 アーカイブ + **MOD で変えたルートファイル** (Base にあるアーカイブでもよい) + 作り直した `patchList.bin` (RomFS にあるすべての 8 桁ハッシュのファイルを列挙) |
| CIA | 公式 Update の CIA を元に、TitleVersion を **4096 より大きく** (例 4112 = 4.1.0)。ExHeader の remaster version も合わせて上げる |

- `patch:` はルートのアーカイブ単位で何でも差し替えられるので、**MOD は変えたアーカイブだけを持てばよい**。テスト MOD (§4) の Update CIA は 10.4 MB (公式 Update とほぼ同じ)。
- 入れ方は普通の Update と同じ (FBI でインストール、Azahar は「CIA をインストール」)。Base はそのまま使える。**LayeredFS も code.ips も要らない。**
- 戻すときは MOD の Update を消して、公式の Update CIA を入れ直す。
- Update のタイトルは 1 つしか入らないので、**MOD を 2 つ同時に入れることはできない**。複数の MOD を使うなら、利用する MOD 作成ツールで 1 つの Update にまとめて書き出す。
- MOD の Update には公式 Update のデータ (11 アーカイブ) が入る。配布用の CIA をそのまま公開すると公式データを含むことになるので、利用者の手元のダンプから作成する形 が無難。

### 2.3 署名
- NCCH ヘッダー・TMD・チケットの RSA 署名はテンプレートのものをそのまま残すので、**正しくない**。署名を確認しない環境 (Luma3DS のカスタムファームウェア + FBI、Azahar) でしか入らない。これは自作 CIA 全般と同じ条件。
- 署名以外のハッシュ (TMD のコンテンツの SHA-256、コンテンツ情報、ExHeader、ExeFS、RomFS の IVFC 3 段) はすべて計算し直している (§3)。インストール時 (AM) と読み込み時 (FS) はこれらを確認する。

## 3. ツールと検証

この節の実データ検証は移設元の解析記録。今回の再編で再実行した範囲は [検証記録](verification.md) を参照。
```
python3 roms/tools/ctrbuild.py applied base.cia update.cia out-applied.cia [--romfs DIR] [--code code.bin]
python3 roms/tools/ctrbuild.py update  update.cia out-update.cia --version 4112 [--romfs DIR] [--code code.bin]
python3 roms/tools/ctr.py verify out.cia     # TMD・NCCH・ExeFS・IVFC のハッシュを全部確認
```
- `ctrbuild.py` は RomFS (レベル 3 + IVFC のハッシュ木)、ExeFS、NCCH、CIA を Python だけで組み立てる (makerom / 3dstool 不要)。他のツールへ移植する際の参照実装にもなる。
- 今回の再検証とCLI・構築関数の違いは [検証記録 §3](verification.md) を参照。CLI の `update` は patchList をソートするため、同じ版番号でも元CIAとの完全一致にはならない。
- 確認したこと:
  - 公式の Update CIA を、元の `patchList.bin` の順序を保持して構築関数で組み立て直すと、**CIA 全体がバイト単位で元と一致**する (RomFS・ExeFS・NCCH・TMD のハッシュの計算が正しい)。
  - Base の RomFS は、レベル 3 のファイルの並び順だけが元と違う (中身・ディレクトリ構造は同じ。並び順はゲームの動作に関係しない)。
  - `applied` / `update` で作った CIA は `ctr.py verify` ですべて ok。`applied` の RomFS の 269 ファイルは `ctr.py merge` の結果と全部一致。

## 4. テスト MOD
`roms/tools/testmod.py update.cia DIR` は、アイテム 1「キズぐすり」(メッセージ 0x4B2) の名前を「ＭＯＤぐすり」に変えた master (`21350000`) を DIR に作る。

```
python3 roms/tools/testmod.py update.cia testmod
python3 roms/tools/ctrbuild.py update update.cia mod-update.cia --version 4112 --romfs testmod
```
- 確かめ方: Base を入れ、公式 Update の代わりに `mod-update.cia` を入れて、店やもちものでキズぐすりの名前が変わっているかを見る。
- 同じ DIR で `applied` を作れば、焼いた CIA の確認にもなる。

## 5. 未確認
- 実機 (Luma3DS + FBI) と Azahar で、2 つの CIA がインストール・起動できるか。この環境ではエミュレータを動かせないので未確認。§4 のテスト MOD で確かめられる。
- 実機で Update がないときに、SelfNCCH の種別 5 (`patch:`) が失敗するのか Base を返すのか。どちらでも `applied` は動く見込み (失敗ならリストが空、Base を返しても `patchList.bin` がない)。
- TitleVersion を公式より上げた Update を、HOME メニューやすれちがい通信がどう扱うか (code.bin の `m_gameVersion` / `incompatible version` が通信の互換確認に関係するかもしれない)。

## ゲームによる差分選択と配布方式

以下は旧 `oahu/analysis.md` §3 の記録。関数アドレスは Update v4096（Base と明記したものを除く）を対象とする。

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
| A. 仮想マージ | Base の RomFS を読み、`patchList.bin` にあるハッシュだけ Update の RomFS から読む。code.bin は Update | 解析・ツールの読み込み | `roms/tools/ctr.py merge` で実装。ゲームのパス選択 (§3.1) と同じ規則 |
| B. LayeredFS (CIA は作り直さない) | Base と Update を両方インストールし、MOD のファイルを `luma/titles/00040000000EF000/romfs/` (Azahar は `load/mods/00040000000EF000/romfs/`) に置く | MOD の配布・実機 | 下記のソースで確認。実機・Azahar での動作は未確認 |
| C. 1 本の CIA に焼く | Base の NCCH の ExHeader と ExeFS を Update のものにし、RomFS を A の結果で作り直して CIA にする (`ctrbuild.py applied`) | アップデートなしで遊べる 1 本にしたいとき | ハッシュまで検証済み、起動は未確認 (本書 §2–5) |
| D. MOD を Update として配る | 公式 Update + 変えたアーカイブ + 作り直した patchList.bin で、TitleVersion を上げた Update CIA を作る (`ctrbuild.py update`) | LayeredFS なしで MOD を入れる | 同上 (本書 §2–5) |

B と D が MOD の配り方の候補 (D の詳細は 本書 §2–5)。B について:
- Luma3DS の LayeredFS は、code.bin に `\0patch:` があればそれを「Update の RomFS」のマウント名とみなし、`rom:` と `patch:` の両方のパスを SD の `romfs/` に振り替える (sysmodules/loader `patcher.c` の `updateRomFsMounts`、`romfsredir.s` の `fsRedir`。SD にファイルがなければ元のアーカイブから開く)。フォルダ名はアップデートの ID ではなく、Base のタイトル ID (`00040000000EF000`)。
- Azahar も、Update の NCCH (`0004000E...`) に対して `GetModId` で `0004000E` → `00040000` に読み替え、同じ `mods/00040000000EF000/` を Base と Update の両方の RomFS に重ねる (`src/core/file_sys/ncch_container.cpp`)。`exefs/code.ips` もこのフォルダ。
- どちらの場合も、MOD に入れたアーカイブは `rom:` / `patch:` のどちらで開かれても MOD 側が使われる。**MOD に入れるアーカイブは Update 版を元に作る** (patchList の 11 個は Base 版を元にすると、アップデートの修正が失われる)。
- code.ips は Update の code.bin (v4096) のアドレスで書く。

C の注意 (詳細は 本書 §2–5):
- Update の RomFS だけを使う方法 (アップデートが RomFS を丸ごと持つゲーム向けの一般的な手順) は**使えない**。RPG3 の Update の RomFS は差分だけなので、ほとんどのデータが欠ける。
- 焼いた CIA には `patch:` がないので、`patchList.bin` の読み込みは失敗してリストは空になり、全部 `rom:` から読まれる (§3.1 のコードでは失敗を無視する)。ただし、焼いた CIA と本物の Update を同時に入れると、`patch:` 側 (公式の Update) が優先される。
- 実機・Azahar での起動は未確認。
