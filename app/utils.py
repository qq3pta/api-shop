import requests
from models import Product, Category
from sqlalchemy.orm import Session

API_URLS = [
    "https://bot-igor.ru/api/products?on_main=true",
    "https://bot-igor.ru/api/products?on_main=false"
]

def fetch_products():
    combined = []
    for url in API_URLS:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        combined.extend(r.json().get("products", []))
    return combined

def upsert_products(session: Session, data: list):
    # Полностью перезаписываем
    session.query(Product).delete()
    session.query(Category).delete()
    session.commit()

    cat_cache = {}
    for item in data:
        categories = []
        for cat_dict in item.get("categories", []):
            cname = cat_dict.get("Category_Name")
            if not cname:
                continue
            if cname not in cat_cache:
                cat = Category(name=cname)
                session.add(cat)
                session.flush()
                cat_cache[cname] = cat
            categories.append(cat_cache[cname])

        product = Product(
            id=item["Product_ID"],
            name=item["Product_Name"],
            price=item["parameters"][0]["price"] if item.get("parameters") else 0,
            main_image=next(
                (img["Image_URL"] for img in item.get("images", []) if img.get("MainImage")),
                None
            ),
            on_main=item["OnMain"],
            categories=categories
        )
        session.add(product)

    session.commit()