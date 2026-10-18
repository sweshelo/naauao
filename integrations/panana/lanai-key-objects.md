# Panana: lanai の重要オブジェクトの直し方 (修正方針)

対象: Panana `main` (2026-10-18 時点、PR #137 マージ後) の lanai マップページ。解析の内容は [lanai/key-objects.md](../../lanai/key-objects.md)。ここには、今の表示のどこが誤っているかと、直すときに触る場所・順番を書く。実装はまだしていない。

## 1. 今の表示の誤り

| もの | 今の Panana | 正しくは |
|---|---|---|
| 会話のあとのボス戦の姿 (区画 5 種類 1) | MapChara +0x2C を MapObject の行として読み、`obj_towerB_stand00` (まおう) や `twn_bill41` のような無関係のモデルを置く (`src/lanai/mapObjects.ts` の `lanaiRecordLook` case 5 → `lanaiCharaObject`) | MapChara の種類 (+0x00 の下位 3 ビット) が 1 なら +0x2C は MonsterDesign の行番号。モンスターのモデルを置く |
| ボス戦の範囲 (区画 8、型 0x8000000C) | 動作の型が「型 8000000C」と出るだけ | 「ボス戦」。引数 1 = MonsterGroup の行番号、引数 2 = 勝つと立つフラグ |
| ゴールの宝箱 (区画 4 見た目 3) | 見た目 3 が `CHEST_IDS` (3 つ) の範囲外なので見た目 0 の `gimk_05_trebox_1` に丸める | MapObject 行 70 `gimk_05_trebox_goal` (行 ID 0x80000274)。外・屋内とも (確定: `FUN_0044F9EC`) |
| ゴールの宝箱の中身・クリア | 型 0x8000002E は `LANAI_CHEST_ACTIONS` にないので、宝箱の中身の編集 (`TreasureEditor`) が出ない。クリアにするコンテンツや台詞の欄もない | 段ごとに TreasureGroup の行 (引数 1)、段 1 のクリアにするコンテンツ (引数 2)、開けた後の台詞 (引数 3) |
| クリアのワープ (区画 3 種類 3) | 種類が「種類 3」、型が「型 80000031」と出る。EO +0x5A = 0 なのでモデルなし、扉と同じく向きの方へ 100 ずらす | 「クリアのワープ」。引数 1 = クリアにするコンテンツ、引数 5 = 1 なら確認の「はい」のあと。**モデルはなく**、EffectData 行 0x22 `fx_bg_f_warpzone_goal.ptcl` のエフェクトを置く。EO +0x5A は見ない (確定: `FUN_0021D744`) |
| 回復ポイント (区画 5 種類 13、型 0x80000030) | 「未解析 (0x30)」、モデルなし | 「回復ポイント」(HP / MP 全回復、クリアとは無関係)。**モデルはなく** EffectData 行 0x27 `fx_bg_repair_point.ptcl`。種類 12 は行 0x26 `fx_bg_repair_field.ptcl` (確定: `FUN_0021C844`) |

## 2. 直す場所

### 2.1 ボスの姿 (確定の内容だけで直せる)

1. `src/lanai/mapObjects.ts`
   - `LanaiRecordModel` に `{ type: 'monster'; design: number }` を足す (RPG3 の `src/oahu/mapObjects.ts` の `OahuRecordModel` と同じ形)。
   - `lanaiRecordLook` の case 5 (`kind <= 2`): MapChara の行の種類 (`LANAI_CHARA_KIND` の判定、+0x00 & 7) が 1 なら `{ type: 'monster', design: u16(+0x2C) }`、それ以外は今どおり MapObject。関数 `lanaiCharaModel(mapChara, chara)` に分けると MapPage と共有できる。
2. `src/lanai/mapview.ts`
   - `modelKey` / `loadModel` / `modelName`: `type === 'monster'` のとき `lanaiMonsterDesign` (`src/lanai/monsters.ts`) と `lanaiMonsterSet` (`src/lanai/monsterModels.ts`) で読む。キーは `m<design>`。
   - `sync3d` の `model.scale.setScalar(lanaiObjectScale(…, look.model.row))`: モンスターでは MapObject の倍率を使わない (1 で始め、実機と見比べる)。
3. `src/lanai/MapPage.tsx` の `ModelLine`: モンスターのとき「MonsterDesign #193 (まおう)」のように出す。名前は `lanaiMonsters` のうち `designRow` が一致するもの。
4. テスト `test/lanai-mapobjects.test.ts`: 「キャラクターは `npc_` のモデル」の割合の期待を、種類 1 を除いて数えるように直し、種類 1 の姿が近くの型 0C の群れのモンスターと一致する件数 (今のデータで 59 / 70 組) を確かめる ROM テストを足す。

### 2.2 動作の型の名前と引数 (`src/lanai/actions.ts`)

`LANAI_ACTIONS` に足す (`MapPage.tsx` の `ActionFields` が名前・引数の欄・台詞の選択を出す):

| 型 | name | talk | args |
|---|---|---|---|
| 0x8000000C | ボス戦 (範囲に入ると戦う) | なし | 0: MonsterGroup の行番号、1: 勝つと立つフラグ、2: 未解析 |
| 0x8000002E | ゴールの宝箱 (開けるとクリア) | [2] | 0: TreasureGroup の行、1: クリアにするコンテンツ (段 1 だけ、0 = なし)、3: モーション (推定)、4: 未解析 |
| 0x80000031 | クリアのワープ | [1] (推定) | 0: クリアにするコンテンツ、1: 台詞 (推定)、2: モーション (推定)、3: 未解析、4: 確認してからクリア (1 = 確認の台詞 0x80000396 で「はい」のとき) |
| 0x80000039 | ワープ (行き先あり) | なし | 0: 行き先のマップ (ハッシュ)、1: 行き先の地点 ID |

あわせて `0x80000030` の name を「回復ポイント」、note を「区画 5 の種類 13 専用。HP / MP を全回復する。クリアにはしない」に直す。

引数を数値ではなく選べるようにする欄 (`ActionFields` の `known.map` の手前に型ごとの分岐を足す):
- MonsterGroup の行番号: 今の `MonsterGroupSelect` (`src/lanai/MapParts.tsx`) は**行 ID** を返すので、行番号を返す版 (`MonsterGroupRowSelect`) を足す。
- クリアにするコンテンツ: `lanaiContents` (`src/lanai/contents.ts`) と `contentTitle` で「34: 駆け出し者への土の試練」と選べるようにする。今のコンテンツ以外を選んだら注意を出す (バニラでは全件が自分の番号)。

### 2.3 ゴールの宝箱 (`src/lanai/treasure.ts`、`src/lanai/MapParts.tsx`)

1. `LANAI_CHEST_ACTIONS` に 0x8000002E (ゴールの宝箱) を足す。
2. `lanaiChestField` は最初の宝箱の動作だけを返す。型 2E は段ごとに別の TreasureGroup の行を持つので、**段 (動作 1〜3) ごとの欄の一覧**を返す関数 (`lanaiChestFields`) に変え、`lanaiChestTreasureRow` / `lanaiChestUsers` も段ごとに数える。
3. `TreasureEditor`: 段が複数あるとき「初回 / 2 回目 / 3 回目以降」の見出しで中身を並べる。段 1 の上に「クリア判定」の行 (クリアにするコンテンツの選択、§2.2) を出す。台詞 (引数 3) は `ActionFields` の台詞の欄で編集できる。
4. `src/lanai/mapObjects.ts` の case 4: 見た目 3 → `byId(0x274)` (外・屋内とも、確定)。見た目 0〜3 以外は今どおり見た目 0 (外 0x34 / 屋内 0x37) に丸める (実機と同じ)。
5. `src/lanai/mapedit.ts` の `lanaiRecLabel` case 4: 見た目 3 は「ゴールの宝箱」。

### 2.4 クリアのワープと回復ポイント: エフェクトの印 (`src/lanai/maps.ts`、`src/lanai/mapObjects.ts`、`src/lanai/mapview.ts`)

どちらも実機はモデルを置かずエフェクト (ptcl) を出す。Panana はエフェクトを描けないので、**「モデルなし」をはっきり示す**形にする。

1. `LANAI_EXIT_KIND` に `3: 'クリアのワープ'` を足す (`lanaiExitLabel`、`lanaiRecLabel`、2D の印の説明に出る)。
2. `LanaiRecordModel` に `{ type: 'effect'; row: number; name: string }` を足し、`lanaiRecordLook` で次を返す。EO +0x5A は見ない (実機と同じ)。
   - case 3 種類 3 → EffectData 行 0x22 (`fx_bg_f_warpzone_goal`)。向きは付けず、扉のように 100 ずらさない (マスの中央)。
   - case 5 種類 13 → 行 0x27 (`fx_bg_repair_point`)。種類 12 → EO +0x5A があればその MapObject、なければ行 0x26 (`fx_bg_repair_field`)。
   - 名前は master +0x1E4 (`effectData.bin`) の表から引く関数を足す (読めなければ番号だけ出す)。
3. `src/lanai/mapview.ts`: `type === 'effect'` は 3D に半透明の円柱など決まった目印を置き、`modelName` は「エフェクト: fx_bg_f_warpzone_goal」と出す。`MapPage.tsx` の `ModelLine` も同じ文字を出す。
4. 2D の印 (`src/editor/view2d.ts` の区画 3 の形) は、種類 3 をワープの形 (ひし形) にする。区画 5 種類 13 は「回復ポイント」と出す。

## 3. 順番

1. §2.1 ボスの姿 と §2.2 の名前 (確定の内容だけ。見た目がいちばん大きく直る)。
2. §2.3 ゴールの宝箱 (中身の段・クリア判定の UI)。
3. §2.4 クリアのワープと回復ポイント。

見た目を選ぶ処理は code.bin で確かめ済み ([lanai/key-objects.md §2.2 / §3.2 / §4](../../lanai/key-objects.md#4-クリア済みの記録-確定-コード))。残る推定は動作の引数の一部だけ ([§5](../../lanai/key-objects.md#5-未解決))。

## 4. 確かめ方

- ROM テスト (CI の rom ジョブ、Panana の普段の ROM テストとして): ボスの姿が群れのモンスターと一致する件数、型 2E の段 1 の引数 2 と型 31 の引数 1 が自分のコンテンツ番号 (60 / 60、46 / 46)、見た目 3 のモデルの名前 (`gimk_05_trebox_goal`)、EffectData 行 0x22 / 0x27 の名前。
- 画面: コンテンツ 15 (魔女のアジト) の `D01001F04` (まおうの姿と範囲)、コンテンツ 34 の `D01001B01` (ゴールの宝箱)、コンテンツ 59 の `D01001B02` (クリアのワープ)。
