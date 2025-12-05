import os
import re
import io
import base64
import pandas as pd
from pandas.errors import EmptyDataError, ParserError
from PIL import Image
import secrets, string
from os.path import defpath

import jwt
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from functools import wraps
from flask import jsonify, request
from datetime import datetime, timedelta, timezone

from app.models import Role
from dotenv import load_dotenv


load_dotenv()
s3 = boto3.client('s3',
                  aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
                  aws_secret_access_key=os.getenv("AWS_SECRET_KEY"))

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

# def generate_token(user_id):
#     payload = {
#         'user_id': user_id,
#         'exp': datetime.now(timezone.utc) + timedelta(days=60)  # token valid for 2 months
#     }
#     return jwt.encode(payload, os.getenv("FLASK_APP_SECRET_KEY"), algorithm='HS256')
def generate_token(user_id, user_role, expires_in=3600, access=False):
    if access:
        payload = {
            'exp': datetime.now(timezone.utc) + timedelta(days=90)  # token valid for 2 days
        }
    else:
        payload = {
            'user_id': user_id,
            'role': user_role,
            'exp': datetime.now(timezone.utc) + timedelta(days=7) # token valid for 2 days
        }
    return jwt.encode(payload, os.getenv("FLASK_APP_SECRET_KEY"), algorithm='HS256')

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access = request.headers.get('Access')
        auth = request.headers.get('Authorization')

        if not access or not access.startswith('Enter '):
            return jsonify({'message': 'Access Denied boboyi'}), 401
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

def authenticate_signin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        access = request.headers.get('Access')

        if not access or not access.startswith('Enter '):
            return jsonify({'message': 'Access Denied boboyi'}), 401

        return f(*args, **kwargs)
    return decorated

# def role_required(required_role):
#     def wrapper(fn):
#         @wraps(fn)
#         def decorated(*args, **kwargs):
#             # if not current_user.is_authenticated:
#             #     return {'error': 'Authentication required'}, 401
#             # if not current_user.has_role(required_role):
#             #     return {'error': f'{required_role} role required'}, 403
#             return fn(*args, **kwargs)
#         return decorated
#     return wrapper

def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            token = None

            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                return {'error': 'Authorization header missing or malformed'}, 401

            payload = jwt.decode(token, os.getenv("FLASK_APP_SECRET_KEY"), algorithms=['HS256'])
            if 'error' in payload:
                return {'error': payload['error']}, 401

            user_role = payload.get('role')
            if not Role.has_access(user_role, required_role):
                return {'error': f'{required_role} role required not {user_role}'}, 403

            # Optionally pass user info to the route
            return fn(user_id=payload['user_id']) #, user_role=user_role)
        return decorated
    return wrapper


def store_pfp(pfp, email):
    match = re.match(r"data:image/[^;]+;base64,(.*)", pfp)
    if match:
        base64_data = match.group(1)
        profile_picture = base64.b64decode(base64_data)
    else:
        profile_picture = None

    if profile_picture:
        try:
            image = Image.open(io.BytesIO(profile_picture))
            image_format = image.format.lower()  # 'png', 'jpeg', etc.
            content_type = f"image/{image_format}"

            email_username = email.split('@')[0]
            extension = 'jpg' if image_format == 'jpeg' else image_format
            s3_key = f"profile-pics/{email_username}.{extension}"

            # Upload to S3
            s3.put_object(
                Bucket="lms-mini-storage",
                Key=s3_key,
                Body=profile_picture,
                ContentType=content_type
            )
            pfp_url = f"https://lms-mini-storage.s3.eu-north-1.amazonaws.com/{s3_key}"
            print("Upload successful!")
        except Exception as e:
            print(f"Image processing/upload failed: {e}")
            raise ValueError
    else:
        pfp_url = None
    return pfp_url


def store_file(filename, file):
    bucket_name = 'lms-mini-storage'
    # file_path = r'..\pfp.jpg'
    object_name = filename  # 'profile-pics/pfp1.jpg'  # or just 'file.txt'

    try:
        s3.head_object(Bucket=bucket_name, Key=object_name)
    except ClientError:
        pass
    else:
        return {"error": "File or Filename already exists"}, 500

    try:
        s3.upload_fileobj(file, bucket_name, object_name)
        url = f"https://lms-mini-storage.s3.eu-north-1.amazonaws.com/{filename}"
    except NoCredentialsError:
        return {"error": "AWS credentials not configured"}, 500
    except Exception as e:
        return {"error": str(e)}, 500
    else:
        return {"success": "Upload complete."}, 200, url

    # print("Upload complete.")


def download_file(filename):
    bucket_name = 'lms-mini-storage'
    file_stream = io.BytesIO()
    s3.download_fileobj(bucket_name, filename, file_stream)
    file_stream.seek(0)
    return file_stream

# def send_file():
#     bucket_name = 'lms-mini-storage'
#     file_path = r'..\pfp.jpg'
#     object_name = 'profile-pics/pfp1.jpg'  # or just 'file.txt'
#
#     s3.upload_file(file_path, bucket_name, object_name)
#
#     print("Upload complete.")

def save_file():
    bucket_name = 'lms-mini-storage'
    object_name = "profile-pics/pfp1.jpg"
    download_path = r"..\pfp\pro1.jpg"

    s3.download_file(bucket_name, object_name, download_path)

    print("Download complete.")

def list_em():
    response = s3.list_objects_v2(Bucket='your-bucket-name')

    for obj in response.get('Contents', []):
        print(obj['Key'])

def validate_questions(excel_file, paper, diet):
    try:
        df = pd.read_excel(excel_file, header=None)
        mapping = {k.lower(): v for k, v in zip(df[0], df[1])}
        print(mapping)
        if mapping["paper"].lower() != paper.lower():
            return False, "Wrong paper!"
        elif mapping["diet name"].lower() != diet.lower():
            return False, "Wrong diet!"

        content = pd.read_excel(excel_file, header=5)
        que_num = content.Question.notna().sum()
        ans_len = []
        ans_num = content.Answer.notna().sum()

        anss = [col for col in content.columns if len(col) == 1]
        for i in anss:
            ans_len.append(content[i].notna().sum())
        if len(set(ans_len)) > 1 or que_num != ans_num != ans_len[0]:
            return False, "Questions and Answers number do not match!"
        # content["No"] = range(1, que_num + 1)
        if not pd.api.types.is_numeric_dtype(content.No):
            return False, "The 'No' column contains non-numeric values."
        expected = list(range(1, que_num + 1))
        if list(content.No) != expected:
            return False, f"The 'No' column must be exactly 1 to {que_num} in order."

        for i in content.Answer:
            if i.lower() not in [a.lower() for a in anss]:
                return False, "Invalid 'correct option'!"
    except ParserError:
        return False, "File is not a xlsx!"
    except EmptyDataError:
        return False, "File is empty!"
    except AttributeError:
        return False, "Wrong header detail!"
    except ZeroDivisionError:
        return False, "Unknown error while reading xlsx!"
    else:
        return True, "Successful"

def generate_code():
    codes = set()
    gen = lambda: (lambda c: codes.add(c) or c)(
        c := ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))) if (c := ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10))) not in codes else gen()
    return gen()


def read_mcq(file, need):
    response = {}
    try:
        content = pd.read_excel("tr.xlsx", header=5)
        if need == "que":
            for entry in content.iterrows():
                n = entry[0]+1
                response[n] = entry[1].to_dict()
        elif need == "ans":
            for entry in content.iterrows():
                response[entry[1].No] = entry[1].Answer
        else:
            raise Exception
    except:
        return {}
    else:
        return response
# send_file()
# print(generate_token(1, "super_admin"))