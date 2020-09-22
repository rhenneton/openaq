from openaq.common import environment
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class Measure(Base):
    __tablename__ = 'measures'
    id = Column(String(100), primary_key=True)
    date_utc = Column(DateTime)
    value = Column(Float)
    unit = Column(String(16))
    location = Column(String(100))
    city = Column(String(100))
    latitude = Column(Float(precision=3))
    longitude = Column(Float(precision=3))
    country = Column(String(100))


def get_session():
    engine = create_engine(environment.db_url,
                           echo=True)
    Measure.__table__.create(bind=engine, checkfirst=True)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def add_measure_to_db(measure: Measure):
    session = get_session()
    session.merge(measure)
    session.commit()
    session.flush()
    session.close()
