import os
import bcrypt
import hashlib

from flask import Flask, request
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, or_, func, and_
from sqlalchemy import update, insert, exists


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
APP_SECRET = os.environ.get("APP_SECRET")
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

application = Flask(__name__)
application.secret_key = APP_SECRET
application.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(application)

class User(db.Model):
    def __init__(self, name, email, password):
        self.key = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(14)
        )
        self.name = name
        self.email = email
        self.funds = 5000.00

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    key = db.Column(db.String(256), unique=True, nullable=False)
    funds = db.Column(db.Numeric(precision=2, asdecimal=True), unique=False, nullable=False)


google_blueprint = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    scope=['https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile'],
    # Indicates whether the app can refresh access tokens when the user is not present at the browser
    # "Enable offline access so that you can refresh an access token without re-prompting the user for permission. Recommended for web server apps."
    offline=True,
    #Uses the offline access to automatically refresh the authorization session
    reprompt_consent=True
)
application.register_blueprint(google_blueprint, url_prefix="/login")



def validate_login(func):
    def wrapper(*args, **kwargs):
        #if user has a valid login cookie, let them log in

        #otherwise, check if google authorized

        if not google.authorized:
            return redirect(url_for("google.login"))
        try:
            resp = google.get("/oauth2/v2/userinfo")
            assert resp.ok, resp.text
        except (AssertionError, InvalidClientIdError, InvalidGrantError):
            return redirect(url_for("google.login"))
    wrapper.func_name = func.func_name
    return wrapper

@application.route('/register', methods=['POST'])
def register():
    params = {
        'Name': request.args.get('name', ''),
        'Email': request.args.get('email', '').lower(),
        'Password': request.args.get('password', '')
    }
    #error in case the email, name or password is too long or empty
    for param in params:
        if not params[param] or len(params[param]) > 64:
            return "{} is of incorrect format".format(params[param])

    # error in the case that the email is taken
    email_taken = db.session.query(exists().where(User.email == email)).scalar()
    if email_taken:
        return "This email is already taken"

    newUser = User(name=params['Name'], email=params['Email'], password=params['Password'])
    db.session.add(newUser)
    db.session.commit()
