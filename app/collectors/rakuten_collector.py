"""
楽天ポイントキャンペーン収集
requests + BeautifulSoup4 でコスト最小化
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re


class RakutenCollector:
    """楽天キャンペーン情報収集"""
    
    def __init__(self):
        self.base_url = "https://event.rakuten.co.jp"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def collect_campaigns(self) -> List[Dict]:
        """
        楽天のキャンペーン情報を収集
        
        Returns:
            キャンペーンリスト
        """
        campaigns = []
        
        # 複数のエンドポイントから収集
        urls = [
            f"{self.base_url}/campaign/",  # メインキャンペーンページ
            "https://point.rakuten.co.jp/campaign/",  # ポイント特集
        ]
        
        for url in urls:
            try:
                campaigns.extend(self._scrape_url(url))
            except Exception as e:
                print(f"楽天収集エラー ({url}): {e}")
        
        return campaigns
    
    def _scrape_url(self, url: str) -> List[Dict]:
        """URLからキャンペーン情報を抽出"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            campaigns = []
            
            # キャンペーン要素を探す（セレクタは実際のHTML構造に合わせて調整）
            campaign_elements = soup.select('.campaign-item, .event-item, article')
            
            for elem in campaign_elements[:10]:  # 上位10件
                campaign = self._parse_campaign_element(elem, url)
                if campaign:
                    campaigns.append(campaign)
            
            return campaigns
        
        except Exception as e:
            print(f"スクレイピングエラー: {e}")
            return []
    
    def _parse_campaign_element(self, elem, source_url: str) -> Optional[Dict]:
        """キャンペーン要素をパース"""
        try:
            # タイトル取得
            title_elem = elem.select_one('h2, h3, .title, .campaign-title')
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            
            # URL取得
            link_elem = elem.select_one('a')
            campaign_url = ""
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if href.startswith('http'):
                    campaign_url = href
                else:
                    campaign_url = f"{self.base_url}{href}"
            
            # 説明文取得
            desc_elem = elem.select_one('.description, .summary, p')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # ポイント還元率を抽出
            return_rate = self._extract_return_rate(f"{title} {description}")
            
            # 期間情報を抽出
            period_text = elem.get_text()
            end_date = self._extract_end_date(period_text)
            
            return {
                'campaign_id': f"rakuten_{hash(title)}",
                'title': title,
                'description': description[:200],  # 200文字制限
                'url': campaign_url or source_url,
                'source': '楽天市場',
                'start_date': datetime.now(),
                'end_date': end_date,
                'base_amount': 10000,  # デフォルト想定利用額
                'return_rate': return_rate,
                'required_cards': ['楽天カード'],
                'target_stores': ['楽天市場'],
                'is_dangerous': False,
                'action_steps': [
                    '1. エントリーページでエントリー',
                    '2. 期間中に楽天市場で買い物'
                ]
            }
        
        except Exception as e:
            print(f"パースエラー: {e}")
            return None
    
    def _extract_return_rate(self, text: str) -> int:
        """
        テキストから還元率を抽出
        
        例: "ポイント10倍" → 10
             "20%還元" → 20
        """
        # ポイント倍率
        match = re.search(r'(\d+)倍', text)
        if match:
            return int(match.group(1))
        
        # パーセント表記
        match = re.search(r'(\d+)%', text)
        if match:
            return int(match.group(1))
        
        # デフォルト
        return 5
    
    def _extract_end_date(self, text: str) -> datetime:
        """
        テキストから終了日を抽出
        
        例: "2026年2月28日まで" → datetime(2026, 2, 28)
        """
        # 年月日パターン
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if match:
            year, month, day = map(int, match.groups())
            try:
                return datetime(year, month, day, 23, 59, 59)
            except ValueError:
                pass
        
        # 月日のみパターン
        match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
        if match:
            month, day = map(int, match.groups())
            year = datetime.now().year
            try:
                end_date = datetime(year, month, day, 23, 59, 59)
                # 過去の日付なら来年
                if end_date < datetime.now():
                    end_date = datetime(year + 1, month, day, 23, 59, 59)
                return end_date
            except ValueError:
                pass
        
        # デフォルト: 30日後
        return datetime.now() + timedelta(days=30)


def collect_rakuten_campaigns() -> List[Dict]:
    """楽天キャンペーン収集のエントリーポイント"""
    collector = RakutenCollector()
    return collector.collect_campaigns()


if __name__ == "__main__":
    # テスト実行
    campaigns = collect_rakuten_campaigns()
    print(f"収集件数: {len(campaigns)}")
    for camp in campaigns[:3]:
        print(f"\n{camp['title']}")
        print(f"  還元率: {camp['return_rate']}%")
        print(f"  URL: {camp['url']}")
