# 開発ガイド

## 環境構築

### 1. リポジトリクローン

```bash
git clone https://github.com/YOUR_USERNAME/poikatsu-line-ai.git
cd poikatsu-line-ai
```

### 2. 仮想環境作成（推奨）

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

### 3. 依存関係インストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数設定

```bash
cp .env.example .env
```

`.env` を編集:
```bash
LINE_CHANNEL_ACCESS_TOKEN=your_actual_token
LINE_CHANNEL_SECRET=your_actual_secret
```

### 5. データベース初期化

```bash
# 自動的に初期化されますが、手動で確認する場合:
python -c "from app.utils.database import init_db; init_db()"
```

## ローカル開発

### サーバー起動

```bash
# 方法1: main.pyから起動
python main.py

# 方法2: uvicornで起動（リロード付き）
uvicorn main:app --reload --port 8000
```

ブラウザで確認:
```
http://localhost:8000
```

→ `{"status": "ok", "service": "poikatsu-line-bot"}` が表示されればOK

### ngrokでLINE連携テスト

LINEはHTTPSが必須のため、ローカル開発時はngrokを使用:

```bash
# ngrokインストール（初回のみ）
# https://ngrok.com/ からダウンロード

# ngrok起動
ngrok http 8000
```

ngrokのURLをLINE Developers Console に設定:
```
https://xxxx-xx-xx-xxx-xxx.ngrok-free.app/webhook
```

## テスト

### モジュールテスト

```bash
python tests/test_modules.py
```

出力例:
```
==========================================================
データベーステスト
==========================================================
✅ データベース初期化成功

==========================================================
ユーザープロフィールテスト
==========================================================
ユーザーID: test_user_123
プラン: free
...
```

### 手動テスト（LINE Bot）

LINEでBotに友だち追加して以下を送信:

```
ping
→ pong

help
→ ヘルプメッセージ

plan
→ プラン情報

top3
→ TOP3表示（プランに応じた応答）
```

## デバッグ

### プラン強制指定

`.env` に追加:

```bash
# 全ユーザーを無料プランとして扱う
FORCE_PLAN=free

# または有料プラン
FORCE_PLAN=paid
```

これにより、DB状態に関わらず指定プランで動作します。

### ログ確認

FastAPIは標準出力にログを出力:

```bash
# サーバー起動時
🚀 ポイ活LINE Bot 起動
   PORT: 8000

# リクエスト時
INFO:     127.0.0.1:52000 - "POST /webhook HTTP/1.1" 200 OK
```

## コード構成

### 主要ファイル

| ファイル | 役割 |
|---------|------|
| `main.py` | エントリーポイント |
| `app/webhook_server.py` | LINE Webhook処理 |
| `app/profiles/user_profile.py` | ユーザー管理 |
| `app/evaluators/personalize.py` | ランキング・最適化 |
| `app/notifiers/formatters.py` | メッセージフォーマット |
| `app/collectors/dummy_collector.py` | ダミーデータ生成 |
| `app/utils/database.py` | DB接続・モデル |

### データフロー

```
LINE User
  ↓ メッセージ送信
LINE Platform
  ↓ Webhook
webhook_server.py
  ↓ プラン判定
  ├─ free → format_free_top3_locked_text()
  └─ paid → rank_campaigns_for_user() → format_paid_top3_text()
  ↓ LINE返信
LINE User
```

## 新機能追加

### 1. 新しいコマンド追加

`app/webhook_server.py` の `handle_message()` に追加:

```python
elif msg_text == 'new_command':
    reply_text = handle_new_command(user_id, plan)
```

### 2. 新しいフォーマッター追加

`app/notifiers/formatters.py` に関数追加:

```python
def format_new_feature(data: Dict) -> str:
    """新機能のフォーマット"""
    return f"新機能: {data['title']}"
```

### 3. データベーステーブル追加

`app/utils/database.py` に新しいモデル追加:

```python
class NewTable(Base):
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True)
    # ...
```

初期化:
```python
from app.utils.database import init_db
init_db()  # 新しいテーブルが作成される
```

## コーディング規約

### Pythonスタイル

- PEP 8準拠
- 関数名: `snake_case`
- クラス名: `PascalCase`
- 定数: `UPPER_CASE`

### docstring

```python
def function_name(arg1: str, arg2: int) -> str:
    """
    関数の説明
    
    Args:
        arg1: 引数1の説明
        arg2: 引数2の説明
    
    Returns:
        戻り値の説明
    """
    pass
```

### 型ヒント

できる限り型ヒントを使用:

```python
def process_data(data: List[Dict]) -> Dict[str, Any]:
    ...
```

## Git運用

### ブランチ戦略

```bash
main         # 本番環境
 └─ develop  # 開発環境
     └─ feature/xxx  # 機能開発
```

### コミットメッセージ

```bash
git commit -m "Add: 新機能追加"
git commit -m "Fix: バグ修正"
git commit -m "Update: 既存機能改善"
git commit -m "Refactor: リファクタリング"
```

## トラブルシューティング

### ImportError

```bash
# パスが通っていない場合
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

### データベースロックエラー

```bash
# SQLiteファイルを削除して再作成
rm data/db.sqlite3
python -c "from app.utils.database import init_db; init_db()"
```

### LINE Webhook エラー

```bash
# シグネチャ検証エラーの場合
# LINE_CHANNEL_SECRET が正しいか確認
```

## パフォーマンス最適化

### データベースクエリ

```python
# 良い例: 必要なカラムのみ取得
session.query(User.line_user_id, User.plan).all()

# 悪い例: 全カラム取得
session.query(User).all()
```

### キャッシュ活用（将来実装）

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_campaign_data(campaign_id: str):
    ...
```

## セキュリティ

### 環境変数管理

- `.env` は絶対にGitにコミットしない
- `.gitignore` に `.env` が含まれているか確認

### SQLインジェクション対策

SQLAlchemyのORMを使用することで自動的に対策済み:

```python
# 安全（ORMが自動エスケープ）
session.query(User).filter_by(line_user_id=user_id).first()
```

## 次のステップ

- [ ] 実キャンペーン収集実装（`app/collectors/`）
- [ ] OpenAI API統合（`app/evaluators/ai_reasoner.py`）
- [ ] 週次通知スケジューラー実装
- [ ] PostgreSQL移行（本番環境）
- [ ] Stripe課金統合

## 参考資料

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LINE Messaging API](https://developers.line.biz/ja/docs/messaging-api/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
