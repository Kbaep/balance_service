import sqlalchemy as db
from datetime import datetime
from app import Base


class Balance(Base):
    __tablename__ = 'balance'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float)


class Operations(Base):
    __tablename__ = 'operations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey('balance.user_id'), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    comment = db.Column(db.String(255), default='Неизвестно')
    create_time = db.Column(db.DateTime, default=datetime.now)
    amount = db.Column(db.Float)