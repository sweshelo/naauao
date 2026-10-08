# Panana の RPG3 対応に関する実装・検証記録

この文書は naauao の旧 oahu 文書から切り出した Panana 固有の実装、UI 方針、検証手段の記録。PR 番号は出典であり、現在の実装状況・完了予定を保証しない。ゲーム自体の仕様は [oahu](../../oahu/README.md) を参照。

## マップ表示

- W01 は最初の対応では読み取りだけにする、という実装方針があった。区画の相違は [マップ §8](../../oahu/map.md)。
- マップページで何も選ばないと、ヘッダーの群れ (選び直せる) とセルごとの群れが出る (panana#99)。

## 電波人間のプレビュー (panana#96)

- RPG2 の既存描画実装はなく、RPG3 の BCH と共有の three.js 描画・スキニングを利用する。
- mapChara 種類 3 は ROM だけを開く場合に denpaCustom #92 の姿を表示し、セーブ未読込と明示する。
- プレビューは素体の見た目を組み立てる。セーブ読込と装備の組み立ては別の対応。
- レベルが 0 のプレビューはセーブ未読込のため最初の習得段階を使う。
- 顔の UV 移動を Maya 形式の coordinator へ渡す際は、引き算の行列になるため両成分を反転する。
- 実装・検証: `src/oahu/denpaModels.ts` / `test/oahu-denpa.test.ts`。ROM から全 126 個体を組み立て、テクスチャ参照・スキンのボーン番号・待機姿勢を検査する。ROM 自体はコミットしない。
- ゲームの参照・UV 計算: [マップモデル §5](../../oahu/map-models.md)。

## 音の読み込み・UI

- `src/sound/` (CSAR・CWAR・CBNK・CSEQ・CSTM の読み込みと再生) を共用できる。ストリーム・波形・シーケンスの 3 種類とも再生を確認した記録がある。
- `#/sounds` (BGM・効果音) は RPG2 の一覧・試聴の部品 (`pages/sounds` の `SoundView`、`ui/SoundPicker`) をそのまま使い、RPG3 の「使われている場所」([音 §3](../../oahu/sound.md)) を出す (`src/oahu/sound.ts`、`src/oahu/SoundPage.tsx`)。[音 §3.3・§3.4](../../oahu/sound.md) のコードの呼び出しは、Update の code.bin を BL / B 命令で走査して見つける (Update がないときは出さない)。


- 旧音文書には「RPG3 のスクリプト実行器がまだない」「マップ (キー) → mapData の行の対応 (#66) が未解析」とあった。後続の [events.md](../../oahu/events.md) と [map.md §4](../../oahu/map.md) に解析結果があるため、現在の未解析事項とは区別する。

## ストーリー調査 (panana#85・#87)

- 実行器: `src/oahu/scripts.ts`。解析手順は [story.md §9](../../oahu/story.md)、クラス生成は [events.md §3](../../oahu/events.md)。
- EventObject の配置マップは Panana のイベント一覧でも表示する。
- 選んだ物語の状態 (段階・0xF9・0xFA・0x49) で各行が「置かれる / まだ出ない / 消えた」かをマップのページで表示する。
- 旧記録の共有フォルダ `oahu-story/navi.tsv` (135 行、見出しとヒント 4 つ)、`oahu-story/events.tsv` (メッセージか書き込みを持つ 508 行: 場所、出現条件、書くセーブの値、メッセージの冒頭) はこのリポジトリに含まれない ROM 由来の調査生成物。共有フォルダの存在を利用条件にしない。
