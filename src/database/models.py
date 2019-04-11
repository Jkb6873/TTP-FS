import datetime
import bcrypt
from . import db
from decimal import Decimal

class User(db.Model):
    def __init__(self, name, email, password):
        self.key = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(14)
        ).decode('utf-8')
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
