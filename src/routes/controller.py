import requests
import bcrypt

from decimal import Decimal
from sqlalchemy.sql import func, and_
from sqlalchemy import exists
from flask import request, session, jsonify

from . import api
from ..config import IEX_PREFIX
from ..database import db
from ..utils import validate_login, issue_token, check_token
from ..database.models import Transaction, User

@api.route('/buy', methods=['POST'])
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

@api.route('/sell', methods=['POST'])
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
        and_(Transaction.user_id == userId, Transaction.symbol == symbol)
    ).group_by(
        Transaction.type
    ).all())

    total_stock = all_transactions.get('buy', 0) - all_transactions.get('sell', 0)
    if total_stock < count:
        return jsonify({"error":"You do not have this much stock"}), 400

    setattr(user, 'funds', user.funds + cost)
    txn = Transaction(userId, symbol, count, cost, 'sell')
    db.session.add(txn)
    db.session.commit()
    return jsonify({"success": True, "balance": str(user.funds)}), 200

@api.route('/transactions', methods=['GET'])
@validate_login
def transaction_list(userId):
    all_transactions = db.session.query(Transaction).filter(Transaction.user_id == userId).all()
    return jsonify(all_transactions), 200

@api.route('/login', methods=['POST'])
def login():
    email = request.args.get('email', '')
    password = request.args.get('password', '').encode('utf-8')
    user = db.session.query(User.name, User.email, User.id, User.key).filter(User.email == email).first()

    if user and bcrypt.checkpw(password, user.key.encode('utf-8')):
        issue_token(user.name, user.email, user.id)
        return jsonify({"success":True}),200
    return jsonify({"error":"No user exists for this email/password"}),403

@api.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success":True}),200

@api.route('/register', methods=['POST'])
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
