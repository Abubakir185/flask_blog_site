from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import InputRequired, Length, Email, EqualTo, DataRequired
from models import Category

class RegisterForm(FlaskForm):
    username = StringField('Foydalanuvchi nomi', validators=[InputRequired(), Length(min=3, max=50)])
    fullname = StringField('Foydalanuvchi toliq ismi', validators=[InputRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Parol', validators=[InputRequired(), Length(min=6)])
    confirm = PasswordField('Parolni tasdiqlang', validators=[EqualTo('password')])
    submit = SubmitField("Ro'yxatdan o'tish")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Parol', validators=[InputRequired()])
    submit = SubmitField('Kirish')


class PostForm(FlaskForm):
    title = StringField('Sarlavha', validators=[InputRequired(), Length(min=3, max=100)])
    content = TextAreaField('Blogingiz', validators=[InputRequired(), Length(min=10)])
    categories = SelectMultipleField('Kategoriya', coerce=int)
    submit = SubmitField("Yaratish")

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.categories.choices = [(c.id, c.name) for c in Category.query.all()]


class CommentForm(FlaskForm):
    text = StringField('Kammentingiz', validators=[InputRequired(), Length(min=1)])
    submit = SubmitField("Yuborih")

# class CategoryForm(FlaskForm):
#     name = StringField('Kategoriya nomi', validators=[DataRequired()])
#     submit = SubmitField("Qo'shish")