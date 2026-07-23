import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config import DB_PATH
from models import Base

logger = logging.getLogger(__name__)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("数据库初始化完成")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
