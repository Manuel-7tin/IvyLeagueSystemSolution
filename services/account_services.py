import os
import ssl
import jwt
import time
import socket
import smtplib
from pathlib import Path
from dotenv import load_dotenv
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone


# load_dotenv()
print(os.getenv("PY_ENV"))
mail_sender = os.getenv("EMAIL_ADDR")
password = os.getenv("EMAIL_PASSWORD")


def generate_confirmation_token(email, time):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=time)
    }
    return jwt.encode(payload, os.getenv("FLASK_APP_SECRET_KEY"), algorithm='HS256')


def touch_letter(filename: str, name: str, link: str):
    script_path = Path(__file__).resolve()
    file_path = script_path.parent / f"../letters/{filename}"
    file_path = file_path.resolve()

    # Read the original HTML content
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    html_content = html_content.replace("[User's First Name]", name)
    html_content = html_content.replace("[CTA Link]", link)
    return html_content
        # html_content = html_content.replace("Thanks for", "gbas")


def send_signup_message(username: str, user_email: str):
    msg_subject = "Welcome to Ivy League Associates! Please Confirm Your Email"
    token = generate_confirmation_token(user_email, 24)
    link = f"{os.getenv('FRONTEND_URL')}/accounts/confirm-email?token={token}"
    print(link)

    try:
        html_content = touch_letter("signup-message.html", username, link)
    except FileNotFoundError:
        print(f"Error: The signup html file was not found.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

    # 4. Send the letter generated in step 3 to that person's email address.
    message = EmailMessage()
    message["From"] = f"Ivy League Updates <{mail_sender}>"
    message["To"] = user_email
    message["Subject"] = msg_subject
    # attach_image(images, message, image_cid)
    # message.set_content(personalized_letter)
    message.add_alternative(html_content, subtype='html')
    message.add_header("Reply-to", "updates@ivyleaguenigeria.com")

    context = ssl.create_default_context()
    breaks = 0
    while True:
        try:
            with smtplib.SMTP_SSL(host="smtp.gmail.com", port=465, context=context) as mail:
                mail.login(user=mail_sender, password=password)
                mail.sendmail(from_addr=mail_sender, to_addrs=user_email, msg=message.as_string())
        except smtplib.SMTPConnectError as f:
            print("error as", f)
        except smtplib.SMTPException as e:
            print("Encountered smtp error :", e)
            break
        except socket.gaierror as e:
            print("there is an error:", e)
            breaks += 1
            time.sleep(3)
            if breaks > 4:
                # error404()
                break
        else:
            print("AN email has been sent")
            break


def send_password_reset_message(username: str, user_email: str):
    msg_subject = "Reset Your Ivy League Associates LMS Password"
    token = generate_confirmation_token(user_email, 0.168) # Token expires after 10 minutes
    link = f"{os.getenv('FRONTEND_URL')}/accounts/reset-password?token={token}"
    print(link)

    try:
        html_content = touch_letter("reset-password.html", username, link)
    except FileNotFoundError:
        print(f"Error: The signup html file was not found.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

    # 4. Send the letter generated in step 3 to that person's email address.
    message = EmailMessage()
    message["From"] = f"Ivy League Updates <{mail_sender}>"
    message["To"] = user_email
    message["Subject"] = msg_subject
    message.add_alternative(html_content, subtype='html')
    message.add_header("Reply-to", "updates@ivyleaguenigeria.com")

    context = ssl.create_default_context()
    breaks = 0
    while True:
        try:
            with smtplib.SMTP_SSL(host="smtp.gmail.com", port=465, context=context) as mail:
                mail.login(user=mail_sender, password=password)
                mail.sendmail(from_addr=mail_sender, to_addrs=user_email, msg=message.as_string())
        except smtplib.SMTPConnectError as f:
            print("error as", f)
        except smtplib.SMTPException as e:
            print("Encountered smtp error :", e)
            break
        except socket.gaierror as e:
            print("there is an error:", e)
            breaks += 1
            time.sleep(3)
            if breaks > 4:
                break
        else:
            print("An email has been sent")
            break


def verify_email(token):
    try:
        payload = jwt.decode(token, os.getenv("FLASK_APP_SECRET_KEY"), algorithms=['HS256'])
        email = payload['email']
        # Find user by email and set verified=True
        return "success", email
    except jwt.ExpiredSignatureError:
        return "expired", None
    except jwt.InvalidTokenError:
        return "invalid", None


# send_signup_message("test_user", "opolopothings@gmail.com")
