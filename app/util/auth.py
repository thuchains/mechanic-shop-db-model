from jose import jwt 
import jose
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify

SECRET_KEY = '__secret_key__'

def encode_token(mechanic_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=0, minutes=20),
        'iat': datetime.now(timezone.utc),
        'sub': str(mechanic_id)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorations(*args, **kwargs):

        token = None

        if 'Authroization' in request.headers:
            token = request.headers['Authorization'].split()[1]

        if not token:
            return jsonify({"Error": "Token missing from authorization headers"}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms='HS256')
            print(data)
            request.mechanic_id = int(data['sub'])

        except jose.exceptions.ExpiredSignatureError:
            return jsonify({"message": "token is expired"}), 403
        except jose.exceptions.JWTError:
            return jsonify({"message": "invalid token"}), 403
        
        return f(*args, **kwargs) 
    
    return decorations


