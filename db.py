import asyncio
from aiohttp import ClientSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase,mapped_column,Mapped

Engine = create_async_engine("sqlite+aiosqlite:///test.db",echo=True)
Session = sessionmaker(bind=Engine,class_=AsyncSession)

class Base(DeclarativeBase):
    id:Mapped[int] = mapped_column(primary_key=True)

class User(Base):
    __tablename__ = "users"

    name:Mapped[str]
    username:Mapped[str]
    email:Mapped[str]

async def init_db():
    async with Engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

async def fetch_users():
    url = "https://jsonplaceholder.typicode.com/users"
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []
            
async def add_user(user_data:dict):
    async with Session() as session:
        user = User(
            id=user_data['id'],
            name=user_data['name'],
            username=user_data['username'],
            email=user_data['email']
        )
        session.add(user)
        await session.commit()

async def delete_user(user_id: int):
    async with Session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user:
            await session.delete(user)
            await session.commit()

async def main():
    await init_db()
    users = await fetch_users()
    for user_data in users:
        await add_user(user_data)

    await delete_user(1)


asyncio.run(main())
