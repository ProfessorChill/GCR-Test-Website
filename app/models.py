from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    password_hash = db.Column(db.String(512))

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    questions = db.Column(db.JSON)

    def __repr__(self):
        return '<Quiz {}>'.format(self.name)


class QuizAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    answers = db.Column(db.JSON)
    score = db.Column(db.Float)
    complete = db.Column(db.Boolean)
    start_dt = db.Column(db.DateTime)
    complete_dt = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<QuizAnswers {} {}>'.format(self.user_id, self.score)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
