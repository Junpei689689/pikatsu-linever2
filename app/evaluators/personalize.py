"""
個人最適化・キャンペーンランキング（有料プラン用）
"""
from datetime import datetime
from typing import List, Dict
from app.profiles.user_profile import UserProfile


def rank_campaigns_for_user(campaigns: List[Dict], profile: UserProfile) -> List[Dict]:
    """
    ユーザーに最適化されたキャンペーンランキング
    
    Args:
        campaigns: キャンペーンリスト
        profile: ユーザープロフィール
    
    Returns:
        ランク付けされたキャンペーンリスト（上位から順）
    """
    ranked = []
    
    for campaign in campaigns:
        score = _calculate_campaign_score(campaign, profile)
        expected_return = _calculate_expected_return(campaign, profile)
        days_remaining = _calculate_days_remaining(campaign)
        
        ranked.append({
            **campaign,
            'score': score,
            'expected_return': expected_return,
            'days_remaining': days_remaining,
            'reason': _generate_reason(campaign, profile, expected_return, days_remaining)
        })
    
    # スコア順にソート
    ranked.sort(key=lambda x: x['score'], reverse=True)
    
    return ranked


def _calculate_campaign_score(campaign: Dict, profile: UserProfile) -> float:
    """
    キャンペーンスコア算出
    
    スコア要素:
    - 期待還元額
    - 残日数（締切が近いほど高得点）
    - カード保有状況
    - 店舗利用状況
    """
    score = 0.0
    
    # 期待還元額（最大50点）
    expected_return = _calculate_expected_return(campaign, profile)
    score += min(expected_return / 100, 50)
    
    # 残日数（最大30点・締切が近いほど高得点）
    days_remaining = _calculate_days_remaining(campaign)
    if days_remaining <= 3:
        score += 30
    elif days_remaining <= 7:
        score += 20
    elif days_remaining <= 14:
        score += 10
    
    # カード保有（最大20点）
    if _has_required_card(campaign, profile):
        score += 20
    else:
        score -= 10  # 必要カード未保有はマイナス
    
    # 地雷判定（大幅減点）
    if campaign.get('is_dangerous', False):
        score -= 50
    
    return max(score, 0)


def _calculate_expected_return(campaign: Dict, profile: UserProfile) -> int:
    """
    期待還元額算出（円）
    
    ユーザーの平均利用額と還元率から推定
    """
    base_amount = campaign.get('base_amount', 10000)  # 想定利用額
    return_rate = campaign.get('return_rate', 5)  # 還元率（%）
    
    # ユーザーの利用傾向による補正
    user_multiplier = _get_user_spending_multiplier(campaign, profile)
    
    expected = int(base_amount * (return_rate / 100) * user_multiplier)
    return expected


def _calculate_days_remaining(campaign: Dict) -> int:
    """締切までの残日数計算"""
    end_date = campaign.get('end_date')
    if not end_date:
        return 999  # 締切不明
    
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    delta = end_date - datetime.now(end_date.tzinfo)
    return max(delta.days, 0)


def _has_required_card(campaign: Dict, profile: UserProfile) -> bool:
    """必要なカードを保有しているか"""
    required_cards = campaign.get('required_cards', [])
    if not required_cards:
        return True  # カード不要
    
    user_cards = [card.get('name', '') for card in profile.cards]
    return any(req in user_cards for req in required_cards)


def _get_user_spending_multiplier(campaign: Dict, profile: UserProfile) -> float:
    """
    ユーザーの支出傾向による係数
    
    よく使う店舗のキャンペーンなら高く、そうでなければ低く
    """
    target_stores = campaign.get('target_stores', [])
    
    if not target_stores:
        return 1.0
    
    # お気に入り店舗と一致
    if any(store in profile.favorite_stores for store in target_stores):
        return 1.5
    
    return 0.8


def _generate_reason(campaign: Dict, profile: UserProfile, expected_return: int, days_remaining: int) -> str:
    """
    おすすめ理由を自然文で生成（2行）
    
    現時点では定型文ベース
    将来的にOpenAI APIで生成
    """
    reasons = []
    
    # 期待還元額
    if expected_return >= 1000:
        reasons.append(f"期待還元額が約{expected_return:,}円と高額")
    elif expected_return >= 500:
        reasons.append(f"約{expected_return:,}円の還元が見込める")
    
    # 締切
    if days_remaining <= 3:
        reasons.append(f"締切まで残り{days_remaining}日")
    elif days_remaining <= 7:
        reasons.append(f"締切が{days_remaining}日後に迫っている")
    
   # カード保有
    if _has_required_card(campaign, profile):
        required_cards = campaign.get('required_cards', [])
        if required_cards and len(required_cards) > 0:
            card_name = required_cards[0]
            if card_name:
                reasons.append(f"{card_name}保有で条件クリア")
                
    # デフォルト
    if not reasons:
        reasons.append("あなたの利用傾向に合致")
        reasons.append("手続きが簡単")
    
    return "。".join(reasons[:2]) + "。"


def get_missed_amount_estimate(profile: UserProfile) -> int:
    """
    取り逃し推定額（無料プラン用）
    
    有料プランだったら得られたであろう金額を推定
    """
    # ダミー実装（実際はキャンペーン履歴から算出）
    base = 5000
    
    # ユーザー属性による補正
    if len(profile.cards) > 0:
        base += len(profile.cards) * 500
    
    if len(profile.favorite_stores) > 0:
        base += len(profile.favorite_stores) * 300
    
    return base
