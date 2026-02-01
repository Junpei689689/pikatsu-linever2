"""
LINE Webhook サーバー
"""
import os
from fastapi import FastAPI, Request, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from dotenv import load_dotenv

from app.profiles.user_profile import UserProfile
from app.evaluators.personalize import rank_campaigns_for_user, get_missed_amount_estimate
from app.notifiers.formatters import (
    format_paid_top3_text,
    format_free_top3_locked_text,
    format_help_text,
    format_plan_info_text
)
from app.collectors.campaign_collector import get_campaigns
from app.collectors.dummy_collector import get_dummy_campaigns
from app.utils.database import init_db

# 環境変数読み込み
load_dotenv()

# LINE設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET must be set")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# FastAPI初期化
app = FastAPI(title="ポイ活LINE Bot")

# DB初期化
init_db()


@app.on_event("startup")
async def startup_event():
    """起動時処理"""
    print("🚀 ポイ活LINE Bot 起動")
    print(f"   PORT: {os.getenv('PORT', 8000)}")


@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"status": "ok", "service": "poikatsu-line-bot"}


@app.post("/webhook")
async def webhook(request: Request):
    """LINE Webhook エンドポイント"""
    signature = request.headers.get('X-Line-Signature')
    body = await request.body()
    body_str = body.decode('utf-8')
    
    try:
        handler.handle(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):  # type: ignore
    """メッセージイベント処理"""
    # 型安全な属性アクセス
    if not hasattr(event.source, 'user_id') or not event.source.user_id:  # type: ignore
        return
    
    user_id: str = event.source.user_id  # type: ignore
    
    # メッセージテキスト取得（型チェック）
    if not isinstance(event.message, TextMessageContent):
        return
    
    msg_text = event.message.text.strip().lower()
    
    # プラン判定
    plan = _load_plan(user_id)
    
    # コマンド処理
    if msg_text in ['ping', 'p']:
        reply_text = "pong"
    
    elif msg_text in ['help', 'h', '使い方']:
        reply_text = format_help_text()
    
    elif msg_text == 'plan':
        reply_text = format_plan_info_text(plan)
    
    elif msg_text in ['top3', 't']:
        reply_text = _handle_top3_command(user_id, plan)
    
    else:
        reply_text = f"コマンドが認識できませんでした。\n「help」で使い方を確認できます。"
    
    # LINE返信
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(  # type: ignore
            ReplyMessageRequest(  # type: ignore
                reply_token=event.reply_token,  # type: ignore
                messages=[TextMessage(text=reply_text)]  # type: ignore
            )
        )


def _load_plan(user_id: str) -> str:
    """
    ユーザープラン読み込み
    
    優先順位:
    1. 環境変数 FORCE_PLAN（デバッグ用）
    2. UserProfile.plan
    """
    force_plan = os.getenv('FORCE_PLAN')
    if force_plan in ['free', 'paid']:
        return force_plan
    
    profile = UserProfile.get_user(user_id)
    return str(profile.plan)


def _handle_top3_command(user_id: str, plan: str) -> str:
    """
    TOP3コマンド処理
    
    有料: TOP3詳細表示
    無料: 拒否文＋取り逃し推定額
    """
    profile = UserProfile.get_user(user_id)
    
    if plan == 'paid':
        # 有料: TOP3詳細
        # 実キャンペーン取得（キャッシュ優先）
        campaigns = get_campaigns(force_refresh=False)
        
        # キャンペーンがない場合はダミー使用
        if not campaigns:
            print("⚠️ 実キャンペーンが取得できないため、ダミーを使用")
            campaigns = get_dummy_campaigns()
        
        ranked = rank_campaigns_for_user(campaigns, profile)
        return format_paid_top3_text(ranked)
    
    else:
        # 無料: 拒否文
        missed_amount = get_missed_amount_estimate(profile)
        return format_free_top3_locked_text(missed_amount)


def _get_dummy_campaigns() -> list:
    """ダミーキャンペーン取得（後方互換）"""
    return get_dummy_campaigns()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)