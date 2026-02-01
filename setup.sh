#!/bin/bash

echo "🚀 ポイ活LINE Bot セットアップ"
echo ""

# データディレクトリ作成
echo "📁 データディレクトリ作成..."
mkdir -p data/raw data/processed

# .env ファイルチェック
if [ ! -f .env ]; then
    echo "⚠️  .env ファイルが見つかりません"
    echo "   .env.example を .env にコピーして編集してください"
    echo ""
    echo "   cp .env.example .env"
    echo ""
    exit 1
fi

# 必須環境変数チェック
source .env

if [ -z "$LINE_CHANNEL_ACCESS_TOKEN" ] || [ "$LINE_CHANNEL_ACCESS_TOKEN" = "your_line_channel_access_token_here" ]; then
    echo "❌ LINE_CHANNEL_ACCESS_TOKEN が設定されていません"
    exit 1
fi

if [ -z "$LINE_CHANNEL_SECRET" ] || [ "$LINE_CHANNEL_SECRET" = "your_line_channel_secret_here" ]; then
    echo "❌ LINE_CHANNEL_SECRET が設定されていません"
    exit 1
fi

echo "✅ 環境変数OK"
echo ""

# Python依存関係インストール
echo "📦 依存関係インストール..."
pip install -r requirements.txt

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "起動方法:"
echo "  python main.py"
echo ""
echo "または"
echo "  uvicorn main:app --reload --port 8000"
echo ""
