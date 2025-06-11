import os
import jwt
from functools import wraps
from flask import jsonify, request
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
load_dotenv()


def check_api(data: dict, required_fields: list, nested_fields: dict = None) -> tuple:
    """
    Validate presence of required top-level and nested fields in API request JSON.
    Returns (is_valid, error_response)
    """
    if not data:
        return False, ["Missing Data", "No data was received."], 400

    # Check top-level fields
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, ["Missing Field", f"'{field}' is required but not provided."], 400

    # Check nested fields (like user_data)
    if nested_fields:
        for parent_key, fields in nested_fields.items():
            nested = data.get(parent_key)
            if not isinstance(nested, dict):
                return False, ["Malformed Data", f"'{parent_key}' must be a dictionary."], 400
            for field in fields:
                if field not in nested or nested[field] is None:
                    return False, [f"Missing Nested Field", f"'{field}' is required in '{parent_key}'"], 400

    return True, ["None", "None"], None

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=7)  # token valid for 7 days
    }
    return jwt.encode(payload, os.getenv("FLASK_APP_SECRET_KEY"), algorithm='HS256')

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')

        if not auth or not auth.startswith('Bearer '):
            return jsonify({'message': 'Token missing or invalid'}), 401

        token = auth.split(' ')[1]

        try:
            data = jwt.decode(token, os.getenv("FLASK_APP_SECRET_KEY"), algorithms=['HS256'])
            request.user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated

# print(generate_token(1))