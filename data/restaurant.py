import sqlalchemy
from .db_session import SqlAlchemyBase


class Rest(SqlAlchemyBase):
    __tablename__ = 'restaurant'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    prc = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    geo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cus = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tm = sqlalchemy.Column(sqlalchemy.String,
                           nullable=True)
    adr = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    cord = sqlalchemy.Column(sqlalchemy.String, nullable=True)
