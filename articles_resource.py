from flask_restful import Resource, abort
from flask import jsonify, request
from data import db_session
from data.Article import Article


def abort_if_article_not_found(article_id):
    session = db_session.create_session()
    articles = session.query(Article).get(article_id)
    if not articles:
        abort (409, message=f"Article {article_id} not found")


class ArticleListResource(Resource):
    def get(self):
        session = db_session.create_session()
        articles = session.query(Article).filter(Article.is_private == False).all()
        return jsonify({'articles': [item.to_dict(
                only=('id',
                      'title',
                      'description',
                      'user_id',)) for item in articles]
                      })


class ArticleResource(Resource):
    def get(self, article_id):
        abort_if_article_not_found(article_id)
        session = db_session.create_session()
        article = session.query(Article).get(article_id)
        return jsonify({'article': article.to_dict(
                only=('id',
                      'title',
                      'description',
                      'content',
                      'category_id',
                      'photo_url',
                      'created_date',
                      'is_private',
                      'rating',
                      'views',
                      'user_id'))
                      })
