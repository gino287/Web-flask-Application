from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField,PasswordField,IntegerField,SelectField
from wtforms.validators import DataRequired, URL, Optional, Length, Email, EqualTo, ValidationError,NumberRange
from .models import User

#文章格式
class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[Optional(), URL()])
    category = SelectField('Category', choices=[('tech', 'Tech'), ('travel', 'Travel'), ('food', 'Food'), ('other', 'Other')], validators=[Optional()])
    submit = SubmitField('Submit')

#使用者資訊
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')

#登入表單資料
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

#評論資料
class CommentForm(FlaskForm):
    content = TextAreaField('Leave a Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Comment')

#評分資料
class RatingForm(FlaskForm):
    score = IntegerField('Rate (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Submit Rating')
