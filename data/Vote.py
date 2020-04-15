import sqlalchemy
from .db_session import SqlAlchemyBase, orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Vote(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'votes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    article_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("articles.id"))
    vote = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # votes: up, down, un
