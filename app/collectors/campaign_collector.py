"""
統合キャンペーン収集マネージャー
すべてのソースからキャンペーンを収集・統合
"""
from typing import List, Dict
import json
from datetime import datetime
from pathlib import Path

from app.collectors.rakuten_collector import collect_rakuten_campaigns
from app.collectors.vpoint_collector import collect_vpoint_campaigns
from app.collectors.dpoint_collector import collect_dpoint_campaigns


class CampaignCollector:
    """キャンペーン収集の統合管理"""
    
    def __init__(self, cache_file: str = None):
        self.cache_file = cache_file or "data/campaigns_cache.json"
    
    def collect_all(self) -> List[Dict]:
        """
        全ソースからキャンペーンを収集
        
        Returns:
            統合されたキャンペーンリスト
        """
        all_campaigns = []
        
        print("📊 キャンペーン収集開始...")
        
        # 楽天
        print("  - 楽天ポイント収集中...")
        try:
            rakuten = collect_rakuten_campaigns()
            all_campaigns.extend(rakuten)
            print(f"    ✅ {len(rakuten)}件")
        except Exception as e:
            print(f"    ❌ エラー: {e}")
        
        # Vポイント
        print("  - Vポイント収集中...")
        try:
            vpoint = collect_vpoint_campaigns()
            all_campaigns.extend(vpoint)
            print(f"    ✅ {len(vpoint)}件")
        except Exception as e:
            print(f"    ❌ エラー: {e}")
        
        # dポイント
        print("  - dポイント収集中...")
        try:
            dpoint = collect_dpoint_campaigns()
            all_campaigns.extend(dpoint)
            print(f"    ✅ {len(dpoint)}件")
        except Exception as e:
            print(f"    ❌ エラー: {e}")
        
        print(f"\n✅ 合計 {len(all_campaigns)}件のキャンペーンを収集")
        
        # 重複排除
        all_campaigns = self._deduplicate(all_campaigns)
        print(f"   重複排除後: {len(all_campaigns)}件")
        
        # キャッシュ保存
        self._save_cache(all_campaigns)
        
        return all_campaigns
    
    def get_cached_campaigns(self) -> List[Dict]:
        """
        キャッシュからキャンペーン取得
        
        Returns:
            キャッシュされたキャンペーン（なければ空リスト）
        """
        try:
            cache_path = Path(self.cache_file)
            if not cache_path.exists():
                return []
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # キャッシュの有効期限チェック（24時間）
            cached_at = datetime.fromisoformat(data.get('cached_at', '2000-01-01'))
            age_hours = (datetime.now() - cached_at).total_seconds() / 3600
            
            if age_hours > 24:
                print("⚠️  キャッシュが古いため再収集が必要")
                return []
            
            campaigns = data.get('campaigns', [])
            
            # 日時文字列をdatetimeに戻す
            for camp in campaigns:
                if isinstance(camp.get('start_date'), str):
                    camp['start_date'] = datetime.fromisoformat(camp['start_date'])
                if isinstance(camp.get('end_date'), str):
                    camp['end_date'] = datetime.fromisoformat(camp['end_date'])
            
            print(f"✅ キャッシュから{len(campaigns)}件のキャンペーンを読み込み")
            return campaigns
        
        except Exception as e:
            print(f"キャッシュ読み込みエラー: {e}")
            return []
    
    def _save_cache(self, campaigns: List[Dict]):
        """キャンペーンをキャッシュに保存"""
        try:
            cache_path = Path(self.cache_file)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            # datetimeをISO形式文字列に変換
            campaigns_serializable = []
            for camp in campaigns:
                camp_copy = camp.copy()
                if isinstance(camp_copy.get('start_date'), datetime):
                    camp_copy['start_date'] = camp_copy['start_date'].isoformat()
                if isinstance(camp_copy.get('end_date'), datetime):
                    camp_copy['end_date'] = camp_copy['end_date'].isoformat()
                campaigns_serializable.append(camp_copy)
            
            data = {
                'cached_at': datetime.now().isoformat(),
                'count': len(campaigns),
                'campaigns': campaigns_serializable
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 キャッシュ保存: {cache_path}")
        
        except Exception as e:
            print(f"キャッシュ保存エラー: {e}")
    
    def _deduplicate(self, campaigns: List[Dict]) -> List[Dict]:
        """
        重複キャンペーンを排除
        
        タイトルが同じものは重複とみなす
        """
        seen = set()
        unique = []
        
        for camp in campaigns:
            title = camp.get('title', '')
            if title and title not in seen:
                seen.add(title)
                unique.append(camp)
        
        return unique


def get_campaigns(force_refresh: bool = False) -> List[Dict]:
    """
    キャンペーン取得のエントリーポイント
    
    Args:
        force_refresh: Trueの場合、キャッシュを無視して再収集
    
    Returns:
        キャンペーンリスト
    """
    collector = CampaignCollector()
    
    if force_refresh:
        return collector.collect_all()
    
    # まずキャッシュを試す
    campaigns = collector.get_cached_campaigns()
    
    # キャッシュがなければ収集
    if not campaigns:
        campaigns = collector.collect_all()
    
    return campaigns


if __name__ == "__main__":
    # テスト実行
    campaigns = get_campaigns(force_refresh=True)
    
    print(f"\n📋 収集結果:")
    print(f"   合計: {len(campaigns)}件")
    
    # ソース別集計
    from collections import Counter
    sources = Counter(c['source'] for c in campaigns)
    print(f"\n   ソース別:")
    for source, count in sources.items():
        print(f"     - {source}: {count}件")
    
    # サンプル表示
    print(f"\n   サンプル（上位3件）:")
    for i, camp in enumerate(campaigns[:3], 1):
        print(f"\n   {i}. {camp['title']}")
        print(f"      還元率: {camp['return_rate']}%")
        print(f"      期限: {camp['end_date'].strftime('%Y-%m-%d')}")
        print(f"      URL: {camp['url'][:50]}...")
