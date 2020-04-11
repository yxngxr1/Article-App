import sqlalchemy
from .db_session import SqlAlchemyBase, orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Category(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
