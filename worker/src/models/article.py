from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String

BackendBase = declarative_base()

class Article(BackendBase):
    __tablename__ = "articles"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    title = Column(String(255), nullable=False)
