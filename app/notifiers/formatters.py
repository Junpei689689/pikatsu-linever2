"""
LINE通知フォーマッター
無料 / 有料プランの表示差を制御
"""
from typing import List, Dict


def format_paid_top3_text(ranked_campaigns: List[Dict]) -> str:
    """
    有料プラン用 TOP3表示
    
    完全な意思決定情報を提供:
    - キャンペーン名
    - 期待還元額
    - 残日数
    - おすすめ理由（自然文）
    - やること（手順）
    - URL
    """
    if not ranked_campaigns:
        return "現在、おすすめのキャンペーンはありません。"
    
    top3 = ranked_campaigns[:3]
    
    lines = ["📊 あなた向けTOP3\n"]
    
    for i, camp in enumerate(top3, 1):
        title = camp.get('title', 'キャンペーン')
        expected_return = camp.get('expected_return', 0)
        days_remaining = camp.get('days_remaining', 0)
        reason = camp.get('reason', '')
        url = camp.get('url', '')
        
        # ランキング表示
        medal = ["🥇", "🥈", "🥉"][i - 1]
        lines.append(f"{medal} {title}")
        
        # 理由（2行）
        lines.append(f"{reason}")
        
        # 金額・残日数
        lines.append(f"💰 期待還元: 約{expected_return:,}円")
        lines.append(f"⏰ 残り: {days_remaining}日")
        
        # やること
        steps = _get_action_steps(camp)
        if steps:
            lines.append(f"✅ やること:")
            for step in steps:
                lines.append(f"  {step}")
        
        # URL
        if url:
            lines.append(f"🔗 {url}")
        
        lines.append("")  # 空行
    
    return "\n".join(lines)


def format_free_top3_locked_text(missed_amount: int) -> str:
    """
    無料プラン用 TOP3拒否表示
    
    提供情報:
    - 機能が有料限定である旨
    - 取り逃し推定額のみ
    
    提供しない情報:
    - キャンペーン名
    - 締切日・残日数
    - 期待還元額の内訳
    - 具体的な手順
    - URL
    """
    text = f"""🔒 この機能は有料プラン限定です

無料プランでは、あなた専用のTOP3キャンペーンを表示できません。

💸 今月の取り逃し推定額
約{missed_amount:,}円

有料プラン（月額1,280円）では:
✅ あなた向けTOP3（優先度順）
✅ 期待還元額の自動計算
✅ 締切リマインド
✅ やるべきことを完全ガイド

今すぐ始める → [プラン変更はこちら]
"""
    return text


def format_help_text() -> str:
    """ヘルプメッセージ"""
    return """🤖 使い方

【コマンド一覧】
ping (p) - 接続確認
help (h) - このメッセージを表示
plan - 現在のプラン確認
top3 (t) - あなた向けTOP3表示 ⭐️

【無料プラン】
週2回の高還元キャンペーン通知

【有料プラン（月額1,280円）】
✅ 個人最適化されたTOP3
✅ 期待還元額の自動計算
✅ 締切リマインド
✅ 地雷キャンペーン除外
✅ 月次成果レポート

💡 詳細はWebサイトをチェック
"""


def format_plan_info_text(plan: str) -> str:
    """プラン情報表示"""
    if plan == "paid":
        return """📋 現在のプラン

✨ 有料プラン（月額1,280円）

ご利用中の機能:
✅ 個人最適化TOP3
✅ 期待還元額算出
✅ 締切リマインド
✅ 地雷キャンペーン除外
✅ 月次成果レポート

いつもご利用ありがとうございます！
"""
    else:
        return """📋 現在のプラン

🆓 無料プラン

利用可能な機能:
・週2回の高還元キャンペーン通知
・AI要約（短文）

🔒 利用できない機能:
・個人最適化TOP3
・期待還元額算出
・締切リマインド

💡 有料プラン（月額1,280円）で
すべての機能が使えます！
"""


def _get_action_steps(campaign: Dict) -> List[str]:
    """
    やるべきステップを生成
    
    最大2ステップ
    """
    steps = campaign.get('action_steps', [])
    
    if not steps:
        # デフォルトステップ
        steps = [
            "1. リンクからキャンペーンページへ",
            "2. エントリーボタンを押す"
        ]
    
    return steps[:2]  # 最大2ステップ


def format_weekly_notification(campaigns: List[Dict], plan: str) -> str:
    """
    週次通知用フォーマット
    
    Args:
        campaigns: 今週の注目キャンペーン
        plan: ユーザープラン
    """
    if plan == "free":
        return _format_free_weekly(campaigns)
    else:
        return _format_paid_weekly(campaigns)


def _format_free_weekly(campaigns: List[Dict]) -> str:
    """無料プラン週次通知"""
    if not campaigns:
        return "今週の高還元キャンペーンはありません。"
    
    lines = ["📢 今週の高還元キャンペーン\n"]
    
    for camp in campaigns[:3]:
        title = camp.get('title', '')
        summary = camp.get('summary_short', '')
        
        lines.append(f"・{title}")
        if summary:
            lines.append(f"  {summary}")
        lines.append("")
    
    lines.append("💡 詳細は「top3」コマンドで確認（有料限定）")
    
    return "\n".join(lines)


def _format_paid_weekly(campaigns: List[Dict]) -> str:
    """有料プラン週次通知"""
    if not campaigns:
        return "今週のおすすめキャンペーンはありません。"
    
    lines = ["📢 今週のあなた向けキャンペーン\n"]
    
    total_expected = 0
    
    for camp in campaigns[:5]:
        title = camp.get('title', '')
        expected_return = camp.get('expected_return', 0)
        days_remaining = camp.get('days_remaining', 0)
        
        total_expected += expected_return
        
        lines.append(f"・{title}")
        lines.append(f"  💰 約{expected_return:,}円 ⏰ 残り{days_remaining}日")
        lines.append("")
    
    lines.append(f"今週の合計期待還元: 約{total_expected:,}円")
    lines.append("\n詳細は「top3」コマンドでチェック！")
    
    return "\n".join(lines)
