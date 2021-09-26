from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm
from sqlalchemy.exc import IntegrityError
from newsapi import NewsApiClient
from flask.json import jsonify

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_demo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
newsapi = NewsApiClient(api_key='3fffbccc1f5e4c2c8d0c75abe4fb295c')


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/tweets', methods=['GET', 'POST'])
def show_tweets():
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    form = TweetForm()
    all_tweets = Tweet.query.order_by(Tweet.timestamp.desc()).all()
    all_articles = newsapi.get_everything(q='tech',
                                      sources='bbc-news,the-verge',
                                      domains='bbc.co.uk,techcrunch.com',
                                      from_param='2021-08-20',
                                      to='2021-09-18',
                                      language='en',
                                      sort_by='relevancy')

    if form.validate_on_submit():
        text = form.text.data
        url = form.url.data
        author = form.author.data
        new_tweet = Tweet(text=text, url=url, author=author, user_id=session['user_id'])
        db.session.add(new_tweet)
        db.session.commit()
        flash('Story Created!', 'success')
        return redirect('/tweets')

    return render_template("tweets.html", form=form, tweets=all_tweets, articles=all_articles["articles"])


@app.route('/tweets/<int:id>', methods=["POST"])
def delete_tweet(id):
    """Delete tweet"""
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/login')
    tweet = Tweet.query.get_or_404(id)
    if tweet.user_id == session['user_id']:
        db.session.delete(tweet)
        db.session.commit()
        flash("Tweet deleted!", "info")
        return redirect('/tweets')
    flash("You don't have permission to do that!", "danger")
    return redirect('/tweets')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect('/tweets')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['user_id'] = user.id
            return redirect('/tweets')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('user_id')
    flash("Goodbye!", "info")
    return redirect('/')


