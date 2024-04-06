import datetime
import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    region = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('countries.id'), nullable=False)

    country = orm.relationship('Countries', back_populates='user')
    news = orm.relationship("News", back_populates='user')


    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
