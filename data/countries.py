import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

class Countries(SqlAlchemyBase):
    __tablename__ = 'countries'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    alpha2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    alpha3 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    region = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    user = orm.relationship('User')