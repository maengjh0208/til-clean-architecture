from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, Text
from sqlalchemy.orm import relationship

from database import Base

# 노트와 태그의 다대다 관계를 나타내기 위한 연결 테이블
note_tag_associtation = Table(
    "note_tag",
    Base.metadata,
    Column("note_id", String(36), ForeignKey("note.id")),
    Column("tag_id", String(36), ForeignKey("tag.id")),
)


class Note(Base):
    __tablename__ = "note"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    memo_date = Column(String(8), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # SQLAlchemy가 제공하는 relationship 함수를 이용해서 다대다 관계를 맺는다.
    tags = relationship(
        "Tag",
        secondary=note_tag_associtation,
        back_populates="notes",
    )


class Tag(Base):
    __tablename__ = "tag"

    id = Column(String(36), primary_key=True)
    name = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    notes = relationship("Note", secondary=note_tag_associtation, back_populates="tags")
