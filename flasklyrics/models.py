from datetime import datetime
from flasklyrics import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    rhymes = db.relationship('Rhyme', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Rhyme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phrase = db.Column(db.String(100), nullable=False)
    n_one = db.Column(db.Integer, primary_key=False)
    n_two = db.Column(db.Integer, primary_key=False)
    n_three = db.Column(db.Integer, primary_key=False)
    nsyl = db.Column(db.Integer, primary_key=False)
    points = db.Column(db.Integer, primary_key=False, nullable=False, default=0)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Rhyme('{self.phrase}', '{self.date_posted}')"