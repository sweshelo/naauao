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
| 0x00 bit0-9 | | 元のモンスターの番号と推定 (同じモンスターの重複の行が同じ値を持つ) | 推定 |
| 0x00 bit10-19 | | 重複でない行では bit0-9 と同じ、重複の行 (2 体目・3 体目のアイスドラゴンなど) では 0 | 観測 |
| 0x00 bit20-29 | | **MonsterDesign の行番号 (見た目)** (例 いちごおばけ `0x1B200401` → 0x1B2 = 434) | **確定 (§2.1)** |
| 0x04 | 文字列 | `name` (例「いちごおばけ」) | 確定 |
| 0x08 | 文字列 | `voice` | 確定 |
| 0x0C | 文字列 | `group_name` (例「いちごおばけたち」) | 確定 |
| 0x10 | u32 | `0x8000xxxx` の値。MonsterDesign の行 ID とは 1231 行中 40 行しか合わず、**見た目ではない** | 未解析 |
| 0x14 | u16 × 2 | 未解析 | |
| 0x18 | u32 | 0x10 が多い。**bit0 = 戦闘の待機に `002_` (animData の行 ID 0x8000005D) を使う** (`FUN_002EF3DC`。立つ 19 行はどれも `002_` のアニメを持つ)。ほかのビットは未解析 | bit0 確定 |

### 2.1 見た目の選び方 (確定)

ゲームは MonsterParameter の行を引いたあと、+0x00 の bit20-29 を取り出し (`lsl #2; lsr #22`)、MonsterDesign をその値で引く。値は 0x80000000 未満なので、表の行の検索 `FUN_0031C038` ([analysis.md §4](analysis.md#4-codebin-update-v17408)) は**行番号**として扱う。

- 場所 (Update の code.bin): `0x306E60`〜`0x306EA4`、同じ並びが `0x2B7EB4`〜`0x2B7EE4`。表の置き場 `*0x004EAE44` の +0x758 が MonsterParameter、+0x18D8 が MonsterDesign (読み込み `0x17C6D4` で、エントリのハッシュ `0x4C2BD400` / `0xC402F800` から決まる)。
- この行の +0x04 / +0x08 / +0x0C などを読むコードがある (`0x189090`、`0x1B68BC`、`0x1A557C`)。
- 照合: この規則で並べると、種族の名前ごとに 1 つのモデルに収まり、色のテクスチャが順に並ぶ (コウモリ enemy_01、鳥 02、キノコ 04、チョウ 05、ドラゴン 10、木 11、イノシシ 12 …)。描画しても名前と姿が合う (アイスドラゴンは竜、いちごおばけはイチゴ)。
- 以前の資料の「+0x10 = MonsterDesign の行 ID」で引くと、enemy_05 あたりから先の多くで別の種族の姿になる (ドラゴンが木、ドライウッドがイノシシ)。

## 3. MonsterDesign (570 × 0xA0)

| off | 型 | 内容 | 確度 |
|---|---|---|---|
| 0x08 | u32 | **モデル** (BCH のエントリのハッシュ。例 `78BFB000` = `enemy_01.bch`) | 確定 |
| 0x0C | u32 | **色違いのテクスチャ** (例 `F8D5D800` = `enemy_01_01_tex.bch`) | 確定 |
| 0x10 | u32 | **戦闘用のモーション** (例 `5C4E3400` = `enemy_01_battle.bch`) | 確定 |
| 0x20〜0x48 | f32 | 大きさ・距離と推定 (60.0、4.0、1.0、0.8 …) | 推定 |

例 (MonsterParameter +0x00 bit20-29 → MonsterDesign の行 → モデル):

| 行 | 名前 | MonsterDesign の行 | モデル | テクスチャ |
|---:|---|---:|---|---|
| 1 | いちごおばけ | 434 | enemy_74_01.bch | enemy_74_01_tex.bch |
| 4 | おおくちばし | 6 | enemy_02.bch | enemy_02_01_tex.bch |
| 50 | アイスバード | 8 | enemy_02.bch | enemy_02_03_tex.bch |
| 55 | アイスドラゴン | 73 | enemy_10_02.bch | enemy_10_02_tex.bch |
| 600 | だいまおう | 194 | enemy_30.bch | enemy_30_02_tex.bch |
| 1200 | むかしテンペスター | 391 | enemy_67.bch | enemy_67_01_tex.bch |

- 1231 行すべてが MonsterDesign の行を持つ (以前の引き方で「MonsterDesign にない ID」になった 183 行も含む)。

- **色違いは、同じモデルにテクスチャを差し替えて作る** (おおくちばし / アイスバード)。

## 4. モデル
- 敵のモデルは `28480000` (Base、497 エントリ) と `719F0000` (Update、349 エントリ) の `enemy_NN[_MM].bch`・`enemy_NN_MM_tex.bch`・`enemy_NN_battle.bch`。基本の番号は enemy_01〜enemy_99 などで 104 種類ある。
- 形式は **BCH (H3D)**。RPG3 (oahu) の type 2 も BCH で、`enemy_03` のような同じ名付けがある。RPG2 (kahara) は CGFX。
- H3D の版 (backward compatibility) は **0x21** (RPG3 は 8)。Panana で読むときに分かった違い (SPICA の版ごとの分岐と同じ向き):
  - 材質は 0x2C バイト。テクスチャの mapper は +0x18 のポインターの先、テクスチャ名 3 つと材質名が +0x1C〜+0x28。
  - アニメのカーブは 0x20 以降、segment がカーブの中にある (index の後ろに u8 補間・u8 量子化・u16 キー数・f32 値の倍率・f32 値のずれ・f32 フレームの倍率・f32 1/長さ)。
  - H3DAnimation の +0x04 が flags (bit0 = ループ)、+0x05 が種類。wait / walk / run はループし、ワザ・ダメージ・倒れるはループしない。
  - モデルの +0x01 (bone scaling) が 1 (Maya) で、骨の flags の bit22 (segment scale compensate) が腰より下の骨に立つ。この骨は親の大きさを回転・大きさに受け継がない (local = T × 親の大きさ⁻¹ × R × S)。舌の骨 (tongue_1〜3) などで効く。
  - 骨の番号が固定の属性 (頂点ごとでない) で、重みが頂点ごとに 4 個のメッシュがある (いちごおばけ・おばけとうがらしの舌)。固定の骨の番号も 4 個使わないと、4 個目の骨の重みが落ちて舌が伸びる。
- **移植の見込み (未検証)**:
  - RPG3 のモンスターは、BCH のまま `enemy_*` として足せる可能性がある。足したあと MonsterDesign → MonsterParameter → 能力の表と行を足す。
  - RPG2 のモンスターは、CGFX から BCH への変換が要る。
- エフェクトは `.ptcl` (SPBD) で、RPG3 の CGFX のエフェクトはそのままでは使えない。

## 5. 未解析
- 0x9C の能力の表の欄と、MonsterParameter との結び付き。
- MonsterParameter +0x00 の bit0-19・bit30-31、+0x10 の意味。
- 戦闘のモーションの番号の割り当て (RPG2 の [kahara/monster-motion.md](../kahara/monster-motion.md) に当たる部分)。
