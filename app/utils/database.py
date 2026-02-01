"""
データベースモデル定義
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class User(Base):
    """ユーザー情報"""
    __tablename__ = "users"
    
    line_user_id = Column(String, primary_key=True, index=True)
    plan = Column(String, default="free")  # free or paid
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 有料プラン情報
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)
    
    # ユーザー属性（有料プラン用）
    cards = Column(JSON, default=list)  # 保有カード情報
    favorite_stores = Column(JSON, default=list)  # 利用店舗
    preferences = Column(JSON, default=dict)  # その他設定


class Campaign(Base):
    """キャンペーン情報"""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, unique=True, index=True)
    
    # 基本情報
    title = Column(String)
    description = Column(String)
    url = Column(String)
    source = Column(String)  # 情報源
    
    # 期間情報
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # 条件情報
    conditions = Column(JSON, default=dict)
    required_cards = Column(JSON, default=list)  # 必要なカード
    target_stores = Column(JSON, default=list)  # 対象店舗
    
    # AI評価結果
    is_dangerous = Column(Boolean, default=False)  # 地雷判定
    danger_reason = Column(String, nullable=True)
    
    # 要約
    summary_short = Column(String, nullable=True)  # OSS要約（40文字）
    
    # メタ情報
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserCampaignAction(Base):
    """ユーザーのキャンペーン行動履歴"""
    __tablename__ = "user_campaign_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    line_user_id = Column(String, index=True)
    campaign_id = Column(String, index=True)
    
    # 行動情報
    action_type = Column(String)  # viewed, clicked, completed
    expected_return = Column(Integer, nullable=True)  # 期待還元額
    actual_return = Column(Integer, nullable=True)  # 実際の還元額
    
    created_at = Column(DateTime, default=datetime.utcnow)


# データベース初期化
def get_db_url():
    """環境変数からDB URLを取得"""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./data/db.sqlite3")
    
    # Renderの場合、相対パスを/tmpに変更
    if db_url.startswith("sqlite:///./"):
        # Render環境かどうかチェック
        if os.getenv("RENDER"):
            # Renderでは /tmp を使用
            db_url = "sqlite:////tmp/db.sqlite3"
        else:
            # ローカル環境では相対パスを絶対パスに変換
            db_path = db_url.replace("sqlite:///./", "")
            abs_path = os.path.abspath(db_path)
            # dataディレクトリを作成
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            db_url = f"sqlite:///{abs_path}"
    
    return db_url


def init_db():
    """データベース初期化"""
    db_url = get_db_url()
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """セッション取得"""
    engine = init_db()
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()