from datetime import datetime

from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, select
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"
    tg_user_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(30))
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    date: Mapped[Optional[str]]
    hero: Mapped[Optional[str]]
    messages: Mapped[List["Messages"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.tg_user_id!r}, name={self.user_name!r}, fullname={self.first_name!r}, hero={self.hero!r})"


class Messages(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    messages: Mapped[str]
    answer_ai: Mapped[Optional[str]]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.tg_user_id"))
    user: Mapped["User"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id!r}, email_address={self.messages!r})"


from sqlalchemy import create_engine

engine = create_engine("sqlite:///tg_database.db", echo=True)
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session

with Session(engine) as session:
    pass
