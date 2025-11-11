from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)


class Base(DeclarativeBase):
    __abstract__ = True

    # Используем declared_attr для динамического определения колонок
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    model_id: Mapped[int] = mapped_column(primary_key=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )
