from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os

Base = declarative_base()

class CardRecord(Base):
    __tablename__ = 'card_history'

    id = Column(Integer, primary_key=True)
    uid = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False) # e.g., 'READ', 'WRITE', 'DETECTED'
    details = Column(String(200))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class DatabaseManager:
    def __init__(self, db_path="sqlite:///acr122u_history.db"):
        self.engine = create_engine(db_path, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_record(self, uid, action, details=""):
        session = self.Session()
        try:
            record = CardRecord(uid=uid, action=action, details=details)
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"DB Error: {e}")
        finally:
            session.close()

    def get_recent_records(self, limit=50):
        session = self.Session()
        try:
            return session.query(CardRecord).order_by(CardRecord.timestamp.desc()).limit(limit).all()
        finally:
            session.close()
