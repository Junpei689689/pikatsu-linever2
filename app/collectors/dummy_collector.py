"""
ダミーキャンペーン生成（開発・テスト用）
"""
from datetime import datetime, timedelta
from typing import List, Dict
import random


def get_dummy_campaigns() -> List[Dict]:
    """
    テスト用ダミーキャンペーン生成
    
    実際の運用では collectors が実キャンペーンを収集
    """
    now = datetime.now()
    
    campaigns = [
        {
            'campaign_id': 'rakuten_super_sale_2026',
            'title': '楽天スーパーセール',
            'description': '全ショップ対象！ポイント最大44倍',
            'url': 'https://event.rakuten.co.jp/campaign/supersale/',
            'source': '楽天市場',
            'start_date': now - timedelta(days=2),
            'end_date': now + timedelta(days=5),
            'base_amount': 20000,
            'return_rate': 10,
            'required_cards': ['楽天カード'],
            'target_stores': ['楽天市場'],
            'is_dangerous': False,
            'action_steps': [
                '1. エントリーページでエントリー',
                '2. 期間中に買い物'
            ]
        },
        {
            'campaign_id': 'paypay_jumbo_2026',
            'title': 'PayPay ジャンボ',
            'description': '最大1,000%還元！全国のPayPay加盟店で',
            'url': 'https://paypay.ne.jp/event/jumbo/',
            'source': 'PayPay',
            'start_date': now - timedelta(days=5),
            'end_date': now + timedelta(days=2),
            'base_amount': 10000,
            'return_rate': 5,
            'required_cards': [],
            'target_stores': ['コンビニ', 'スーパー'],
            'is_dangerous': False,
            'action_steps': [
                '1. PayPayアプリを開く',
                '2. 対象店舗で決済'
            ]
        },
        {
            'campaign_id': 'dcard_gold_20percent',
            'title': 'dカードGOLD 20%還元',
            'description': 'ドコモ料金の支払いで20%ポイント還元',
            'url': 'https://d-card.jp/st/campaigns/gold20/',
            'source': 'dカード',
            'start_date': now - timedelta(days=10),
            'end_date': now + timedelta(days=20),
            'base_amount': 15000,
            'return_rate': 20,
            'required_cards': ['dカード GOLD'],
            'target_stores': ['ドコモ'],
            'is_dangerous': False,
            'action_steps': [
                '1. dカードGOLD支払い設定',
                '2. 自動適用（手続き不要）'
            ]
        },
        {
            'campaign_id': 'aupay_50percent_dangerous',
            'title': 'au PAY 50%還元（要注意）',
            'description': '条件達成で50%還元！ただし上限500円',
            'url': 'https://aupay.auone.jp/campaign/50percent/',
            'source': 'au PAY',
            'start_date': now - timedelta(days=1),
            'end_date': now + timedelta(days=14),
            'base_amount': 5000,
            'return_rate': 50,
            'required_cards': [],
            'target_stores': ['ローソン'],
            'is_dangerous': True,  # 地雷判定
            'danger_reason': '還元率は高いが上限500円のため、実質還元額が低い',
            'action_steps': [
                '1. au PAYアプリ起動',
                '2. ローソンで決済'
            ]
        },
        {
            'campaign_id': 'amazon_prime_day',
            'title': 'Amazonプライムデー',
            'description': 'プライム会員限定セール！最大50%オフ',
            'url': 'https://www.amazon.co.jp/primeday',
            'source': 'Amazon',
            'start_date': now + timedelta(days=1),
            'end_date': now + timedelta(days=3),
            'base_amount': 30000,
            'return_rate': 15,
            'required_cards': [],
            'target_stores': ['Amazon'],
            'is_dangerous': False,
            'action_steps': [
                '1. プライム会員確認',
                '2. セール商品をチェック'
            ]
        }
    ]
    
    # ランダムで3-5件返す
    num_campaigns = random.randint(3, 5)
    return random.sample(campaigns, num_campaigns)


def get_dummy_weekly_campaigns() -> List[Dict]:
    """週次通知用ダミーキャンペーン"""
    all_campaigns = get_dummy_campaigns()
    
    # 週次通知用に軽量化
    weekly = []
    for camp in all_campaigns:
        weekly.append({
            'title': camp['title'],
            'summary_short': f"{camp['source']}で{camp['return_rate']}%還元",
            'expected_return': int(camp['base_amount'] * camp['return_rate'] / 100),
            'days_remaining': (camp['end_date'] - datetime.now()).days
        })
    
    return weekly
