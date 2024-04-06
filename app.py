from flask import Flask, request, jsonify, render_template, redirect, abort, request
from os import environ
from data import db_session
from data.countries import Countries
from data.users import User
from data.news import News
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.news import NewsForm
from forms.profile_edit_form import ProfileEditForm

secret_key = environ.get('RANDOM_SECRET')
url = 'yandexlyceum_secret_key'
# url = environ.get('POSTGRES_CONN')
app = Flask(__name__)
app.config['SECRET_KEY'] = url

login_manager = LoginManager()
login_manager.init_app(app)

@app.route("/api/me")
@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route('/api/ping', methods=['GET'])
def send():
    return jsonify({"status": "ok"}), 200



@app.route('/api/countries', methods=['GET'])
def get_countries():
    db_sess = db_session.create_session()
    countries = db_sess.query(Countries).filter(Countries.name)
    contry_list = [{'name': country.name, 'alpha2': country.alpha2, 'alpha3': country.alpha3, 'region':
        country.region} for country in countries]
    return jsonify(countries=contry_list)


@app.route('/register',  methods=['GET', 'POST'])
@app.route('/api/auth/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            region=form.region.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/api/auth/sign-in", methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/api/logout")
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/api/posts",  methods=['GET', 'POST'])
@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route("/api/posts/<int:id>", methods=['GET', 'POST'])
@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )

@app.route('/api/news_delete/<int:id>', methods=['GET', 'POST'])
@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/api/me/password', methods=['GET', 'POST'])
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    form = ProfileEditForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            user.name = form.name.data
            user.set_password(form.password.data)
            db_sess.commit()
            return redirect('/')
    else:
        form.username.data = current_user.name

    return render_template('profile_edit.html', title='Изменение профиля', form=form)

def main():
    db_session.global_init('db/social.db')
    app.run()


if __name__ == "__main__":
    main()