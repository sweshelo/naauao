# 3DS のアップデートの仕組みと、CIA の書き出し

目的: RPG3 の **Update を適用済みの CIA** を書き出すこと、**MOD を Update として配る**こと。どちらも作り方を特定し、ツール (`oahu/tools/ctrbuild.py`) で実データから作れるところまで確認した。実機・Azahar での起動は未確認 (§5)。

## 1. 3DS のアップデートの仕組み

- アップデートは**別のタイトル**として入る。タイトル ID の上位が `00040000` → `0004000E` に変わるだけで、下位 (`000EF000`) は同じ。中身は普通の CIA (チケット・TMD・NCCH)。
- 起動するとき、システムは同じ下位 ID の Update が SD にあれば、**ExHeader と ExeFS (code.bin) を Update の NCCH から**読む。RomFS は 2 つとも見える:
  - Base の RomFS = SelfNCCH アーカイブのパス種別 0 (`RomFS`)
  - Update の RomFS = パス種別 5 (`UpdateRomFS`)
  - Azahar の実装 (`loader/ncch.cpp` の `overlay_ncch` と `ReadUpdateRomFS`、`file_sys/archive_selfncch.cpp`)。Update がないとき、Azahar は種別 5 を Base の RomFS で代用する。
- **RomFS をどう使うかはゲーム次第。** Update の RomFS に全部を入れて Base を使わないゲームもあるが、RPG3 は差分方式: Base を `rom:`、Update を `patch:` にマウントし、`patch:/patchList.bin` にあるルートファイルだけ `patch:` から読む (`analysis.md` §3.1、`FUN_0011ad1c`)。
- Update の ExHeader は Base とほぼ同じで、違うのは remaster version (+0x0E: 0 → 4)、jump ID (+0x1C8: Update のタイトル ID)、セクションのサイズ、署名つきの部分。ARM11 のプログラム ID (+0x200) は Base のまま (`00040000000EF000`)。
- 3DS の eShop は 2023 年 3 月に終了しているので、公式の Update は TitleVersion 4096 が最後になる (新しい公式版で MOD が上書きされる心配はない)。

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
- Update のタイトルは 1 つしか入らないので、**MOD を 2 つ同時に入れることはできない**。複数の MOD を使うなら、Panana 側で 1 つの Update にまとめて書き出す。
- MOD の Update には公式 Update のデータ (11 アーカイブ) が入る。配布用の CIA をそのまま公開すると公式データを含むことになるので、Panana がユーザーの手元のダンプから作る形 (いまの code.ips / RomFS の書き出しと同じ考え方) が無難。

### 2.3 署名
- NCCH ヘッダー・TMD・チケットの RSA 署名はテンプレートのものをそのまま残すので、**正しくない**。署名を確認しない環境 (Luma3DS のカスタムファームウェア + FBI、Azahar) でしか入らない。これは自作 CIA 全般と同じ条件。
- 署名以外のハッシュ (TMD のコンテンツの SHA-256、コンテンツ情報、ExHeader、ExeFS、RomFS の IVFC 3 段) はすべて計算し直している (§3)。インストール時 (AM) と読み込み時 (FS) はこれらを確認する。

## 3. ツールと検証
```
python3 oahu/tools/ctrbuild.py applied base.cia update.cia out-applied.cia [--romfs DIR] [--code code.bin]
python3 oahu/tools/ctrbuild.py update  update.cia out-update.cia --version 4112 [--romfs DIR] [--code code.bin]
python3 oahu/tools/ctr.py verify out.cia     # TMD・NCCH・ExeFS・IVFC のハッシュを全部確認
```
- `ctrbuild.py` は RomFS (レベル 3 + IVFC のハッシュ木)、ExeFS、NCCH、CIA を Python だけで組み立てる (makerom / 3dstool 不要)。将来 Panana (TypeScript) に移すときの参照実装にもなる。
- 確認したこと:
  - 公式の Update CIA を分解して組み立て直すと、**CIA 全体がバイト単位で元と一致**する (RomFS・ExeFS・NCCH・TMD のハッシュの計算が正しい)。
  - Base の RomFS は、レベル 3 のファイルの並び順だけが元と違う (中身・ディレクトリ構造は同じ。並び順はゲームの動作に関係しない)。
  - `applied` / `update` で作った CIA は `ctr.py verify` ですべて ok。`applied` の RomFS の 269 ファイルは `ctr.py merge` の結果と全部一致。

## 4. テスト MOD
`oahu/tools/testmod.py update.cia DIR` は、アイテム 1「キズぐすり」(メッセージ 0x4B2) の名前を「ＭＯＤぐすり」に変えた master (`21350000`) を DIR に作る。

```
python3 oahu/tools/testmod.py update.cia testmod
python3 oahu/tools/ctrbuild.py update update.cia mod-update.cia --version 4112 --romfs testmod
```
- 確かめ方: Base を入れ、公式 Update の代わりに `mod-update.cia` を入れて、店やもちものでキズぐすりの名前が変わっているかを見る。
- 同じ DIR で `applied` を作れば、焼いた CIA の確認にもなる。

## 5. 未確認
- 実機 (Luma3DS + FBI) と Azahar で、2 つの CIA がインストール・起動できるか。この環境ではエミュレータを動かせないので未確認。§4 のテスト MOD で確かめられる。
- 実機で Update がないときに、SelfNCCH の種別 5 (`patch:`) が失敗するのか Base を返すのか。どちらでも `applied` は動く見込み (失敗ならリストが空、Base を返しても `patchList.bin` がない)。
- TitleVersion を公式より上げた Update を、HOME メニューやすれちがい通信がどう扱うか (code.bin の `m_gameVersion` / `incompatible version` が通信の互換確認に関係するかもしれない)。
