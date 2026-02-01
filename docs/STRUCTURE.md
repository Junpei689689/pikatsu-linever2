# プロジェクト構成

```
poikatsu-line-ai/
│
├── README.md                  # プロジェクト概要
├── QUICKSTART.md             # クイックスタート
├── requirements.txt          # Python依存関係
├── setup.sh                  # セットアップスクリプト
├── main.py                   # エントリーポイント
├── render.yaml               # Renderデプロイ設定
├── .env.example              # 環境変数テンプレート
├── .env                      # 環境変数（Git管理外）
├── .gitignore               # Git除外設定
│
├── app/                      # アプリケーション本体
│   ├── __init__.py
│   ├── webhook_server.py     # ★ LINE Webhook メインサーバー
│   │
│   ├── collectors/           # キャンペーン情報収集
│   │   ├── __init__.py
│   │   └── dummy_collector.py  # ダミーデータ生成（開発用）
│   │
│   ├── summarizers/          # AI要約
│   │   ├── __init__.py
│   │   └── oss_summarizer.py   # OSS LLM要約（無料プラン用）
│   │
│   ├── evaluators/           # 評価・最適化
│   │   ├── __init__.py
│   │   └── personalize.py      # ★ ランキング・個人最適化
│   │
│   ├── notifiers/            # LINE通知
│   │   ├── __init__.py
│   │   └── formatters.py       # ★ メッセージフォーマット
│   │
│   ├── profiles/             # ユーザー管理
│   │   ├── __init__.py
│   │   └── user_profile.py     # ★ ユーザープロフィール
│   │
│   └── utils/                # ユーティリティ
│       ├── __init__.py
│       └── database.py         # ★ DB接続・モデル定義
│
├── data/                     # データ保存（Git管理外）
│   ├── raw/                  # 生データ
│   ├── processed/            # 処理済みデータ
│   └── db.sqlite3           # SQLiteデータベース
│
├── config/                   # 設定ファイル
│   ├── plans.yml            # プラン設定
│   └── sources.yml          # 情報源設定
│
├── docs/                     # ドキュメント
│   ├── DEPLOY.md            # デプロイガイド
│   └── DEVELOPMENT.md       # 開発ガイド
│
└── tests/                    # テスト
    ├── __init__.py
    └── test_modules.py       # モジュールテスト
```

## 主要モジュールの役割

### webhook_server.py
- LINE Webhookのエンドポイント
- メッセージイベント処理
- コマンド判定（ping/help/plan/top3）
- プラン判定（free/paid）

### user_profile.py
- ユーザー情報管理
- DB CRUD操作
- カード・店舗情報管理
- プラン変更

### personalize.py
- キャンペーンランキング生成
- 期待還元額算出
- スコアリング
- 取り逃し推定額計算

### formatters.py
- LINE返信メッセージ生成
- free/paid表示差分制御
- TOP3フォーマット
- ヘルプ・プラン情報

### database.py
- SQLAlchemyモデル定義
- User, Campaign, UserCampaignActionテーブル
- DB初期化・セッション管理

### dummy_collector.py
- テスト用ダミーキャンペーン生成
- 実キャンペーン収集は将来実装

## データフロー

```
┌─────────┐
│LINE User│
└────┬────┘
     │ メッセージ送信
     ▼
┌──────────────┐
│LINE Platform │
└──────┬───────┘
       │ Webhook POST /webhook
       ▼
┌─────────────────────┐
│ webhook_server.py   │
│ ・イベント受信      │
│ ・プラン判定        │
│ ・コマンド処理      │
└──────┬──────────────┘
       │
       ├─ プラン=free ─────────────┐
       │                           ▼
       │                  ┌────────────────┐
       │                  │formatters.py   │
       │                  │・拒否文生成    │
       │                  │・取り逃し額表示│
       │                  └────────┬───────┘
       │                           │
       └─ プラン=paid ─────────────┤
                                   ▼
                          ┌────────────────┐
                          │personalize.py  │
                          │・ランキング生成│
                          │・期待還元額算出│
                          └────────┬───────┘
                                   ▼
                          ┌────────────────┐
                          │formatters.py   │
                          │・TOP3詳細生成  │
                          └────────┬───────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │LINE返信         │
                          └────────────────┘
```

## 無料 vs 有料の情報開示差

### 無料プラン
- ❌ キャンペーン名
- ❌ 締切日・残日数
- ❌ 期待還元額内訳
- ❌ 優先度・順位
- ❌ 具体的手順
- ❌ URL
- ✅ 取り逃し推定額（合計のみ）

### 有料プラン
- ✅ TOP3キャンペーン名
- ✅ 締切日・残日数
- ✅ 期待還元額（円）
- ✅ 優先理由（自然文）
- ✅ やること（2ステップ）
- ✅ URL

## 環境変数

| 変数名 | 必須 | 説明 |
|-------|------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | ✅ | LINEチャネルアクセストークン |
| `LINE_CHANNEL_SECRET` | ✅ | LINEチャネルシークレット |
| `DATABASE_URL` | | DB接続URL（デフォルト: SQLite） |
| `FORCE_PLAN` | | プラン強制指定（free/paid）デバッグ用 |
| `OLLAMA_BASE_URL` | | Ollama API URL（将来実装） |
| `OPENAI_API_KEY` | | OpenAI API Key（将来実装） |

## 次の実装予定

- [ ] 実キャンペーン収集（collectors実装）
- [ ] OpenAI API統合（優先理由生成）
- [ ] 週次通知スケジューラー
- [ ] 締切リマインド機能
- [ ] 月次成果レポート
- [ ] Stripe課金統合
- [ ] PostgreSQL移行
