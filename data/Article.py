import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase, orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Article(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'articles'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.CLOB, nullable=True)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    photo_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    views = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
