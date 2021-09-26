from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class TweetForm(FlaskForm):
    text = StringField("Story Title", validators=[InputRequired()])
    url = StringField("url")
    author = StringField("author")
