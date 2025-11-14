from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_base.app_declarative_base import Base
from app.data_base.mixin_models import SchemaMixin


class User(SchemaMixin, Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)  # password_hash

    # Связь с квизами (1 пользователь → много квизов)
    created_quizzes = relationship(
        "Quiz", back_populates="author", cascade="all, delete-orphan"
    )
