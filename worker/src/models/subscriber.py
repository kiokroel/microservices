from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base

UsersBase = declarative_base()

class Subscriber(UsersBase):
    __tablename__ = "subscribers"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    subscriber_id = Column(PG_UUID(as_uuid=True), primary_key=False)
    author_id = Column(PG_UUID(as_uuid=True), primary_key=False)
