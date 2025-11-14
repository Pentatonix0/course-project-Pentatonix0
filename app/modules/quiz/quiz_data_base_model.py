from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_base.app_declarative_base import Base


class Quiz(Base):
    __tablename__ = "quiz"

    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.model_id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # при желании можно связать с пользователем (если есть модель User)
    author = relationship("User", back_populates="created_quizzes")
