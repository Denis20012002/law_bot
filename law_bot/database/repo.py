from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

from .models import Base, Category, Product, Answer

# Создаем подключение к SQLite базе данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./komp_bot.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Нужно для SQLite
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Функция для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CategoryRepo:
    def __init__(self, db: Session = None):
        if db is None:
            self.db = SessionLocal()
            self._own_session = True
        else:
            self.db = db
            self._own_session = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._own_session:
            self.db.close()

    def __del__(self):
        """Закрываем сессию при удалении объекта, если она была создана нами"""
        if hasattr(self, '_own_session') and self._own_session and hasattr(self, 'db'):
            try:
                self.db.close()
            except:
                pass

    def get_all(self):
        categories = self.db.query(Category).all()
        return [{"id": cat.id, "name": cat.name} for cat in categories]

    def add_item(self, item: dict):
        try:
            category = Category(name=item["name"])
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            return category
        except Exception as e:
            self.db.rollback()
            raise


class ProductRepo:
    def __init__(self, db: Session = None):
        if db is None:
            self.db = SessionLocal()
            self._own_session = True
        else:
            self.db = db
            self._own_session = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._own_session:
            self.db.close()

    def __del__(self):
        """Закрываем сессию при удалении объекта, если она была создана нами"""
        if hasattr(self, '_own_session') and self._own_session and hasattr(self, 'db'):
            try:
                self.db.close()
            except:
                pass

    def get_all(self):
        products = self.db.query(Product).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "image": p.image,
                "description": p.description,
                "category_id": p.category_id,
                "cnt": p.cnt,
            }
            for p in products
        ]

    def get_by_category(self, category_id: int):
        products = self.db.query(Product).filter(Product.category_id == category_id).all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "image": p.image,
                "description": p.description,
                "category_id": p.category_id,
                "cnt": p.cnt,
            }
            for p in products
        ]

    def get_by_id(self, product_id: int):
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            return [
                {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "image": product.image,
                    "description": product.description,
                    "category_id": product.category_id,
                    "cnt": product.cnt,
                }
            ]
        return []

    def add_item(self, item: dict):
        try:
            product = Product(
                name=item["name"],
                price=item["price"],
                image=item.get("image", "image"),
                description=item["description"],
                category_id=item["category_id"],
                cnt=item.get("cnt", 0),
            )
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception as e:
            self.db.rollback()
            raise


class AnswerRepo:
    def __init__(self, db: Session = None):
        if db is None:
            self.db = SessionLocal()
            self._own_session = True
        else:
            self.db = db
            self._own_session = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._own_session:
            self.db.close()

    def __del__(self):
        """Закрываем сессию при удалении объекта, если она была создана нами"""
        if hasattr(self, '_own_session') and self._own_session and hasattr(self, 'db'):
            try:
                self.db.close()
            except:
                pass

    def get_all(self):
        """Получить все вопросы"""
        answers = self.db.query(Answer).order_by(Answer.id.desc()).all()
        return [
            {
                "id": a.id,
                "question_text": a.question_text,
                "answer_text": a.answer_text,
                "status": a.status,
                "user_id": a.user_id,
            }
            for a in answers
        ]

    def get_by_id(self, answer_id: int):
        """Получить вопрос по ID"""
        answer = self.db.query(Answer).filter(Answer.id == answer_id).first()
        if answer:
            return {
                "id": answer.id,
                "question_text": answer.question_text,
                "answer_text": answer.answer_text,
                "status": answer.status,
                "user_id": answer.user_id,
            }
        return None

    def add_question(self, question_text: str, user_id: int):
        """Добавить новый вопрос"""
        try:
            answer = Answer(
                question_text=question_text,
                answer_text=None,
                status="в ожидании",
                user_id=user_id,
            )
            self.db.add(answer)
            self.db.commit()
            self.db.refresh(answer)
            return answer
        except Exception as e:
            self.db.rollback()
            raise

    def update_answer(self, answer_id: int, answer_text: str):
        """Обновить ответ на вопрос и изменить статус на 'обработано'"""
        try:
            answer = self.db.query(Answer).filter(Answer.id == answer_id).first()
            if answer:
                answer.answer_text = answer_text
                answer.status = "обработано"
                self.db.commit()
                self.db.refresh(answer)
                return {
                    "id": answer.id,
                    "question_text": answer.question_text,
                    "answer_text": answer.answer_text,
                    "status": answer.status,
                    "user_id": answer.user_id,
                }
            return None
        except Exception as e:
            self.db.rollback()
            raise