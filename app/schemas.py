from models import Product
from sqlalchemy.orm import Session

def generate_summary(session: Session, name_filter: str = None) -> str:
    query = session.query(Product)
    if name_filter:
        query = query.filter(Product.name.ilike(f"%{name_filter}%"))

    products = query.all()
    count = len(products)
    categories = {cat.name for product in products for cat in product.categories}

    lines = [
        f"\n📦 Всего товаров: {count}",
        f"🏷️ Категории: {', '.join(sorted(categories)) if categories else 'Нет'}",
        f"\n🛍️ Список товаров:\n"
    ]

    for p in products:
        lines.append(f"- {p.name} | {p.price} ₽ | 🖼 {p.main_image or 'нет изображения'}")

    return "\n".join(lines)
