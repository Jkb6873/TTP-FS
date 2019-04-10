import os
import bcrypt
import hashlib
import datetime
import jwt
import requests


from flask import Flask, request, session, jsonify
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, or_, func, and_
from sqlalchemy import update, insert, exists
from decimal import Decimal

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
APP_SECRET = os.environ.get("APP_SECRET")
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
IEX_PREFIX = os.environ.get("IEX_PREFIX")

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

class Transaction(db.Model):
    def __init__(self, user_id, symbol, count, cost, type):
        self.user_id = user_id
        self.symbol = symbol
        self.count = count
        self.cost = cost
        self.type = type
        self.purchase_date = datetime.datetime.now()

    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=False, nullable=False)
    purchase_date = db.Column(db.DateTime, unique=False, nullable=False)
    symbol = db.Column(db.String(5), unique=False, nullable=False)
    cost = db.Column(db.Numeric(precision=2, asdecimal=True), unique=False, nullable=False)
    count = db.Column(db.Integer, unique=False, nullable=False)
    type = db.Column(db.Enum(*("buy", "sell"), name="txn_type"), nullable=False)

# google_blueprint = make_google_blueprint(
#     client_id=GOOGLE_CLIENT_ID,
#     client_secret=GOOGLE_CLIENT_SECRET,
#     scope=['https://www.googleapis.com/auth/userinfo.email',
#           'https://www.googleapis.com/auth/userinfo.profile'],
#     # Indicates whether the app can refresh access tokens when the user is not present at the browser
#     # "Enable offline access so that you can refresh an access token without re-prompting the user for permission. Recommended for web server apps."
#     offline=True,
#     #Uses the offline access to automatically refresh the authorization session
#     reprompt_consent=True
# )
# application.register_blueprint(google_blueprint, url_prefix="/login")

def validate_login(func):
    def wrapper(*args, **kwargs):
        #if user has a valid login cookie, let them log in
        token = session.get('site_token', None)
        id = check_token(token)
        if token and id:
            return func(*args, **dict(kwargs, userId=id))
        #otherwise, check if google authorized
        # elif not google.authorized:
        #     return redirect(url_for("google.login"))
        # try:
        #     resp = google.get("/oauth2/v2/userinfo")
        #     assert resp.ok, resp.text
        # except (AssertionError, InvalidClientIdError, InvalidGrantError):
        #     return redirect(url_for("google.login"))
        return jsonify({"error":"You must be logged in to preform this action"}),403
    wrapper.func_name = func.func_name
    return wrapper


def issue_token(name, email, id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=30),
        'iat': datetime.datetime.utcnow(),
        'sub': id,
        'name': name,
        'email': email
    }
    session['site_token'] = jwt.encode(
        payload,
        APP_SECRET,
        algorithm='HS256'
    )

def check_token(token):
    try:
        payload = jwt.decode(token, APP_SECRET)
    except (jwt.ExpiredSignatureError):
        return False
    return payload['sub']

@application.route('/buy', methods=['POST'])
@validate_login
def buy(userId):
    symbol = request.args.get('symbol', '')

    try:
        count = int(request.args.get('count', 1))
        if count < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error":"Not a valid count"}), 400

    r = requests.get(IEX_PREFIX + symbol)

    if not(r.ok and len(r.json()) == 1):
        return jsonify({"error":"Not a valid symbol"}),400

    cost = Decimal(r.json()[0]['price'] * count)

    user = db.session.query(User).filter(User.id == userId).first()
    if user.funds < cost:
        return jsonify({"error": "Insufficient Funds"}), 400

    setattr(user, 'funds', user.funds - cost)
    txn = Transaction(userId, symbol, count, cost, 'buy')
    db.session.add(txn)
    db.session.commit()
    return jsonify({"success": True, "balance": float(user.funds)}), 200

@application.route('/sell', methods=['POST'])
@validate_login
def sell(userId):
    symbol = request.args.get('symbol', '')

    try:
        count = int(request.args.get('count', 1))
        if count < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error":"Not a valid count"}), 400

    r = requests.get(IEX_PREFIX + symbol)

    if not(r.ok and len(r.json()) == 1):
        return jsonify({"error":"Not a valid symbol"}),400

    cost = Decimal(r.json()[0]['price'] * count)
    user = db.session.query(User).filter(User.id == userId).first()

    all_transactions = dict(db.session.query(
        Transaction.type,
        func.sum(Transaction.count)
    ).filter(
        Transaction.user_id == userId and Transaction.symbol == symbol
    ).group_by(
        Transaction.type
    ).all())

    total_stock = all_transactions['buy'] - all_transactions['sell']
    if total_stock < count:
        return jsonify({"error":"You do not have this much stock"}), 400

    setattr(user, 'funds', user.funds + cost)
    txn = Transaction(userId, symbol, count, cost, 'sell')
    db.session.add(txn)
    db.session.commit()
    return jsonify({"success": True, "balance": float(user.funds)}), 200

@application.route('/login', methods=['POST'])
def login():
    email = request.args.get('email', '')
    password = request.args.get('password', '').encode('utf-8')
    user = db.session.query(User.name, User.email, User.id, User.key).filter(User.email == email).first()

    if user and bcrypt.checkpw(password, user.key.encode('utf-8')):
        issue_token(user.name, user.email, user.id)
        return jsonify({"success":True}),200
    return jsonify({"error":"No user exists for this email/password"}),403

@application.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success":True}),200

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
            return jsonify({"error":"{} is of incorrect format".format(param)}), 400

    # error in the case that the email is taken
    email_taken = db.session.query(exists().where(User.email == params['Email'])).scalar()
    if email_taken:
        return jsonify({"error":"This email is already taken"}),400

    newUser = User(name=params['Name'], email=params['Email'], password=params['Password'])
    db.session.add(newUser)
    db.session.flush()
    db.session.refresh(newUser)
    db.session.commit()
    issue_token(newUser.name, newUser.email, newUser.id)
    return jsonify({"success":True}),200
