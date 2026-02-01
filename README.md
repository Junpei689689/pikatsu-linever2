# ポイ活・キャンペーン追跡AI LINE Bot

LINEを通知UIとして活用し、AIによるキャンペーン監視・要約・最適化を提供する
サブスクリプション型ポイ活サービス。

## 🎯 プロジェクト目的

「ポイ活の取り逃しを防ぎ、意思決定を代行する」

## ✨ 特徴

### 無料プラン（集客用）
- 週2回の高還元キャンペーン通知
- AI要約（短文）
- 個人最適化なし

### 有料プラン（月額1,280円）
- 保有カード・利用店舗に基づく個人最適化
- キャンペーン期待還元額の算出
- 今やるべきランキング（TOP3）
- 締切リマインド
- 地雷キャンペーン除外
- 月次成果レポート

## 🏗️ 技術構成

- **Backend**: FastAPI
- **Database**: SQLite
- **AI処理**:
  - 無料プラン: OSS LLM (Qwen2.5-7B)
  - 有料プラン: OpenAI API（予定）
- **通知**: LINE Messaging API
- **Deploy**: Render

## 📁 ディレクトリ構成

```
poikatsu-line-ai/
├── app/
│   ├── collectors/        # 情報収集
│   ├── summarizers/       # 要約（OSS/API）
│   ├── evaluators/        # 危険判定・優先度
│   ├── notifiers/         # LINE通知
│   ├── plans/             # 無料/有料制御
│   ├── profiles/          # ユーザー管理
│   ├── utils/             # DB等
│   └── webhook_server.py  # メインサーバー
├── data/                  # データ保存
├── config/                # 設定ファイル
├── main.py               # エントリーポイント
└── requirements.txt
```

## 🚀 セットアップ

### 1. 環境変数設定

`.env.example` を `.env` にコピーして編集:

```bash
cp .env.example .env
```

必須項目:
- `LINE_CHANNEL_ACCESS_TOKEN`: LINEチャネルアクセストークン
- `LINE_CHANNEL_SECRET`: LINEチャネルシークレット

### 2. 依存関係インストール

```bash
pip install -r requirements.txt
```

### 3. データベース初期化

初回起動時に自動作成されます。

### 4. ローカル起動

```bash
python main.py
```

または

```bash
uvicorn main:app --reload --port 8000
```

### 5. ngrokでローカルテスト（開発時）

```bash
ngrok http 8000
```

ngrokのURLをLINE Developers Console のWebhook URLに設定:
```
https://your-ngrok-url.ngrok.io/webhook
```

## 📦 Renderデプロイ

### 方法1: render.yaml使用

1. GitHubリポジトリと連携
2. Renderダッシュボードで「New Web Service」
3. リポジトリ選択
4. 環境変数を設定:
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`

### 方法2: 手動設定

1. Renderダッシュボードで「New Web Service」
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. 環境変数設定（上記と同じ）

デプロイ後、RenderのURLをLINEのWebhook URLに設定:
```
https://your-app-name.onrender.com/webhook
```

## 💬 LINEコマンド

| コマンド | 説明 |
|---------|------|
| `ping` / `p` | 接続確認 |
| `help` / `h` | 使い方表示 |
| `plan` | 現在のプラン確認 |
| `top3` / `t` | あなた向けTOP3表示 ⭐ |

## 🔧 開発用設定

### プラン強制指定（デバッグ用）

`.env` に追加:

```bash
# 全ユーザーを無料プランとして扱う
FORCE_PLAN=free

# または有料プラン
FORCE_PLAN=paid
```

## 🔒 セキュリティ方針

### 保有カード情報の扱い

**取得する情報（属性のみ）:**
- カード名
- 発行会社
- ブランド（VISA等）
- ポイント種別
- ランク（一般/ゴールド等）

**絶対に取得しない情報:**
- カード番号
- 有効期限
- セキュリティコード
- 利用明細
- ログイン情報

## 📊 設計原則

1. **無料は「気づき」まで**
   - キャンペーン情報の存在を知らせる
   
2. **有料は「判断と行動」を完全に代行**
   - 何をいつやるべきかを明示
   - 期待還元額を算出
   
3. **差別化は「意思決定情報の開示差」**
   - 機能差ではなく、情報開示の差で価値提供

## 📝 今後の実装予定

- [ ] 実キャンペーン収集（collectors実装）
- [ ] OpenAI API統合（優先理由生成）
- [ ] 締切リマインド機能
- [ ] 月次成果レポート
- [ ] Stripe課金統合
- [ ] ユーザー設定UI（LIFF）

## 📄 ライセンス

Private - All Rights Reserved

## 🤝 お問い合わせ

開発中のため、お問い合わせは受け付けておりません。
