import datetime
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import (BigInteger, Column, DateTime, ForeignKey, Integer, String, Text, func,
                        select)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base, relationship

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


class User(Base):
    """User model class."""

    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    message_count = Column(Integer)

    messages = relationship('Message', back_populates='user')


class Message(Base):
    """Message model class."""

    __tablename__ = 'messages'

    id = Column(BigInteger, primary_key=True)
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.datetime.now,
        nullable=False,
    )
    text = Column(Text, nullable=False)
    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    user = relationship('User', back_populates='messages')


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    """Get database session."""
    async with async_session() as session:
        yield session


app = FastAPI()


@app.on_event('startup')
async def startup_event() -> None:
    await create_all()


class MessageInput(BaseModel):

    text: str
    name: str


class MessageOutput(BaseModel):

    text: str
    name: str
    created_at: datetime.datetime
    order_number: int
    message_count: int


@app.post('/send', response_model=list[MessageOutput])
async def sent(
    db_session: Annotated[AsyncSession, Depends(get_session)],
    message_body: MessageInput,
):
    text = message_body.text
    name = message_body.name

    async with db_session.begin():
        user = await db_session.scalar(select(User).where(User.name == name))
        if not user:
            user = User(name=name, message_count=0)

        user.message_count += 1
        message = Message(text=text, user=user)
        db_session.add_all([user, message])

        messages = (await db_session.execute(
            select(
                Message,
                User,
                func.count().over(order_by=Message.id)
            )
            .join(Message.user)
            .order_by(Message.id.desc())
            .limit(10),
        )).all()

    result = []
    for item in messages:
        item_dict = {
            'name': item.User.name,
            'text': item.Message.text,
            'created_at': item.Message.created_at,
            'order_number': item[2],
            'message_count': item.User.message_count,
        }
        result.append(item_dict)

    return result
