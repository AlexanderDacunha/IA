from . import db
from flask import redirect, url_for
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

class User(db.Model , UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(80), nullable=False)

    class_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=True)

    problems = db.relationship('Problems', secondary='user_progress', back_populates='users', lazy='dynamic')
    user_progress = db.relationship('Progress', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    
class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.Integer, unique=True, nullable=False)

    students = db.relationship('User', backref='classroom', lazy=True, cascade="all, delete")

class ProblemCategory(db.Model):
    __tablename__ = 'problem_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    problems = db.relationship('Problems', lazy=True)  

class Problems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problemName = db.Column(db.String(100), nullable=False, unique=True)
    function = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(80), nullable=False)

    users = db.relationship('User', secondary='user_progress', back_populates='problems', lazy='dynamic')
    user_progress = db.relationship('Progress', back_populates='problem', lazy='dynamic')

    category_id = db.Column(db.Integer, db.ForeignKey('problem_categories.id'), nullable=False)
    category = db.relationship('ProblemCategory', backref=db.backref('problem_set', lazy=True), overlaps='problems')  

    test_cases = db.relationship('TestCases', backref='problem', lazy=True, cascade="all, delete")

class Progress(db.Model):
    __tablename__ = "user_progress"

    User_ID = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    Problem_ID = db.Column(db.Integer, db.ForeignKey('problems.id', ondelete="CASCADE"), primary_key=True)

    completed = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='user_progress')
    problem = db.relationship('Problems', back_populates='user_progress')

class TestCases(db.Model):
    __tablename__ = "test_cases"

    id = db.Column(db.Integer, primary_key=True)

    Problem_ID = db.Column(db.Integer, db.ForeignKey('problems.id', ondelete="CASCADE"), nullable=False) 
    
    input_data = db.Column(db.Text, nullable=False) 
    expected_output = db.Column(db.Text, nullable=False)


class MyViews(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role == 'Admin'
        
        return False
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))
    
