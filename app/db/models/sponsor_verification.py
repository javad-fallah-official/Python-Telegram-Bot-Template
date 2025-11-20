from sqlalchemy import Column, BigInteger, Integer, String, Boolean
from app.db.base import Base

class SponsorVerification(Base):
    __tablename__ = "sponsor_verifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    channels_missing = Column(String, nullable=True)
    policy = Column(String, nullable=False, default="all")
    success = Column(Boolean, nullable=False, default=False)
