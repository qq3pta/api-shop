from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, create_engine
from sqlalchemy.orm import declarative_base, relationship
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

product_category = Table(
    'product_category', Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id', ondelete="CASCADE")),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete="CASCADE"))
)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    main_image = Column(String)
    on_main = Column(Boolean, default=False)
    categories = relationship(
        "Category",
        secondary=product_category,
        back_populates="products",
        cascade="all, delete"
    )
class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    products = relationship("Product", secondary=product_category, back_populates="categories")
