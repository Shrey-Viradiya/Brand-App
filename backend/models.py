from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from backend import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"UserID('{self.id}') Email('{self.email}')"

class RequestID(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def get_request_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'request_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_request_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['request_id']
        except:
            return None
        return RequestID.query.get(user_id)

    def __repr__(self):
        return f"RequestID('{self.email}')"

class Month(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    month = db.Column(db.String(120),unique = True,nullable = False)
    primary_subject = db.Column(db.String(120),unique = True, nullable =False)
    comment = db.Column(db.text,nullable = False)
    questions = db.relationship('Question',backref = 'month',lazy = True)

    def __repr__(self):
        return f"Month: {self.month} with primary subject: {self.primary_subject} \n\n Comments: {self.comment})"

class Question(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    question = db.Column(db.text,nullable = False)
    options = db.Column(db.String,nullable = False)
    answer = db.Column(db.String, nullable = False)
