# セットアップチェックリスト

このチェックリストに従って、正しくセットアップされているか確認してください。

## ☑️ 事前準備

- [ ] Python 3.9以上がインストールされている
- [ ] LINE Developers アカウントを持っている
- [ ] LINE Messaging API チャネルを作成済み
- [ ] GitHubアカウントを持っている（Renderデプロイ用）

## ☑️ LINE設定確認

LINE Developers Console で以下を確認:

- [ ] チャネルアクセストークンを取得
- [ ] チャネルシークレットを取得
- [ ] Messaging API が有効化されている
- [ ] Webhook設定が「Use webhook」になっている

## ☑️ ローカル環境セットアップ

### 1. リポジトリクローン
```bash
□ git clone https://github.com/YOUR_USERNAME/poikatsu-line-ai.git
□ cd poikatsu-line-ai
```

### 2. 仮想環境作成（推奨）
```bash
□ python -m venv venv
□ source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 環境変数設定
```bash
□ cp .env.example .env
□ .env に LINE_CHANNEL_ACCESS_TOKEN を記入
□ .env に LINE_CHANNEL_SECRET を記入
```

### 4. セットアップ実行
```bash
□ chmod +x setup.sh
□ ./setup.sh
```

または

```bash
□ pip install -r requirements.txt
□ mkdir -p data/raw data/processed
```

## ☑️ 動作確認（ローカル）

### サーバー起動
```bash
□ python main.py
```

確認項目:
```
□ 「🚀 ポイ活LINE Bot 起動」が表示される
□ エラーメッセージが出ていない
```

### ヘルスチェック
ブラウザで http://localhost:8000 を開く

```
□ {"status": "ok", "service": "poikatsu-line-bot"} が表示される
```

### モジュールテスト
```bash
□ python tests/test_modules.py
```

確認項目:
```
□ 全テストが「✅」で完了
□ エラーが出ていない
```

## ☑️ LINE連携確認（ngrok使用）

### ngrok起動
```bash
□ ngrok http 8000
```

### Webhook URL設定
```
□ ngrok URL をコピー（例: https://xxxx.ngrok-free.app）
□ LINE Developers Console で Webhook URL を設定
   （例: https://xxxx.ngrok-free.app/webhook）
□ 「Verify」をクリックして成功を確認
```

### LINE Bot動作確認
LINEでBotに友だち追加して、以下を送信:

```
□ 「ping」→「pong」が返ってくる
□ 「help」→ ヘルプメッセージが表示される
□ 「plan」→ プラン情報が表示される
□ 「top3」→ プランに応じた応答が返ってくる
```

### プラン切り替えテスト
`.env` に `FORCE_PLAN=free` を追加して再起動:

```
□ 「top3」→ 拒否文＋取り逃し推定額が表示される
```

`.env` を `FORCE_PLAN=paid` に変更して再起動:

```
□ 「top3」→ TOP3詳細が表示される
```

## ☑️ Renderデプロイ（本番環境）

### GitHub準備
```bash
□ git init
□ git add .
□ git commit -m "Initial commit"
□ git remote add origin https://github.com/YOUR_USERNAME/poikatsu-line-ai.git
□ git push -u origin main
```

### Render設定
```
□ Render Dashboard にログイン
□ 「New Web Service」をクリック
□ GitHubリポジトリを連携
□ 以下を設定:
   - Name: poikatsu-line-bot
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   - Plan: Free
```

### 環境変数設定
Renderの Environment タブで設定:

```
□ LINE_CHANNEL_ACCESS_TOKEN
□ LINE_CHANNEL_SECRET
□ DATABASE_URL (デフォルト: sqlite:///./data/db.sqlite3)
□ 「Save Changes」をクリック
```

### デプロイ確認
```
□ デプロイが完了（ログで確認）
□ 「🚀 ポイ活LINE Bot 起動」が表示される
□ Render URL が発行される（例: https://poikatsu-line-bot-xxxx.onrender.com）
```

### Webhook URL更新
```
□ Render URL をコピー
□ LINE Developers Console で Webhook URL を更新
   （例: https://poikatsu-line-bot-xxxx.onrender.com/webhook）
□ 「Verify」をクリックして成功を確認
```

### 本番動作確認
```
□ 「ping」→「pong」が返ってくる
□ 「top3」→ プランに応じた応答が返ってくる
```

## ☑️ トラブルシューティング

### サーバーが起動しない
```
□ .env ファイルが存在するか確認
□ LINE_CHANNEL_ACCESS_TOKEN が正しいか確認
□ LINE_CHANNEL_SECRET が正しいか確認
□ requirements.txt の依存関係がインストールされているか確認
```

### Webhook接続エラー
```
□ Webhook URL が正しいか確認
□ LINE_CHANNEL_SECRET が正しいか確認
□ サーバーが起動しているか確認
□ ファイアウォールで8000番ポートが開いているか確認
```

### Botが応答しない
```
□ 「Use webhook」がONになっているか確認
□ Renderのログでエラーが出ていないか確認
□ LINE Developers Console でエラーが出ていないか確認
```

## ✅ セットアップ完了！

全てのチェック項目が完了したら、以下を確認:

```
□ ローカル環境で正常に動作
□ LINE Bot が正常に応答
□ Renderにデプロイ成功
□ 本番環境で正常に動作
```

おめでとうございます！ポイ活LINE Botのセットアップが完了しました。

## 📚 次のステップ

- [ ] ユーザーデータを収集・分析
- [ ] 実キャンペーン収集機能の実装
- [ ] OpenAI API統合（優先理由生成）
- [ ] PostgreSQL移行（本番運用）
- [ ] Stripe課金統合

---

問題が発生した場合:
- [開発ガイド](DEVELOPMENT.md) を参照
- [デプロイガイド](DEPLOY.md) を参照
