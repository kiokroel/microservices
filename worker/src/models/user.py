from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base

UsersBase = declarative_base()

class User(UsersBase):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    subscription_key = Column(Text, nullable=True)
