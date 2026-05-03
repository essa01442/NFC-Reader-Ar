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

class CardRegistry(Base):
    __tablename__ = 'card_registry'
    id = Column(Integer, primary_key=True)
    card_number = Column(Integer, unique=True)  # 1-200
    uid = Column(String(50), unique=True)       # Serial from reader
    domain = Column(String(200))                # Domain/Service
    note = Column(String(500))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

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

    # ── Card Registry Methods ──────────────────────────────────────────

    def get_card_from_registry(self, uid):
        session = self.Session()
        try:
            return session.query(CardRegistry).filter_by(uid=uid).first()
        finally:
            session.close()

    def upsert_card_registry(self, card_number, uid, domain, note):
        session = self.Session()
        try:
            card = session.query(CardRegistry).filter_by(card_number=card_number).first()
            if card:
                card.uid = uid
                card.domain = domain
                card.note = note
                card.updated_at = datetime.datetime.utcnow()
            else:
                card = CardRegistry(card_number=card_number, uid=uid, domain=domain, note=note)
                session.add(card)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"DB Registry Error: {e}")
            return False
        finally:
            session.close()

    def delete_card_from_registry(self, card_number):
        session = self.Session()
        try:
            card = session.query(CardRegistry).filter_by(card_number=card_number).first()
            if card:
                session.delete(card)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"DB Registry Delete Error: {e}")
            return False
        finally:
            session.close()

    def get_all_registry_entries(self):
        session = self.Session()
        try:
            return session.query(CardRegistry).order_by(CardRegistry.card_number).all()
        finally:
            session.close()
