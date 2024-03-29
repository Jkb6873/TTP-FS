import jwt
import datetime
from flask import json, session, jsonify, render_template
from decimal import Decimal
from .config import APP_SECRET
from .database.models import Transaction

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, Transaction):
            output = {
                'symbol': obj.symbol,
                'type': obj.type,
                'cost': obj.cost,
                'count': obj.count,
                'purchase_date': obj.purchase_date
            }
            return output
        return super(CustomEncoder, self).default(obj)

def validate_login(func):
    def wrapper(*args, **kwargs):
        token = session.get('site_token', None)
        id = check_token(token)
        if token and id:
            return func(*args, **dict(kwargs, userId=id))
        return render_template('login.html'), 403
    wrapper.__name__ = func.__name__
    return wrapper

def issue_token(name, email, id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=2),
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
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        return False
    return payload['sub']
