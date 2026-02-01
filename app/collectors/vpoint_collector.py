"""
Vポイント（三井住友カード）キャンペーン収集
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re


class VPointCollector:
    """Vポイントキャンペーン情報収集"""
    
    def __init__(self):
        self.base_urls = [
            "https://www.smbc-card.com/mem/campaign/",  # 三井住友カード
            "https://www.saisoncard.co.jp/campaign/",  # セゾンカード（Vポイント提携）
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def collect_campaigns(self) -> List[Dict]:
        """Vポイントキャンペーン収集"""
        campaigns = []
        
        for url in self.base_urls:
            try:
                campaigns.extend(self._scrape_url(url))
            except Exception as e:
                print(f"Vポイント収集エラー ({url}): {e}")
        
        return campaigns
    
    def _scrape_url(self, url: str) -> List[Dict]:
        """URLからキャンペーン情報を抽出"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            campaigns = []
            
            # キャンペーン要素を探す
            campaign_elements = soup.select('.campaign-list li, .campaign-item, article')
            
            for elem in campaign_elements[:10]:
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
            title_elem = elem.select_one('h2, h3, h4, .title')
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
                elif href.startswith('/'):
                    base = source_url.split('/')[0:3]
                    campaign_url = '/'.join(base) + href
            
            # 説明文
            desc_elem = elem.select_one('.description, .text, p')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # 還元率抽出
            return_rate = self._extract_return_rate(f"{title} {description}")
            
            # 期間抽出
            period_text = elem.get_text()
            end_date = self._extract_end_date(period_text)
            
            # カード判定
            required_cards = []
            if '三井住友' in f"{title} {description}":
                required_cards.append('三井住友カード')
            if 'セゾン' in f"{title} {description}":
                required_cards.append('セゾンカード')
            
            return {
                'campaign_id': f"vpoint_{hash(title)}",
                'title': title,
                'description': description[:200],
                'url': campaign_url or source_url,
                'source': 'Vポイント',
                'start_date': datetime.now(),
                'end_date': end_date,
                'base_amount': 15000,
                'return_rate': return_rate,
                'required_cards': required_cards if required_cards else ['三井住友カード'],
                'target_stores': ['コンビニ', 'スーパー', 'オンラインショップ'],
                'is_dangerous': False,
                'action_steps': [
                    '1. キャンペーンページでエントリー',
                    '2. 対象カードで決済'
                ]
            }
        
        except Exception as e:
            print(f"パースエラー: {e}")
            return None
    
    def _extract_return_rate(self, text: str) -> int:
        """還元率抽出"""
        # ポイント倍率
        match = re.search(r'(\d+)倍', text)
        if match:
            return int(match.group(1))
        
        # パーセント
        match = re.search(r'(\d+)%', text)
        if match:
            return int(match.group(1))
        
        # Vポイント直接指定
        match = re.search(r'(\d+)ポイント', text)
        if match:
            points = int(match.group(1))
            # 1万円利用で何ポイントかを推定
            return max(1, int((points / 10000) * 100))
        
        return 5
    
    def _extract_end_date(self, text: str) -> datetime:
        """終了日抽出"""
        # 年月日
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if match:
            year, month, day = map(int, match.groups())
            try:
                return datetime(year, month, day, 23, 59, 59)
            except ValueError:
                pass
        
        # 月日のみ
        match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
        if match:
            month, day = map(int, match.groups())
            year = datetime.now().year
            try:
                end_date = datetime(year, month, day, 23, 59, 59)
                if end_date < datetime.now():
                    end_date = datetime(year + 1, month, day, 23, 59, 59)
                return end_date
            except ValueError:
                pass
        
        return datetime.now() + timedelta(days=30)


def collect_vpoint_campaigns() -> List[Dict]:
    """Vポイントキャンペーン収集のエントリーポイント"""
    collector = VPointCollector()
    return collector.collect_campaigns()


if __name__ == "__main__":
    campaigns = collect_vpoint_campaigns()
    print(f"収集件数: {len(campaigns)}")
    for camp in campaigns[:3]:
        print(f"\n{camp['title']}")
        print(f"  還元率: {camp['return_rate']}%")
