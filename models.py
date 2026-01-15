from ext import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 

class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    img = db.Column(db.String(), nullable=False, default="default_img.jpg")
    artist = db.Column(db.String(), nullable=False, default="Unknown Artist")

class Comment(db.Model):


    __tablename__ = "comments"
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(), nullable=False)
    product_id = db.Column(db.Integer(), db.ForeignKey("products.id"))
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="comments")
    comment_likes = db.relationship("CommentLike", backref="comment", cascade="all, delete-orphan")

class Wishlist(db.Model):  
    

    __tablename__ = "wishlist"
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer(), db.ForeignKey("products.id"), nullable=False)
    

    user = db.relationship("User", backref="wishlist_items")
    product = db.relationship("Product", backref="wishlisted_by")


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    role = db.Column(db.String())

    comment_likes = db.relationship("CommentLike", backref="user", cascade="all, delete-orphan")

    def __init__(self, username, password, role="Guest"):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    subject = db.Column(db.String(), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean(), default=False)

class CommentLike(db.Model):
    __tablename__ = "comment_likes"
    
    id = db.Column(db.Integer(), primary_key=True)
    comment_id = db.Column(db.Integer(), db.ForeignKey("comments.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('comment_id', 'user_id', name='unique_comment_like'),)