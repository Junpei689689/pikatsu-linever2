"""
OSS LLM要約（無料プラン用）
Qwen2.5-7B-Instruct via Ollama
"""
import os
import requests
from typing import Optional


class OSSummarizer:
    """OSS LLMによる要約生成"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    
    def summarize_campaign(self, campaign_text: str, max_length: int = 40) -> str:
        """
        キャンペーン情報を短文要約
        
        Args:
            campaign_text: キャンペーン情報の元テキスト
            max_length: 最大文字数（デフォルト40文字）
        
        Returns:
            要約文（約40文字）
        """
        prompt = f"""以下のキャンペーン情報を{max_length}文字以内で簡潔に要約してください。
重要なポイント（対象サービス、還元率、条件）のみを含めてください。
判断や評価は含めず、事実のみを記述してください。

キャンペーン情報:
{campaign_text}

要約（{max_length}文字以内）:"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 100
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("response", "").strip()
                
                # 文字数制限
                if len(summary) > max_length + 10:
                    summary = summary[:max_length] + "..."
                
                return summary
            else:
                return self._fallback_summary(campaign_text, max_length)
        
        except Exception as e:
            print(f"OSS要約エラー: {e}")
            return self._fallback_summary(campaign_text, max_length)
    
    def _fallback_summary(self, text: str, max_length: int) -> str:
        """フォールバック要約（LLM使用不可時）"""
        # 単純な切り詰め
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
    
    def batch_summarize(self, campaigns: list) -> list:
        """
        複数キャンペーンの一括要約
        
        Args:
            campaigns: キャンペーン情報のリスト
        
        Returns:
            要約済みキャンペーンのリスト
        """
        results = []
        for campaign in campaigns:
            campaign_text = f"{campaign.get('title', '')} {campaign.get('description', '')}"
            summary = self.summarize_campaign(campaign_text)
            campaign['summary_short'] = summary
            results.append(campaign)
        
        return results
    
    def is_available(self) -> bool:
        """Ollamaが利用可能かチェック"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
