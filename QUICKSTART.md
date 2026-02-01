# クイックスタートガイド

## 🚀 5分で始めるポイ活LINE Bot

### ステップ1: 環境変数設定

```bash
cp .env.example .env
```

`.env` を開いて、LINE Developers Console から取得した情報を入力:

```bash
LINE_CHANNEL_ACCESS_TOKEN=your_actual_channel_access_token
LINE_CHANNEL_SECRET=your_actual_channel_secret
```

### ステップ2: セットアップ実行

```bash
chmod +x setup.sh
./setup.sh
```

または手動で:

```bash
pip install -r requirements.txt
mkdir -p data/raw data/processed
```

### ステップ3: ローカル起動

```bash
python main.py
```

→ `http://localhost:8000` でサーバーが起動

### ステップ4: ngrokでLINE連携（ローカル開発時）

```bash
# 別ターミナルで
ngrok http 8000
```

→ `https://xxxx.ngrok-free.app` が表示される

LINE Developers Console で Webhook URL を設定:
```
https://xxxx.ngrok-free.app/webhook
```

### ステップ5: 動作確認

LINEでBotに以下を送信:

```
ping
```

→ `pong` が返ってくればOK！

```
top3
```

→ プランに応じた応答が返ってくる

## 🎯 プラン切り替え（開発・デバッグ用）

`.env` に追加:

```bash
# 無料プランでテスト
FORCE_PLAN=free

# 有料プランでテスト
FORCE_PLAN=paid
```

## 📦 Renderにデプロイ

詳細は [DEPLOY.md](docs/DEPLOY.md) を参照

簡易版:
1. GitHubにプッシュ
2. Renderで「New Web Service」
3. リポジトリ連携
4. 環境変数設定
5. デプロイ

## 🐛 トラブルシューティング

### Botが応答しない

1. サーバーが起動しているか確認
2. `.env` の設定が正しいか確認
3. LINE Webhook URLが正しいか確認

### 環境変数エラー

```bash
# 環境変数が読み込まれているか確認
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))"
```

## 📚 次のステップ

- [開発ガイド](docs/DEVELOPMENT.md) - 詳細な開発方法
- [デプロイガイド](docs/DEPLOY.md) - Render本番デプロイ
- [README.md](README.md) - プロジェクト全体像

## 💡 よく使うコマンド

```bash
# サーバー起動（開発モード）
uvicorn main:app --reload --port 8000

# テスト実行
python tests/test_modules.py

# データベース確認
sqlite3 data/db.sqlite3 "SELECT * FROM users;"
```
