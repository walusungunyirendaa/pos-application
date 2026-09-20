from sqlalchemy.orm import Session
from models.category import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int):
        return self.db.query(Category).filter(Category.category_id == category_id).first()

    def get_all(self):
        return self.db.query(Category).all()

    def create(self, category_data: dict):
        db_category = Category(**category_data)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def update(self, db_category: Category, updates: dict):
        for key, value in updates.items():
            setattr(db_category, key, value)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def delete(self, db_category: Category):
        self.db.delete(db_category)
        self.db.commit()