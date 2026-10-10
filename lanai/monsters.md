# モンスター (移植のための整理)

対象: lanai Base v0 + Update v17408。表は master `2135000A` (形式は [analysis.md §2](analysis.md#2-gs-テーブル-lanai-形式確定))。RPG3 の monsterParameter (201 × 0x70、ビット詰め、[oahu/analysis.md](../oahu/analysis.md)) とは行の形が違うので、欄を流用しない。

## 1. 表の構成

| 表 | 行 × サイズ | 内容 | 確度 |
|---|---|---|---|
| **MonsterParameter** (名前なし LZ、`4C2BD400`) | 1231 × 0x24 | 名前・群れの名前・見た目への参照 | §2 |
| MonsterParameterMain | 370 × 0x9C | 能力などの本体と推定 (本編) | 推定 |
| MonsterParameterExtra | 184 × 0x9C | 同上 (追加) | 推定 |
| MonsterParameterRegularEvent | 200 × 0x9C | 同上 (定期イベント) | 推定 |
| MonsterParameterSpecialEvent | 437 × 0x9C | 同上 (特別イベント) | 推定 |
| **MonsterDesign** | 570 × 0xA0 | モデル・テクスチャ・モーションと大きさ | §3 |
| MonsterBrain (`402F0000`) | 40 × 0x4 | 行動の選び方と推定 | 推定 |
| ActionData | 5017 × 0x2C | ワザ | |
| コンテンツの MonsterGroup | 0x9C × n | ステージの敵の群れ | |

0x9C の 4 表は合わせて 1191 行。MonsterParameter (1231 行) との対応 (どの欄がどの行を指すか) は未確定。0x9C の行には `0x34xxxxxx` / `0x68xxxxxx` で始まる値や、`0x8000xxxx` (行 ID) が並ぶ。

## 2. MonsterParameter (1231 × 0x24)

| off | 型 | 内容 | 確度 |
|---|---|---|---|
| 0x00 | u32 | ビット詰めの値 (例 いちごおばけ `0x1B200401`) | 未解析 |
| 0x04 | 文字列 | `name` (例「いちごおばけ」) | 確定 |
| 0x08 | 文字列 | `voice` | 確定 |
| 0x0C | 文字列 | `group_name` (例「いちごおばけたち」) | 確定 |
| 0x10 | u32 | **MonsterDesign の行 ID** | 確定 (§3 の例) |
| 0x14 | u16 × 2 | 未解析 | |
| 0x18 | u32 | 0x10 が多い | 未解析 |

## 3. MonsterDesign (570 × 0xA0)

| off | 型 | 内容 | 確度 |
|---|---|---|---|
| 0x08 | u32 | **モデル** (BCH のエントリのハッシュ。例 `78BFB000` = `enemy_01.bch`) | 確定 |
| 0x0C | u32 | **色違いのテクスチャ** (例 `F8D5D800` = `enemy_01_01_tex.bch`) | 確定 |
| 0x10 | u32 | **戦闘用のモーション** (例 `5C4E3400` = `enemy_01_battle.bch`) | 確定 |
| 0x20〜0x48 | f32 | 大きさ・距離と推定 (60.0、4.0、1.0、0.8 …) | 推定 |

例 (MonsterParameter → MonsterDesign → モデル):

| 行 | 名前 | MonsterDesign | モデル | テクスチャ |
|---:|---|---|---|---|
| 1 | いちごおばけ | `80000163` | enemy_59_05.bch | enemy_59_07_tex.bch |
| 4 | おおくちばし | `80000004` | enemy_02.bch | enemy_02_01_tex.bch |
| 50 | アイスバード | `80000006` | enemy_02.bch | enemy_02_03_tex.bch |
| 600 | だいまおう | `80000099` | enemy_38.bch | enemy_38_02_tex.bch |
| 1200 | むかしテンペスター | `8000013A` | enemy_03_07.bch | enemy_03_07_tex.bch |

- **色違いは、同じモデルにテクスチャを差し替えて作る** (おおくちばし / アイスバード)。

## 4. モデル
- 敵のモデルは `28480000` (Base、497 エントリ) と `719F0000` (Update、349 エントリ) の `enemy_NN[_MM].bch`・`enemy_NN_MM_tex.bch`・`enemy_NN_battle.bch`。基本の番号は enemy_01〜enemy_99 などで 104 種類ある。
- 形式は **BCH (H3D)**。RPG3 (oahu) の type 2 も BCH で、`enemy_03` のような同じ名付けがある。RPG2 (kahara) は CGFX。
- **移植の見込み (未検証)**:
  - RPG3 のモンスターは、BCH のまま `enemy_*` として足せる可能性がある。足したあと MonsterDesign → MonsterParameter → 能力の表と行を足す。
  - RPG2 のモンスターは、CGFX から BCH への変換が要る。
- エフェクトは `.ptcl` (SPBD) で、RPG3 の CGFX のエフェクトはそのままでは使えない。

## 5. 未解析
- 0x9C の能力の表の欄と、MonsterParameter との結び付き。
- MonsterParameter +0x00 のビット詰め。
- 戦闘のモーションの番号の割り当て (RPG2 の [kahara/monster-motion.md](../kahara/monster-motion.md) に当たる部分)。
