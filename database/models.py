from sqlalchemy import BigInteger, Integer, String, ForeignKey, Date, Time
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config_data.config import Config, load_config
from datetime import date, time


config: Config = load_config()

DB_HOST = config.db.db_host
DB_PORT = config.db.db_port
DB_NAME = config.db.database
DB_USER = config.db.db_user
DB_PASSWORD = config.db.db_password

engine = create_async_engine(f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}', echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String)
    tg_id = mapped_column(BigInteger)

    appointments = relationship("Appointment", back_populates="user")


class Appointment(Base):
    __tablename__ = 'appointments'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date)
    time: Mapped[time] = mapped_column(Time)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String)

    user = relationship("User", uselist=False, back_populates="appointments")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

