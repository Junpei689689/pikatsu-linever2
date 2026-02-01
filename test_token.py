# test_token.py を作成して実行
from dotenv import load_dotenv
import os
import requests

load_dotenv()

token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
print(f"トークン（最初の30文字）: {token[:30] if token else 'None'}")

# LINE APIにテストリクエスト
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = requests.get('https://api.line.me/v2/bot/info', headers=headers)

print(f"\nステータスコード: {response.status_code}")
print(f"レスポンス: {response.json()}")

if response.status_code == 200:
    print("\n✅ トークンは有効です！")
else:
    print("\n❌ トークンが無効です")