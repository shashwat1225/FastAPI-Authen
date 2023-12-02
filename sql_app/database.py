from typing import Tuple
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from configuration.database_config import db_config


Base = declarative_base()


def get_db() -> Tuple[Session, Engine]:

    sqlalchemy_database_url = (
            "postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(db)s" % db_config
    )
    engine = create_engine(sqlalchemy_database_url)
    local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = local_session()
    return db, engine