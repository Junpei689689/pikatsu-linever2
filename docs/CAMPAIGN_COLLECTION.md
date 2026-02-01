# キャンペーン収集機能ガイド

## 概要

楽天ポイント、Vポイント、dポイントのキャンペーン情報を自動収集します。

## 対象サイト

### 1. 楽天ポイント
- 楽天市場キャンペーン
- 楽天ポイントクラブ

### 2. Vポイント
- 三井住友カードキャンペーン
- セゾンカードキャンペーン

### 3. dポイント
- dカードキャンペーン
- dポイントクラブ

## 収集スケジュール

### 自動収集（GitHub Actions）
- **頻度**: 毎日午前9時（JST）
- **実行時間**: 約1〜2分
- **保存先**: `data/campaigns_cache.json`

### 手動収集
```bash
# テスト実行
python tests/test_collectors.py

# 本番実行
python -c "from app.collectors.campaign_collector import get_campaigns; get_campaigns(force_refresh=True)"
```

## 技術仕様

### 使用ライブラリ
- **requests**: HTTP通信
- **BeautifulSoup4**: HTMLパース
- **lxml**: 高速パーサー

### コスト
- **APIコスト**: 0円（スクレイピングのみ）
- **実行時間**: 約30秒〜1分
- **GitHub Actions**: 無料枠内（月2,000分まで）

## キャッシュ仕様

### キャッシュファイル
```
data/campaigns_cache.json
```

### 有効期限
- **24時間**
- 有効期限内はキャッシュを使用（高速化）
- 期限切れまたは強制更新時に再収集

### キャッシュ構造
```json
{
  "cached_at": "2026-02-01T09:00:00",
  "count": 25,
  "campaigns": [
    {
      "campaign_id": "rakuten_123456",
      "title": "楽天スーパーセール",
      "description": "全ショップ対象...",
      "url": "https://...",
      "source": "楽天市場",
      "start_date": "2026-02-01T00:00:00",
      "end_date": "2026-02-10T23:59:59",
      "return_rate": 10,
      "required_cards": ["楽天カード"],
      "is_dangerous": false
    }
  ]
}
```

## 収集データ項目

| 項目 | 説明 | 例 |
|------|------|-----|
| campaign_id | 一意ID | rakuten_123456 |
| title | キャンペーン名 | 楽天スーパーセール |
| description | 説明文 | 全ショップ対象... |
| url | キャンペーンURL | https://... |
| source | 情報源 | 楽天市場 |
| start_date | 開始日時 | 2026-02-01 |
| end_date | 終了日時 | 2026-02-10 |
| base_amount | 想定利用額 | 10000円 |
| return_rate | 還元率 | 10% |
| required_cards | 必要カード | [楽天カード] |
| target_stores | 対象店舗 | [楽天市場] |
| is_dangerous | 地雷判定 | false |
| danger_reason | 地雷理由 | null |
| action_steps | 手順 | [エントリー, 買い物] |

## エラーハンドリング

### ネットワークエラー
- **対応**: 各ソース個別にtry-catch
- **影響**: 一部ソースが失敗しても他は継続

### パースエラー
- **対応**: 要素ごとにtry-catch
- **影響**: 該当キャンペーンのみスキップ

### キャッシュエラー
- **対応**: エラー時は空リストを返す
- **影響**: 自動的に再収集を試行

## トラブルシューティング

### キャンペーンが収集できない

**原因1: ネットワークエラー**
```bash
# 接続確認
curl -I https://event.rakuten.co.jp/
```

**原因2: HTML構造変更**
- サイトのHTML構造が変更された可能性
- セレクタの修正が必要

**原因3: アクセス制限**
- User-Agentが拒否された可能性
- ヘッダーの調整が必要

### キャッシュが更新されない

**確認事項**:
1. GitHub Actionsが正常に実行されているか
2. `data/` ディレクトリの書き込み権限
3. キャッシュファイルの存在確認

## カスタマイズ

### 新しいソース追加

1. **コレクタークラス作成**
```python
# app/collectors/new_collector.py
class NewCollector:
    def collect_campaigns(self) -> List[Dict]:
        # 収集ロジック
        pass
```

2. **統合マネージャーに追加**
```python
# app/collectors/campaign_collector.py
from app.collectors.new_collector import collect_new_campaigns

# collect_all()メソッド内に追加
new = collect_new_campaigns()
all_campaigns.extend(new)
```

### セレクタの調整

各コレクターの `_scrape_url()` メソッド内：
```python
campaign_elements = soup.select('.your-selector')
```

### 収集頻度の変更

`.github/workflows/collect_campaigns.yml`:
```yaml
schedule:
  # 毎日2回（午前9時・午後9時）
  - cron: '0 0,12 * * *'
```

## セキュリティ

### 取得しない情報
- ユーザーの個人情報
- ログイン情報
- Cookie・セッション情報

### 取得する情報
- 公開されているキャンペーン情報のみ

## コスト最適化

### 現在の設計（月額800円前提）

| 項目 | コスト |
|------|--------|
| スクレイピング | 0円 |
| GitHub Actions | 0円（無料枠） |
| ストレージ | 0円（JSONキャッシュ） |
| **合計** | **0円** |

### スケーラビリティ
- ユーザー数増加でもコスト増なし
- 収集頻度を上げてもほぼコスト増なし

## 次のステップ

1. **本番環境で動作確認**
2. **HTML構造変更時の通知設定**
3. **より多くのソース追加**
4. **機械学習による地雷判定精度向上**
