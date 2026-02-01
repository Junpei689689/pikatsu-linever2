# Renderデプロイガイド

## 前提条件

- GitHubアカウント
- Renderアカウント（無料プランでOK）
- LINE Developers アカウント
- LINE Messaging APIチャネル作成済み

## 手順

### 1. GitHubリポジトリ準備

```bash
# リポジトリ初期化（まだの場合）
git init
git add .
git commit -m "Initial commit"

# GitHubにプッシュ
git remote add origin https://github.com/YOUR_USERNAME/poikatsu-line-ai.git
git push -u origin main
```

### 2. Render設定

1. [Render Dashboard](https://dashboard.render.com/) にログイン
2. 「New +」→「Web Service」をクリック
3. GitHubリポジトリを連携
4. 以下の設定を入力:

| 項目 | 値 |
|-----|-----|
| Name | `poikatsu-line-bot`（任意） |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Plan | `Free` |

### 3. 環境変数設定

Renderの Environment タブで以下を設定:

| キー | 値 |
|-----|-----|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINEチャネルアクセストークン |
| `LINE_CHANNEL_SECRET` | LINEチャネルシークレット |
| `DATABASE_URL` | `sqlite:///./data/db.sqlite3` |

**重要**: 
- `LINE_CHANNEL_ACCESS_TOKEN` と `LINE_CHANNEL_SECRET` は必ず設定
- Renderの環境変数は「Save Changes」を押すまで保存されない

### 4. デプロイ実行

「Save Changes」を押すと自動的にデプロイが開始されます。

デプロイログを確認:
```
==> Building...
==> Installing dependencies...
==> Starting server...
🚀 ポイ活LINE Bot 起動
   PORT: 10000
```

### 5. Webhook URL設定

デプロイ完了後、RenderのURLが発行されます:
```
https://poikatsu-line-bot-xxxx.onrender.com
```

このURLをLINE Developers Consoleに設定:

1. LINE Developers Console にログイン
2. チャネルを選択
3. 「Messaging API」タブ
4. 「Webhook settings」→「Webhook URL」に以下を入力:
   ```
   https://your-app-name.onrender.com/webhook
   ```
5. 「Verify」をクリックして接続確認
6. 「Use webhook」をONにする

### 6. 動作確認

LINEで友だち追加して、以下のコマンドを送信:

```
ping
```

→ `pong` が返ってくればOK

```
help
```

→ ヘルプメッセージが表示されればOK

```
top3
```

→ プランに応じた応答が返ってくればOK

## トラブルシューティング

### デプロイが失敗する

**原因1: requirements.txtの問題**
```bash
# ローカルで確認
pip install -r requirements.txt
```

**原因2: 環境変数未設定**
- Renderの Environment タブで環境変数が設定されているか確認

### Webhook接続エラー

**症状**: LINE Developers Console で「Verify」が失敗

**確認事項**:
1. Renderのサービスが起動しているか（Dashboard確認）
2. Webhook URLが正しいか
   - 末尾に `/webhook` がついているか
   - `https://` で始まっているか
3. `LINE_CHANNEL_SECRET` が正しく設定されているか

**確認方法**:
```bash
# Renderのログを確認
# Dashboard → Logs タブ
```

### Botが応答しない

**確認事項**:
1. Renderのログでエラーが出ていないか
2. LINE Messaging API の「Use webhook」がONになっているか
3. 環境変数が正しく設定されているか

**デバッグ方法**:
```bash
# Renderのシェルに接続（Dashboardから）
# 環境変数確認
echo $LINE_CHANNEL_ACCESS_TOKEN
```

## 無料プランの制限

Renderの無料プランには以下の制限があります:

- **15分間アクセスがないとスリープ**
  - 次回アクセス時に起動（30秒程度かかる）
  - 解決策: 定期的にアクセスするcronジョブ設置（別サービス）

- **月750時間まで**
  - 基本的に問題なし

- **ストレージ一時的**
  - SQLiteデータは再デプロイ時に消える
  - 解決策: PostgreSQL等の外部DBを使用（有料プラン移行時）

## アップデート方法

コード修正後:

```bash
git add .
git commit -m "Update: ..."
git push origin main
```

→ Renderが自動的に再デプロイ

## ログ確認

Render Dashboard → Logs タブ

リアルタイムでログが確認できます。

## データベースバックアップ

無料プランではSQLiteが再デプロイ時に消えるため、
本番運用前にPostgreSQLへの移行を推奨。

```bash
# 将来的な移行例
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## 参考リンク

- [Render Docs](https://render.com/docs)
- [LINE Messaging API Docs](https://developers.line.biz/ja/docs/messaging-api/)
