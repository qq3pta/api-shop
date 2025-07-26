import os
import logging
from threading import Thread
from time import sleep
from flask import Flask, request, Response
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time

from models import Base, engine
from schemas import generate_summary
from utils import fetch_products, upsert_products

FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", 3600))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

SessionLocal = sessionmaker(bind=engine)

for i in range(30):
    try:
        engine.connect().close()
        break
    except OperationalError:
        print("⏳ Postgres not ready, retrying...")
        time.sleep(1)
else:
    raise RuntimeError("Postgres didn't start in time")

Base.metadata.create_all(bind=engine)

app = Flask(__name__)

@app.route("/info")
def info():
    session = SessionLocal()
    try:
        name_filter = request.args.get("name")
        summary = generate_summary(session, name_filter)
        return Response(summary, content_type="text/plain; charset=utf-8")
    finally:
        session.close()

def fetch_and_store():
    while True:
        try:
            logging.info("Fetching data from remote API...")
            data = fetch_products()
            session = SessionLocal()
            upsert_products(session, data)
            session.close()
            logging.info(f"Loaded {len(data)} products.")
        except Exception:
            logging.exception("Error during fetch and store")
        sleep(FETCH_INTERVAL)

if __name__ == '__main__':
    Thread(target=fetch_and_store, daemon=True).start()
    app.run(host="0.0.0.0", port=5555, threaded=True)