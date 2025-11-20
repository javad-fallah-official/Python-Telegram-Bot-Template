from sqlalchemy import Column, BigInteger, String, Boolean
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    referred_by = Column(BigInteger, nullable=True)
