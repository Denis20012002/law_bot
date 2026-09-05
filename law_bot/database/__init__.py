from .models import Base, Category, Product, Answer
from .repo import CategoryRepo, ProductRepo, AnswerRepo, get_db, engine, SessionLocal

# Создаем таблицы при импорте модуля
def init_db():
    """Инициализация базы данных - создание всех таблиц"""
    Base.metadata.create_all(bind=engine)


# Автоматически создаем таблицы при импорте
init_db()