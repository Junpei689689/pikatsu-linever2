"""
開発用テストスクリプト
各モジュールの動作確認
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.profiles.user_profile import UserProfile
from app.collectors.dummy_collector import get_dummy_campaigns
from app.evaluators.personalize import rank_campaigns_for_user, get_missed_amount_estimate
from app.notifiers.formatters import (
    format_paid_top3_text,
    format_free_top3_locked_text,
    format_help_text,
    format_plan_info_text
)
from app.utils.database import init_db


def test_database():
    """データベーステスト"""
    print("=" * 60)
    print("データベーステスト")
    print("=" * 60)
    
    init_db()
    print("✅ データベース初期化成功")
    print()


def test_user_profile():
    """ユーザープロフィールテスト"""
    print("=" * 60)
    print("ユーザープロフィールテスト")
    print("=" * 60)
    
    # テストユーザー作成
    profile = UserProfile("test_user_123")
    print(f"ユーザーID: {profile.line_user_id}")
    print(f"プラン: {profile.plan}")
    print(f"保有カード: {len(profile.cards)}枚")
    print()
    
    # カード追加テスト
    profile.add_card({
        'name': '楽天カード',
        'issuer': '楽天カード株式会社',
        'brand': 'VISA'
    })
    print(f"カード追加後: {len(profile.cards)}枚")
    print(f"✅ カード情報: {profile.cards[0]['name']}")
    print()


def test_dummy_campaigns():
    """ダミーキャンペーンテスト"""
    print("=" * 60)
    print("ダミーキャンペーンテスト")
    print("=" * 60)
    
    campaigns = get_dummy_campaigns()
    print(f"生成されたキャンペーン数: {len(campaigns)}")
    
    for i, camp in enumerate(campaigns, 1):
        print(f"\n{i}. {camp['title']}")
        print(f"   還元率: {camp['return_rate']}%")
        print(f"   地雷: {'⚠️ はい' if camp['is_dangerous'] else '✅ いいえ'}")
    
    print()


def test_ranking():
    """ランキングテスト"""
    print("=" * 60)
    print("ランキングテスト（有料プラン）")
    print("=" * 60)
    
    # ユーザープロフィール準備
    profile = UserProfile("test_user_ranking")
    profile.add_card({
        'name': '楽天カード',
        'issuer': '楽天カード株式会社',
        'brand': 'VISA'
    })
    profile.add_favorite_store('楽天市場')
    
    # キャンペーン取得
    campaigns = get_dummy_campaigns()
    
    # ランキング生成
    ranked = rank_campaigns_for_user(campaigns, profile)
    
    print(f"TOP3:")
    for i, camp in enumerate(ranked[:3], 1):
        print(f"\n{i}. {camp['title']}")
        print(f"   スコア: {camp['score']:.1f}")
        print(f"   期待還元: {camp['expected_return']:,}円")
        print(f"   残日数: {camp['days_remaining']}日")
        print(f"   理由: {camp['reason']}")
    
    print()


def test_formatters():
    """フォーマッターテスト"""
    print("=" * 60)
    print("フォーマッターテスト")
    print("=" * 60)
    
    # 有料プラン用TOP3
    profile = UserProfile("test_formatter")
    campaigns = get_dummy_campaigns()
    ranked = rank_campaigns_for_user(campaigns, profile)
    
    print("\n【有料プラン TOP3表示】")
    print("-" * 60)
    paid_text = format_paid_top3_text(ranked)
    print(paid_text)
    
    print("\n" + "=" * 60)
    
    # 無料プラン用拒否文
    missed = get_missed_amount_estimate(profile)
    print("\n【無料プラン 拒否表示】")
    print("-" * 60)
    free_text = format_free_top3_locked_text(missed)
    print(free_text)
    
    print("\n" + "=" * 60)
    
    # ヘルプ
    print("\n【ヘルプ表示】")
    print("-" * 60)
    help_text = format_help_text()
    print(help_text)
    
    print()


def test_all():
    """全テスト実行"""
    test_database()
    test_user_profile()
    test_dummy_campaigns()
    test_ranking()
    test_formatters()
    
    print("=" * 60)
    print("✅ 全テスト完了")
    print("=" * 60)


if __name__ == "__main__":
    test_all()
