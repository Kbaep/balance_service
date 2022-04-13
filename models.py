import sqlalchemy as db

from app import Base


class Balance(Base):
    __tablename__ = 'balance'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float)