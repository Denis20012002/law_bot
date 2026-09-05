from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    image = Column(String, nullable=True)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    cnt = Column(Integer, nullable=False, default=0)

    category = relationship("Category", back_populates="products")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    answer_text = Column(String, nullable=True)
    status = Column(String, nullable=False, default="в ожидании")  # "в ожидании" или "обработано"
    user_id = Column(Integer, nullable=False)  # ID пользователя из Telegram