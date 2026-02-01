"""
ユーザープロフィール管理
"""
from datetime import datetime
from typing import List, Dict, Optional
from app.utils.database import get_session, User


class UserProfile:
    """ユーザープロフィールクラス"""
    
    def __init__(self, line_user_id: str):
        self.line_user_id = line_user_id
        self.plan = "free"
        self.cards: List[Dict] = []
        self.favorite_stores: List[str] = []
        self.preferences: Dict = {}
        self.subscription_start: Optional[datetime] = None
        self.subscription_end: Optional[datetime] = None
        
        # DBから読み込み
        self._load_from_db()
    
    def _load_from_db(self):
        """DBからユーザー情報を読み込み"""
        session = get_session()
        try:
            user = session.query(User).filter_by(line_user_id=self.line_user_id).first()
            if user:
                self.plan = user.plan
                self.cards = user.cards or []
                self.favorite_stores = user.favorite_stores or []
                self.preferences = user.preferences or {}
                self.subscription_start = user.subscription_start
                self.subscription_end = user.subscription_end
            else:
                # 新規ユーザーの場合、DBに登録
                self._create_new_user(session)
        finally:
            session.close()
    
    def _create_new_user(self, session):
        """新規ユーザーをDBに登録"""
        new_user = User(
            line_user_id=self.line_user_id,
            plan="free",
            cards=[],
            favorite_stores=[],
            preferences={}
        )
        session.add(new_user)
        session.commit()
    
    def save(self):
        """DBに保存"""
        session = get_session()
        try:
            user = session.query(User).filter_by(line_user_id=self.line_user_id).first()
            if user:
                user.plan = self.plan
                user.cards = self.cards
                user.favorite_stores = self.favorite_stores
                user.preferences = self.preferences
                user.subscription_start = self.subscription_start
                user.subscription_end = self.subscription_end
                user.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    def is_paid_user(self) -> bool:
        """有料ユーザーかどうか"""
        return self.plan == "paid"
    
    def add_card(self, card_info: Dict):
        """カード追加"""
        self.cards.append(card_info)
        self.save()
    
    def add_favorite_store(self, store_name: str):
        """お気に入り店舗追加"""
        if store_name not in self.favorite_stores:
            self.favorite_stores.append(store_name)
            self.save()
    
    def upgrade_to_paid(self):
        """有料プランにアップグレード"""
        self.plan = "paid"
        self.subscription_start = datetime.utcnow()
        self.save()
    
    def downgrade_to_free(self):
        """無料プランにダウングレード"""
        self.plan = "free"
        self.subscription_end = datetime.utcnow()
        self.save()
    
    @staticmethod
    def get_user(line_user_id: str) -> 'UserProfile':
        """ユーザー取得"""
        return UserProfile(line_user_id)
