# サードパーティのサーバーでチェックインを動かす (提案・未検証)

対象: lanai Update v17408 の code.bin。アドレスは Update の `code.bin` (基準 0x100000)。

ゲーム側の仕様 (確定・推定の区別つき) は [checkin.md](checkin.md) にある。本書はそれを前提にした **提案** で、実機・エミュレータでは何も確かめていない。ROM の取得先や鍵などのアクセス情報は扱わない。

## 1. サーバーが返すべき応答 (仕様からの要約)

すべて HTTP 200、本文はテキスト。成功は `SUCCESS` で始め、欄は `,` で区切る ([checkin.md §2](checkin.md#2-共通の約束))。

| 要求 | 方式 | 返す本文の例 | ゲーム側の読み方 |
|---|---|---|---|
| `checkinserver?req=time` | GET | `SUCCESS,20261017 093000` | 2 つ目の欄を位置で読む (年 +0・月 +4・日 +6・時 +9・分 +11・秒 +13)。15 文字以上 |
| `checkinserver?req=bonus_tbl` | GET | `SUCCESS,<base64>` | 9 バイト目以降を base64 でデコードし、GS テーブルとして使う (§3.3)。応答全体で 0x3C00 バイト未満にする |
| `checkinserver?req=check&support_id=…` | GET | `SUCCESS,true` / `SUCCESS,false` | `true` なら登録済み (`update` へ)、それ以外は `create` へ |
| `checkinserver` `req=create` / `update` / `delete` | POST | `SUCCESS` | 最初の欄が `ERROR` でなければ成功 |
| `gameserver?req=res_ver` | GET | `SUCCESS,1.17.0` | 自分の版より新しいと更新の案内 (0x8000030C) を出すと推定。ゲームの版と同じか古い値を返す |

- **返してはいけない応答**: `ERROR,10` はトークンの取り直しとやり直しを起こす ([checkin.md §2](checkin.md#2-共通の約束))。`update` に `ERROR,11` を返すと「記録が見つからない」扱い (作業領域 +0xAAC = 1) になる。
- 時刻の時差: 元のサーバーは日本の運営なので、日本時間を返す想定 (推定)。ゲームは日付の差でチェックインの連続・通算を数え、セーブにその日付を書く。時差を途中で変えると日数の計算がずれる。
- `support_id` は u64 の 10 進。プレイヤーの識別子として使う。
- コロシアム (`gameserver?req=rank…`)・コード照会 (`campaigncodeserver`)・ジュエルの購入 (`ctr_ec` など) は応答の解釈を解析していないので、本書の範囲外。

## 2. ゲーム側の MOD

### 2.1 書き換える場所

| 目的 | 方法の案 | 根拠 |
|---|---|---|
| 接続先 | URL の文字列 (ro の `0x4A2078` 付近と、text のリテラル `0x26EE50`・`0x437C74`・`0x439184`・`0x2A377C` など) を、元の長さ以下の自分のホストに書き換える。`https://la1.denpamen.com` は 24 文字 | [checkin.md §1](checkin.md#1-通信先-codebin-の文字列確定) |
| HTTPS | **`http://` に書き換える (推奨)**。1 文字短くなるので長さの条件を満たす | 下記 |
| サービス終了モード | `FUN_003E9840` の中の分岐 (スイッチが立つと `0x3E99C8` へ飛ぶ所) だけを外す。`FUN_002E7DEC` 全体を 0 にすると、ジュエル販売所・コロシアムの終了の案内も消えて、つながらない機能に進んでしまう | [checkin.md §6](checkin.md#6-サービス終了後のオフラインチェックイン) |
| auth_token | 取得 (`FUN_004359EC`) が失敗する環境では、成功を返して固定の文字列を `0x5A87F4` に置くようにする。サーバーは値を検査しない | [checkin.md §2](checkin.md#共通-auth_token) |

HTTPS を残す場合の選択肢 (どれも未検証):
- 証明書の差し替え: `0x4A2C60` の DER (0x536 バイト) を自分のサーバーの自己署名の証明書に替え、`FUN_002AF464` が返す長さを直す。0x536 バイトを超える証明書は、別の場所に置いて `FUN_002AF458` の返す位置も変える。
  - Cloudflare の配信網の証明書は Cloudflare が選ぶので、自己署名の証明書は使えない。
  - 3DS の SSL は古い TLS と暗号方式しか扱えないとされ、今のサーバーとつながらない恐れがある。
- 検証を外す: `FUN_002AF470(ctx, 0)` の引数を、検証を省く設定に変える。nn::http の SSL 設定の値の意味は未確認。

`http://` にしても `FUN_002AF42C` (証明書の追加) は呼ばれたままになる。害はないと推定するが未確認。

### 2.2 配り方
- **Luma3DS の code.ips (または code.bps)**: Update の code.bin に当てるパッチとして `luma/titles/0004000000125D00/` に置く。Luma は動いている code.bin (Update があれば Update のもの) に当てる ([RPG2 の例](../roms/kahara.md#luma3ds-での適用))。
- **Update として配る**: パッチを当てた code.bin を入れた Update CIA を作る ([RPG3 の Update 方式](../roms/oahu-update.md#22-mod-を-update-として配る-タイトル-0004000e000ef000))。LayeredFS が要らない。
- どちらも、接続先を書き換えたセーブは元の接続先に戻しても問題ないと推定 (セーブには接続先を書かない。未確認)。

## 3. サーバー側: Cloudflare Worker の案

### 3.1 構成
- Worker 1 つで `/checkinserver` と `/gameserver` を受ける。ほかのパスは `SUCCESS` だけを返すか 404 にする。
- 記録 (`create` / `update`) は D1 に置く。表 `players(support_id TEXT PRIMARY KEY, total_num INTEGER, num INTEGER, bdat TEXT, body TEXT, updated_at INTEGER)` (`body` に送られた欄をすべて JSON で残す)。`delete` で行を消す。
- ログインボーナスの表は Worker の中で作るか、KV に置いた base64 を返す。
- HTTP のまま受けるため、Cloudflare の「Always Use HTTPS」を切る。
- POST の本文は `application/x-www-form-urlencoded` と推定 (nn::http の POST の欄)。`request.formData()` で読めなければ、本文をそのまま記録して形式を確かめる。

### 3.2 Worker の骨組み (TypeScript)

```ts
export interface Env { DB: D1Database; BONUS: KVNamespace }

const ok = (...f: string[]) => new Response(['SUCCESS', ...f].join(','), { headers: { 'content-type': 'text/plain' } });

function jstNow(): string {
  const d = new Date(Date.now() + 9 * 3600_000);
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}${p(d.getUTCMonth() + 1)}${p(d.getUTCDate())} ${p(d.getUTCHours())}${p(d.getUTCMinutes())}${p(d.getUTCSeconds())}`;
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const q = req.method === 'POST' ? Object.fromEntries((await req.formData()) as unknown as Iterable<[string, string]>) : Object.fromEntries(url.searchParams);
    if (url.pathname === '/gameserver' && q.req === 'res_ver') return ok('1.17.0');
    if (url.pathname !== '/checkinserver') return ok();
    switch (q.req) {
      case 'time': return ok(jstNow());
      case 'bonus_tbl': return ok((await env.BONUS.get('bonus_tbl')) ?? bonusTable());
      case 'check': {
        const row = await env.DB.prepare('SELECT 1 FROM players WHERE support_id = ?').bind(q.support_id).first();
        return ok(row ? 'true' : 'false');
      }
      case 'create': case 'update':
        await env.DB.prepare('INSERT OR REPLACE INTO players (support_id, total_num, num, bdat, body, updated_at) VALUES (?, ?, ?, ?, ?, ?)')
          .bind(q.support_id, Number(q.total_num), Number(q.num), q.bdat ?? '', JSON.stringify(q), Date.now()).run();
        return ok();
      case 'delete':
        await env.DB.prepare('DELETE FROM players WHERE support_id = ?').bind(q.support_id).run();
        return ok();
    }
    return ok();
  },
};
```

- `auth_token` は受け取るが検査しない。
- `bdat` は gzip + base64 と推定 ([checkin.md §2.2](checkin.md#22-bdat-確定一部推定))。保存しておけば、後で中身 (0x8B84 バイト) を解析できる。

### 3.3 ログインボーナスの表を作る
lanai 形式の GS テーブル ([analysis.md §2](analysis.md#2-gs-テーブル-lanai-形式確定)) を 1 個作り、base64 にする。文字列の欄が無いので、再配置は 0 件でよい見込み。

```ts
// 行: { item: u32 (0x80000000 = なし), day: s16 (通算日数), gold: u16, jewel: u8 } を 0x0C バイトに詰める
function bonusTable(rows = defaultRows()): string {
  const name = new TextEncoder().encode('CheckinBonus\0');
  const strSize = (name.length + 3) & ~3;
  const dataOff = 0x40 + strSize;
  const size = 0x0c;
  const b = new Uint8Array(dataOff + rows.length * size);
  const v = new DataView(b.buffer);
  v.setUint32(0x00, rows.length, true); v.setUint32(0x04, size, true);
  v.setUint32(0x08, 0x40, true); v.setUint32(0x0c, strSize, true);
  v.setUint32(0x10, dataOff, true); v.setUint32(0x14, rows.length * size, true);
  v.setUint32(0x28, b.length, true); // 再配置表なし: ファイルの末尾
  v.setUint32(0x34, 0, true); v.setUint32(0x38, name.length, true);
  b.set(name, 0x40);
  rows.forEach((r, i) => {
    const o = dataOff + i * size;
    v.setUint32(o, r.item, true); v.setInt16(o + 4, r.day, true); v.setUint16(o + 6, r.gold, true); v.setUint8(o + 8, r.jewel);
    b.fill(0xd0, o + 9, o + size);
  });
  return btoa(String.fromCharCode(...b));
}
```

未確認の点:
- 行の大きさ (0x0C と推定)、表の名前を見るか (見当たらない)、行 ID の表が要るか。
- base64 の文字の種類 (`+` `/` か、トークンと同じ URL 用の置き換えか)。`FUN_002AF0DC` の表を見て決める。
- 行が見つからない日は既定のボーナス ([checkin.md §3](checkin.md#reqbonus_tbl-ログインボーナスの表)) になるかどうか。

元の表の値は残っていないので、既定のボーナス (1・3・7 日目、5 の倍数、100 の倍数) をまねた行から始める。

## 4. ROM にないステージを配る構想の実現性

### 4.1 サーバーが届けられるもの (仕様から)

| 経路 | 中身 | ステージに効くか |
|---|---|---|
| `bonus_tbl` (HTTP) | ログインボーナスの行 (アイテム・ゴールド・ジュエル) だけ | **効かない**。行の形が違い、報酬の種類 0x1B (公開) を持てない |
| `checkin.dat` (SpotPass、NsData 2) | 0x54 バイトの行 (条件・報酬・お知らせ) の GS テーブル、最大 1 MB | **既存のステージの公開**はできる (報酬の種類 0x1B)。ただし SpotPass のデータは任天堂の署名・暗号化つきと推定され、第三者は作れない |
| `resource.dat` (SpotPass、NsData 3) | 版つきのアーカイブの束と推定。拡張データの `ext:/arc/` に書き込む (§4.3) | **新しいアーカイブを足す仕組みそのもの**と推定。ただし SpotPass なので第三者は作れない |

したがって、未改造の code.bin のままで (接続先の書き換えだけで) 届けられるのはログインボーナスだけ。

### 4.2 段階ごとの見込み

| 段階 | 必要なもの | 見込み |
|---|---|---|
| A. 既存のイベントステージを好きな日に公開する | MOD: `FUN_0040CBAC` (NsData の読み込み) を、HTTP で `checkin.dat` 相当を取る処理に替える。サーバーは 0x54 バイトの行の表 (Checkin_Rom・CheckinEVCK18/19 と同じ形) を返す | **高い**。行の形と評価 (`FUN_003008BC`) は分かっていて、読み込み先を替えるだけ。1 MB の領域がある |
| B. 既存の表 (master など) の値を差し替える | ファイルの差し替え (LayeredFS か Update) | 高い。ただしサーバー経由ではなく MOD の配布になる |
| C. ROM にない新しいステージを足す | 新しいコンテンツのアーカイブ・master の Contents / MapStageIntegration / MessageMapStage の行・CRO・CRR ([contents.md §5](contents.md#5-新しいコンテンツを足すには-提案未検証)) | 中程度。中身の作り方は [contents.md](contents.md) の課題 |
| D. C をサーバーからダウンロードさせる | C に加えて、MOD: `resource.dat` の読み込み (`FUN_0040CBAC`) を HTTP に替え、ゲーム自身の書き込み (`FUN_00448C24`) に渡す | 中程度。書き込みの経路はゲームにある (§4.3)。読み出しの経路と中身の形式が未確認 |

### 4.3 resource.dat と拡張データのアーカイブ (確定・一部推定)
ゲームには、**SpotPass で届いた `resource.dat` の中身を拡張データ (`ext:`) にアーカイブとして書き込む処理**がある。

確定した部分:
- チェックインの日・そうでない日のどちらでも、BOSS の作業 0x80000001 (`resource.dat`、[checkin.md §8](checkin.md#8-spotpass-boss-で配る表-確定一部推定)) を動かす。スレッドの入口 `0x3EB470` が `FUN_00448C24` を呼ぶ。`FUN_002FE1D0` (チェックインの処理から呼ぶ) も `FUN_002D99C4` → `FUN_0040CBAC` で NsData を読み、`FUN_00448F5C` で版を確かめる。
- `FUN_00448F5C` / `FUN_00448C24` は、データの先頭の +0xA / +0xC / +0xE の u16 (版 a.b.c と推定) を `0x4EB570` の 3 つの u16 とくらべ、新しいときだけ進む。
- `FUN_00448C24` は、表 `0x737AF400` の行 (最大 0x3FF 行) を順に見て、行ごとに `FUN_00208BB4` を呼ぶ。最後に版を `FUN_0040D034(a, b, c)` で保存する。
- `FUN_00208BB4` は UTF-16 の `ext:/arc/` (`0x4A499C`) でパスを作り、ファイルを開く・作る処理 (`FUN_0031F0C0`、`FUN_0030FDC4` / `FUN_0030FD88` / `FUN_0030FE00`) を呼ぶ。FS の結果 0xD863FBF3 / 0xD883FBEF で分かれる。
- パスの書式: `FUN_0031B728(n)` は n < 0x400 なら `ext:/arc/` + 10 進 4 桁、そうでなければ 16 進 8 桁のパスを作る。ほかに `ext:/FFFFFFFF` の書式がある。
- ふつうのアーカイブを開く `FUN_0031F108` は、patchList.bin に載っていれば `patch:/XXXXXXXX`、なければ `rom:/XXXXXXXX` を選ぶ。ここに `ext:` は出てこない。
- CRO の読み込み (`FUN_001E9B9C`) は、master +0x30 の値が 0x400 未満のとき CRR を `content:/.crr/contentsNNNN.crr` から読む ([contents.md §4](contents.md#4-cro-と-crr))。`content:/0000` (10 進 4 桁) の書式を `FUN_0031F3B4` が作る。

推定:
- `ext:/arc/NNNN` (10 進 4 桁) と `content:/NNNN`・`contentsNNNN` が同じ 0x400 未満の番号を使うので、**拡張データに置いたアーカイブを `content:` として開き、コンテンツ (ステージ) として読む** 仕組みと推定する。つまり、元のゲームは **新しいステージを SpotPass で配る** 設計を持っていた可能性が高い。
- どこで `content:` をマウントするか、表 `0x737AF400` の中身 (master `2135000A`・`A9DF0000`・`7BF7000A`・`25D60000`・`307C0000` には無い)、`resource.dat` の形式は未確認。

`ext:/arc/` のパスを使う関数 (確定):
- パスを作る `FUN_0031B728` / `FUN_0031B9C0` の呼び出し元は、`resource.dat` の書き込みのまとまり (`FUN_00448C24`・`FUN_00448FCC` → `FUN_00208660`・`FUN_00449080` → `FUN_002087C8`) と、アーカイブを開く側 (`FUN_0031F6AC` → `FUN_0011F0F8`、`FUN_0031F9EC`、`FUN_0010EFEC` → `FUN_0011645C`、`FUN_00208528`) だけ。
- `FUN_0031F6AC` / `FUN_0031F9EC` は、`rom:` / `patch:` のパス (`FUN_0031F0C0`) と、`ext:/arc/`・`content:/NNNN` (`FUN_0031F200`) のパスの両方を作る。アーカイブを開くときに拡張データも探すと推定 (探す順は未確認)。

### 4.4 島に遊びに行く機能との関係 (確定・一部推定)
- 島の訪問はローカル通信 (`nn::nwm` の UDS) で、クラス名 `rootIslandCreateRoom` の `SendIslandDataAsMaster`、`rootIslandSearch` の `ReceiveIslandDataAsClient` がある。`rootLocalBattleSearch` も同じ受け取りの仕組みを使う。
- 上の `ext:/arc/` を使う関数の中に、これらの島の通信の処理は無い。したがって `ext:/arc/` は島の訪問の保存先ではなく、SpotPass の `resource.dat` の保存先と判断する (呼び出し元からの推定)。
- 島のデータの送受信を転用する案は、相手が別の 3DS (ローカル通信) なので、サーバーからの配信には直接は使えない。島の家・植物・住人などの島の状態を配る用途なら、受け取った島のデータの形式を調べる価値がある (未解析)。
- チェックインの記録の欄 `go_island` / `come_island` (`0x26F1F4`) は、島の訪問の回数をサーバーに送る欄と推定。

### 4.5 提案
- 新しいステージそのもの (アーカイブ・CRO・CRR・master の行) は **MOD (Update または LayeredFS) で配り**、サーバーは **いつ・誰に公開するか (0x54 バイトの行)** と報酬を配る分担にする。段階 A の仕組みがそのまま使える。
- CRR は RSA 署名つきで、作り直した CRR を通すには RO の署名の確認を外す環境が要る ([contents.md §4.2](contents.md#42-crr))。既存の CRO と同じバイト列なら既存の CRR のハッシュで通るので、まずは **既存の CRO を使い回し、表とマップだけ違うステージ** から試すのが安全。
- 段階 D は、ゲームが持つ拡張データの仕組み (§4.3) に乗れる見込みがある。MOD は `resource.dat` の取得先を HTTP に替えるだけで、書き込みと読み出しはゲームの処理を使える。先に `resource.dat` の形式・表 `0x737AF400`・`content:` のマウントを確かめる。うまくいけば、新しいステージをサーバーから配り、拡張データに置かせることができる。

## 5. 未確認事項 (確かめる順)
1. auth_token の取得に失敗したときの挙動 (エミュレータ・NNID なしの環境)。
2. `http://` に書き換えたときに nn::http がそのまま通すか。
3. `bonus_tbl` の行の大きさと base64 の文字の種類。
4. `FUN_0040CBAC` を差し替えて、HTTP で取った 0x54 バイトの行の表で既存ステージが開くか (段階 A)。
5. `resource.dat` の形式、表 `0x737AF400`、`content:` のマウントと `ext:/arc/` のアーカイブを開く経路 (§4.3)。
