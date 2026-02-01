"""
キャンペーン収集テストスクリプト
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.collectors.campaign_collector import get_campaigns


def test_collection():
    """キャンペーン収集テスト"""
    print("=" * 60)
    print("キャンペーン収集テスト")
    print("=" * 60)
    print()
    
    # 強制的に再収集
    campaigns = get_campaigns(force_refresh=True)
    
    print(f"\n📊 収集結果:")
    print(f"   合計: {len(campaigns)}件")
    
    if campaigns:
        # ソース別集計
        from collections import Counter
        sources = Counter(c['source'] for c in campaigns)
        print(f"\n   ソース別:")
        for source, count in sources.items():
            print(f"     - {source}: {count}件")
        
        # サンプル表示
        print(f"\n   サンプル（上位5件）:")
        for i, camp in enumerate(campaigns[:5], 1):
            print(f"\n   {i}. {camp['title']}")
            print(f"      ソース: {camp['source']}")
            print(f"      還元率: {camp['return_rate']}%")
            print(f"      期限: {camp['end_date'].strftime('%Y-%m-%d')}")
            print(f"      必要カード: {', '.join(camp['required_cards'])}")
            print(f"      地雷: {'⚠️ はい' if camp['is_dangerous'] else '✅ いいえ'}")
            if camp.get('url'):
                print(f"      URL: {camp['url'][:60]}...")
    else:
        print("\n⚠️  キャンペーンが収集できませんでした")
        print("     ネットワーク接続とURLを確認してください")
    
    print("\n" + "=" * 60)
    print("✅ テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    test_collection()
