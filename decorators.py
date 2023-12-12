# decorators.py

from flask import jsonify, request
import jwt
from functools import wraps
from inspect import getfullargspec
from datetime import datetime, timedelta
from flask import current_app as app

# Function to verify the JWT token
def token_required(f):
    @wraps(f, assigned=('__module__', '__name__', '__qualname__', '__doc__', '__annotations__'))
    def decorated(*args, **kwargs):
        try:
            # Check if the 'Authorization' header is present
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'error': 'Authorization header is missing'}), 401

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return f(data, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    return decorated
