# -*- coding: utf-8 -*-
from flask import Flask, request, make_response, render_template, redirect, abort, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from flask import jsonify
import requests
import random
import os

from data import db_session
from data.User import User
from data.Article import Article
from data.Category import Category
from data.Vote import Vote

from forms.article import ArticleForm
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.user_edit import UserEditForm
from forms.user_edit_password import UserEditPasswordForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top_security'

login_manager = LoginManager()
login_manager.init_app(app)


article_defoult_image = 'img/articles/article_defoult.jpg'
user_defoult_image = 'img/users/user_defoult.jpg'
article_category_list = ['Наука', 'Спорт', 'Игры', 'Программирование', 'Фильмы', 'Сериалы', 'Аниме', 'Обзоры', 'Другое']
article_sort_list = ['Дате', 'Названию', 'Просмотрам', 'Рейтингу']


def delete_file(url):
    try:
        if url != article_defoult_image and url != user_defoult_image:
            os.remove(url_for('static', filename=url)[1:])
    except:
        pass


def create_img_url(id, type):
    random_int = random.randrange(100000, 999999)
    if type == 'article':
        return f'img/articles/article_{id}_{random_int}.jpg'
    elif type == 'user':
        return f'img/users/user_{id}_{random_int}.jpg'


def count_votes(article_id):
    session = db_session.create_session()
    votes = session.query(Vote).filter(Vote.article_id == article_id).all()
    count = 0
    for vote in votes:
        if vote.vote == 'up':
            count += 1
        elif vote.vote == 'down':
            count -= 1
    return count


def valid_password(password):
    message = ''
    flag = True
    if len(password) < 8:
        message = 'Пароль должен быть больше 8 символов'
        flag = False

    if not any(s.isdigit() for s in password):
        message = 'Пароль не содержит цифр'
        flag = False

    if not any(s.isupper() for s in password):
        message = 'Пароль не содержит заглавных букв'
        flag = False

    if not any(s.islower() for s in password):
        message = 'Пароль не содержит строчных букв'
        flag = False

    return [flag, message]


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('index.html', title='Главная', url='/')


@app.route('/about')
def about():
    return render_template('about.html', title='О проекте', url='/about')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        is_valid_password, message = valid_password(form.password.data)
        if not is_valid_password:
            return render_template('register.html', title='Регистрация', form=form, message=message)
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            photo_url=user_defoult_image)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", title='Авторизация', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


#######################################################################################################################
# Articles


# получение значений из формы сортировки
def get_sort_data():
    category_id = int(request.form.get('category_id'))
    sort_by = int(request.form.get('sort_by'))
    reverse = int(request.form.get('reverse'))
    search = str(request.form.get('search'))
    return [category_id, sort_by, reverse, search]


def article_sort():
    category_id, sort_by, reverse, search = get_sort_data()
    session = db_session.create_session()

    # сортировка по значениям из модели
    if sort_by == 0:
        articles = session.query(Article).order_by(Article.created_date).all()
    elif sort_by == 1:
        articles = session.query(Article).order_by(Article.title).all()
    elif sort_by == 2:
        articles = session.query(Article).order_by(Article.views).all()
    elif sort_by == 3:
        articles = session.query(Article).order_by(Article.rating).all()

    # фильтр по категориям статей
    if category_id != 0 and category_id != 10:
        articles = list(filter(lambda x: x.category_id == category_id, articles))

    # фильтр по личным статьям
    if category_id == 10:
        articles = list(filter(lambda x: x.is_private == True, articles))

    # задом наперед
    if reverse == 1:
        articles.reverse()

    # поиск по слову/ам
    if len(search) != 0:
        search = search.lower()
        articles = list(filter(lambda x: ((search in x.title.lower()) or
                                          (search in x.description.lower()) or
                                          (search in x.content.lower())), articles))
    return articles


@app.route('/articles', methods=['GET', 'POST'])
def article_list():
    form = {}
    session = db_session.create_session()

    form['articles'] = session.query(Article).filter(Article.is_private == False).all()
    form['categories'] = ['Все'] + article_category_list
    form['sort_list'] = article_sort_list
    form['selected'] = [0, 0, 0, '']

    if request.method == 'POST':
        form['articles'] = article_sort()
        form['articles'] = list(filter(lambda x: x.is_private == False, form['articles']))
        form['selected'] = get_sort_data()

    return render_template('article_list.html', title='Статьи', form=form, url='/articles')


@app.route('/articles/show/<int:article_id>')
def article_show(article_id):
    form = {}
    session = db_session.create_session()
    article = session.query(Article).get(article_id)
    article.rating = count_votes(article.id)
    session.commit()
    if article:
        if (article.is_private is False) or (article.user == current_user):
            title = article.title
            article.views += 1
            session.commit()
            form['category'] = session.query(Category).get(article.category_id)
            if current_user.is_authenticated:
                form['current_user_vote'] = session.query(Vote).filter(Vote.article_id == article.id, Vote.user_id == current_user.id).first()
                if form['current_user_vote']:
                    form['current_user_vote'] = form['current_user_vote'].vote
                else:
                    form['current_user_vote'] = 'un'
            return render_template('article_show.html', title=title, article=article, form=form)
        else:
            abort(403)
    else:
        abort(404)


@app.route('/articles/vote/<int:article_id>/<string:vote>')
@login_required
def article_vote(article_id, vote):
    session = db_session.create_session()
    article = session.query(Article).get(article_id)
    if article:
        if (article.is_private is False) or (article.user == current_user):
            exist_vote = session.query(Vote).filter(Vote.article_id == article.id, Vote.user_id == current_user.id).first()
            if exist_vote:
                if exist_vote.vote == vote:
                    exist_vote.vote = 'un'
                else:
                    exist_vote.vote = vote
            else:
                vote = Vote(user_id=current_user.id,
                            article_id=article.id,
                            vote=vote)
                session.add(vote)
            session.commit()
            article.rating = count_votes(article.id)
            session.commit()
            return redirect(f'/articles/show/{ article.id }')
        else:
            abort(403)
    else:
        abort(404)


@app.route('/articles/create', methods=['GET', 'POST'])
@login_required
def article_create():
    form = ArticleForm()
    session = db_session.create_session()
    user = session.query(User).get(current_user.id)
    form.category_id.choices = [[category.id, category.name] for category in session.query(Category).all()]

    if form.validate_on_submit():
        file = request.files['file']
        if file:
            id = len(session.query(Article).all()) + 1
            photo_url = create_img_url(id, 'article')
            path = url_for('static', filename=photo_url)[1:]
            file.save(path)
        else:
            photo_url = article_defoult_image

        article = Article(title=form.title.data,
                          description=form.description.data,
                          content=form.content.data,
                          category_id=form.category_id.data,
                          photo_url=photo_url,
                          is_private=form.is_private.data)

        user.articles.append(article)
        session.merge(user)
        session.commit()
        return redirect(f'/user/show/{ current_user.id }')
    return render_template('article_create.html', title='Создание статьи', form=form)


@app.route('/articles/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def article_edit(article_id):
    form = ArticleForm()
    session = db_session.create_session()
    form.category_id.choices = [[category.id, category.name] for category in session.query(Category).all()]
    article = session.query(Article).get(article_id)
    if request.method == "GET":
        if article:
            if current_user == article.user:
                form.title.data = article.title
                form.description.data = article.description
                form.content.data = article.content
                form.category_id.data = article.category_id
                form.is_private.data = article.is_private
            else:
                abort(403)
        else:
            abort(404)
    if form.validate_on_submit():
        if article:
            file = request.files['file']
            if file:
                delete_file(article.photo_url)
                id = article.id
                photo_url = create_img_url(id, 'article')
                path = url_for('static', filename=photo_url)[1:]
                file.save(path)
            else:
                photo_url = article.photo_url

            if current_user == article.user:
                article.title = form.title.data
                article.description = form.description.data
                article.content = form.content.data
                article.category_id = form.category_id.data
                article.is_private = form.is_private.data
                article.photo_url = photo_url
                session.commit()
                return redirect(f'/user/show/{ current_user.id }')
            else:
                abort(403)
        else:
            abort(404)
    return render_template('article_edit.html', title='Редактирование статьи', form=form, article=article)


@app.route('/articles/delete/<int:article_id>')
@login_required
def article_delete(article_id):
    session = db_session.create_session()
    article = session.query(Article).get(article_id)
    if article:
        if current_user == article.user:
            delete_file(article.photo_url)
            session.delete(article)
            session.commit()
        else:
            abort(403)
    else:
        abort(404)
    return redirect(f'/user/show/{ current_user.id }')


@app.route('/articles/delete/image/<int:article_id>')
@login_required
def article_delete_image(article_id):
    session = db_session.create_session()
    article = session.query(Article).get(article_id)
    if article:
        if current_user == article.user:
            delete_file(article.photo_url)
            article.photo_url = article_defoult_image
            session.commit()
        else:
            abort(403)
    else:
        abort(404)
    return redirect(f'/user/show/{ current_user.id }')


#######################################################################################################################
# Users


@app.route('/users')
@login_required
def user_list():
    session = db_session.create_session()
    users = session.query(User)
    return render_template('user_list.html', title='Все пользователи', form=users, url='/users')


@app.route('/user/show/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_show(user_id):
    form = {}
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    title = f'{user.surname} {user.name}'

    if user:
        form['articles'] = session.query(Article).filter(Article.user == user).all()
        form['categories'] = ['Все'] + article_category_list + ['Личное']
        form['sort_list'] = article_sort_list
        form['selected'] = [0, 0, 0, '']

        if request.method == 'POST':
            form['articles'] = article_sort()
            form['articles'] = list(filter(lambda x: x.user == user, form['articles']))
            form['selected'] = get_sort_data()

        if user == current_user:
            pass
        else:
            form['articles'] = list(filter(lambda x: x.is_private == False, form['articles']))
        return render_template('user_show.html', title=title, user=user, form=form)
    else:
        abort(404)


@app.route('/user/edit', methods=['GET', 'POST'])
@login_required
def user_edit():
    form = UserEditForm()
    session = db_session.create_session()
    user = session.query(User).get(current_user.id)
    if request.method == "GET":
        if user:
            form.email.data = user.email
            form.name.data = user.name
            form.surname.data = user.surname
            form.info.data = user.info
            form.age.data = user.age
            form.city_from.data = user.city_from
        else:
            abort(404)
    if form.validate_on_submit():
        if user:
            file = request.files['file']
            if file:
                delete_file(user.photo_url)
                id = user.id
                photo_url = create_img_url(id, 'user')
                path = url_for('static', filename=photo_url)[1:]
                file.save(path)
            else:
                photo_url = user.photo_url
            if session.query(User).filter(User.email == form.email.data, form.email.data != user.email).first():
                return render_template('user_edit.html', title='Редактирование профиля', form=form,
                                       message="Пользователь с таким email уже есть")
            user.email = form.email.data
            user.name = form.name.data
            user.surname = form.surname.data
            user.info = form.info.data
            user.age = form.age.data
            user.city_from = form.city_from.data
            user.photo_url = photo_url
            session.commit()
            return redirect(f'/user/show/{ current_user.id }')
        else:
            abort(404)
    return render_template('user_edit.html', title='Редактирование профиля', form=form)


@app.route('/user/edit/password', methods=['GET', 'POST'])
@login_required
def user_edit_password():
    form = UserEditPasswordForm()
    session = db_session.create_session()
    user = session.query(User).get(current_user.id)
    if form.validate_on_submit():
        if user:
            if form.password.data != form.password_again.data:
                return render_template('user_edit_password.html', title='Смена пароля', form=form, message="Пароли не совпадают")
            is_valid_password, message = valid_password(form.password.data)
            if not is_valid_password:
                return render_template('user_edit_password.html', title='Регистрация', form=form, message=message)
            user.set_password(form.password.data)
            session.commit()
            return redirect(f'/user/show/{ current_user.id }')
        else:
            abort(404)
    return render_template('user_edit_password.html', title='Смена пароля', form=form)


@app.route('/user/delete', methods=['GET', 'POST'])
@login_required
def user_delete():
    session = db_session.create_session()
    user = session.query(User).get(current_user.id)
    articles = session.query(Article).filter(Article.user == user)
    votes = session.query(Vote).filter(Vote.user_id == user.id)
    for item in articles:
        delete_file(item.photo_url)
        session.delete(item)
    for item in votes:
        session.delete(item)
    delete_file(current_user.photo_url)
    session.delete(user)
    session.commit()
    return redirect('/')


@app.route('/user/delete/image', methods=['GET', 'POST'])
@login_required
def user_delete_image():
    session = db_session.create_session()
    user = session.query(User).get(current_user.id)
    delete_file(user.photo_url)
    user.photo_url = user_defoult_image
    session.commit()
    return redirect(f'/user/show/{ current_user.id }')


########################################################################################################################


@app.errorhandler(401)
def error(error):
    message = 'Необходима регистрация'
    return render_template('error.html', title='Ошибочка 401', message=message)


@app.errorhandler(403)
def error(error):
    message = 'Доступ ограничен'
    return render_template('error.html', title='Ошибочка 403', message=message)


@app.errorhandler(404)
def not_found(error):
    message = 'Страница не найдена'
    return render_template('error.html', title='Ошибочка 404', message=message)


# функция добавления списка категорий в базу данных
def add_categories():
    session = db_session.create_session()
    categories = article_category_list
    for category in categories:
        category = Category(name=category)
        session.add(category)
    session.commit()


# добавление категорий в новую базу данных
def check_db():
    if not os.path.exists("db/data.db"):
        db_session.global_init("db/data.db")
        add_categories()
    else:
        db_session.global_init("db/data.db")


def main():
    check_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
