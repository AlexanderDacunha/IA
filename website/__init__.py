from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Making the database object.
db = SQLAlchemy()

# Assigning a global variable to track the name of my database.
DB_NAME = "users.db"

# Isolating the app creation into a function.
def create_app():
    # Making the app object and setting the config.
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Dr. Hammond Rocks'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    #Initializing the database.
    db.init_app(app)    

    # Importing the different routes that my website will have as flask Blueprint objects.
    from .views import views
    from .auth import auth
    from .problems import problems

    # Unpacking the Blueprint objects and making them usable in my website.
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(problems, url_prefix="/problemsets/", name="problemsets_blueprint")

    # Importing my database models
    from .models import User, Classroom, Problems, Progress, TestCases, ProblemCategory

    # Importing my class that modifies Flask_Admin's default views.
    from .models import MyViews

    admin = Admin(app, name="Admin Panel", template_mode="bootstrap3")
    admin.add_view(MyViews(User, db.session))
    admin.add_view(MyViews(Classroom, db.session))
    admin.add_view(MyViews(ProblemCategory, db.session))
    admin.add_view(MyViews(Problems, db.session))
    admin.add_view(MyViews(Progress, db.session))
    admin.add_view(MyViews(TestCases, db.session))
    

    with app.app_context():
       create_database(app)

    # Initialize my own variable that stores the class LoginManager which I imported from Flask_Login to use methods on my variable.
    login_manager = LoginManager()

    # Setting the default page view that users should use to login to my website.
    login_manager.login_view = 'auth.login'

    # Initializing the variable to work in my app
    login_manager.init_app(app)

    # Decorator that takes the user_loader function from Flask_Login and lets me define it, making it find a specific user based on their
    # unique id value and return that specific user as a User object.
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Returning the app to be run from a different file
    return app

# Creates the file for my database if a database does not already exist.
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all()
        print('Created Database')