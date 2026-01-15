from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, FileField, DecimalField, TextAreaField
from wtforms.fields.choices import RadioField, SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, length, equal_to

#<input type="text">
class RegisterForm(FlaskForm):
    username = StringField("enter your username", validators=[DataRequired()])
    password  = PasswordField("enter your password", validators=[DataRequired(), length(min=8, max=16)])
    repeat_password = PasswordField("repeat your password", validators=[DataRequired(), equal_to("password")])


    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("enter your username")
    password  = PasswordField("enter your password")

    login = SubmitField("Login")


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    artist = StringField("Artist Name", validators=[DataRequired()])
    price = DecimalField("Price (GEL)", validators=[DataRequired()])
    product_img = FileField("Upload a photo of your product", [ FileAllowed(["jpg", "png", "jpeg", "jfif"])] )

    submit = SubmitField("Add Product")

class CommentForm(FlaskForm):
    text = TextAreaField("Leave a comment", validators=[DataRequired()])
    submit = SubmitField("Post Comment")

class ContactForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired()])
    subject = SelectField("Subject", choices=[
        ('', 'Choose a topic...'),
        ('Purchase Inquiry', 'Purchase Inquiry'),
        ('Artist Collaboration', 'Artist Collaboration'),
        ('General Question', 'General Question'),
        ('Technical Support', 'Technical Support')
    ], validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send Message")


class AskForm(FlaskForm):
    question = StringField("Ask AI", validators=[
        DataRequired(),
        length(max=200, message="Maximum 200 characters allowed.")
    ])
    submit = SubmitField("Send")  