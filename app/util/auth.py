from jose import jwt 
import jose
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify

SECRET_KEY = '__secret_key__'

def encode_token(mechanic_id: int):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(minutes=20),
        'iat': datetime.now(timezone.utc),
        'sub': str(mechanic_id)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
   
    return token


def token_required(f):
    @wraps(f)
    def decorations(*args, **kwargs):

        token = None

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401
        token = auth.split(" ", 1)[1]

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            print(data)
            request.mechanic_id = int(data['sub'])

        except jose.exceptions.ExpiredSignatureError:
            return jsonify({"message": "token is expired"}), 401
        except jose.exceptions.JWTError:
            return jsonify({"message": "invalid token"}), 401
        
        return f(*args, **kwargs) 
    
    return decorations


