import sqlalchemy as db

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
    type =