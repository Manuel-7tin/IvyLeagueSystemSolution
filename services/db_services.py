import re
import io
import uuid
# import base64
import requests
import sqlalchemy
import pandas as pd
# from PIL import Image
from pprint import pprint

# from run import app
from app.models import db
from config import Config
from flask import jsonify, copy_current_request_context
from functools import wraps
from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload
from app.errors import UserNotFoundError
from sqlalchemy.exc import SQLAlchemyError
from requests.exceptions import ConnectionError
from services.other_services import store_pfp
from services.account_services import send_receipt
from app.models import Attempt, Student, Paper, Action, Signee, Payment, Sponsored, Scholarship, Enrollment, Diet
from app.models import StaffActivity, DirectoryInstance, GatewayTest, McqHistory


def encode_year(year: int, a=117, b=53, m=10000):
    return (a * year + b) % m

def decode_year(code: int, a=117, b=53, m=10000):
    a_inv = pow(a, -1, m)  # modular inverse
    return ((code - b) * a_inv) % m

def encode_serial(serial: int, a=211, b=79, m=10000):
    return (a * serial + b) % m

def decode_serial(code: int, a=211, b=79, m=10000):
    a_inv = pow(a, -1, m)
    return ((code - b) * a_inv) % m


def is_valid_password(password: str) -> tuple:
    """
    Checks if the password is at least 8 characters long and contains
    at least one letter, one number, and one special character.
    """
    if len(password) < 8:
        return False, "LEN: Too short"
    elif not re.search(r"[A-Za-z]", password):
        return False, "ALPH: No letter"
    elif not re.search(r"[0-9]", password):
        return False, "NUM: No number"
    elif not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "CHAR: No special character"
    return True, "Verified"


def log_attempt(data: dict, purpose: str, ref: str):
    user_data = data["user_data"]
    new_attempt = Attempt(
        email=data.get("email"),
        first_name=data.get("firstname"),
        last_name=data.get("lastname"),
        user_type=data.get("user_status"),
        phone_number=data.get("phone"),
        purpose=purpose,
        context=user_data.get("papers") if user_data.get("papers") else user_data.get("context"),
        amount=data.get("amount"),
        payment_reference=ref,
        other_data=user_data,
    )
    db.session.add(new_attempt)
    db.session.commit()


def log_staff_activity(**kwargs):
    new_activity = StaffActivity(
        title = kwargs.get("title"),
        description = kwargs.get("desc"),
        time = kwargs.get("time") or datetime.now(timezone.utc),
        staff = kwargs.get("staff"),
        object_id=kwargs.get("object_id"),
        object_type = kwargs.get("obj"),
    )
    db.session.add(new_activity)
    db.session.commit()

def generate_payment_reference(prefix: str):
    unique_part = uuid.uuid4().hex  # 32-char hex string
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{timestamp}-{unique_part[:8]}"


def calculate_payment_status(full_payment: int, paid:int):
    if paid > full_payment:
        payment_status = "Overpaid"
    elif full_payment == paid:
        payment_status = "Fully paid"
    else:
        payment_status = "Partly paid"
    return payment_status


def calculate_discount_amount(discount: list, papers: list):
    amount = 0
    try:
        discount_papers = db.session.execute(db.select(Paper).where(Paper.code.in_(papers))).scalars().all()
        unique_by_code = {}
        for paper in discount_papers:
            if paper.code not in unique_by_code:
                unique_by_code[paper.code] = paper
        distinct_papers = list(unique_by_code.values())
    except Exception as e:
        print(f"error: {e}, {discount}, {papers}")
        return jsonify({
            "error": f"{e}, {discount}, {papers}"
        })

    for i in range(len(distinct_papers)):
        amount += distinct_papers[i].price * (discount[i]/100)
    return amount

# def store_receipt(no: str, reg: str, student_id: int, file: BytesIO):
#     try:
#         file.seek(0)
#         binary_data = file.read()
#         receipt = Receipt(
#             receipt_number=no,
#             student_reg=reg,
#             pdf_data=binary_data,
#             student_id=student_id
#         )
#         db.session.add(receipt)
#         db.session.commit()
#         print("Receipt stored successfully.")
#     except Exception as e:
#         print(e)
#         db.session.rollback()
#         raise ValueError #Create custom erro later
#     finally:
#         pass
#         # db.session.close()


def move_signee(info: dict, sponsored: bool, email: str, paid: any, spons_details: any=None):
    print("IN move signee")
    stmt = select(func.count()).select_from(Student)
    stmt2 = sqlalchemy.text("SELECT last_value FROM students_id_seq")
    ser = db.session.execute(stmt2).scalar()
    total_students = db.session.execute(stmt).scalar()
    print(ser, total_students)
    year_code = encode_year(datetime.now(timezone.utc).year)  # e.g., 6318
    serial_code = encode_serial(total_students)
    if sponsored:
        sponsor = spons_details.company
        sponsored_papers = ",".join([paper.split("-")[0] for paper in spons_details.papers])
        employment = "Fully/Self employed"
        papers = db.session.execute(db.select(Paper).where(Paper.code.in_(spons_details.papers))).scalars().all()
        paid = sum([paper.price for paper in papers])
        diet = db.session.execute(db.select(Diet).where(Diet.name == spons_details.diet_name)).scalar()
    else:
        sponsor = None
        sponsored_papers = ""
        employment = info.get("employed")
        papers = db.session.execute(db.select(Paper).where(Paper.code.in_(info.get("papers")))).scalars().all()
        paid = int(paid/100)
        diet = db.session.execute(db.select(Diet).where(Diet.name == info.get("diet_name"))).scalar()

    # print(info)
    full_payment = sum([paper.price for paper in papers])
    discount_amount = calculate_discount_amount(info.get("discount", [0]), info.get("discount_papers", []))
    full_payment = full_payment - discount_amount
    payment_status = calculate_payment_status(full_payment, paid-5000)
    acca_reg_no = info.get("acca_reg") + "~" + uuid.uuid4().hex[:9] if info.get("acca_reg") == "001" else info.get("acca_reg")

    signee = db.session.execute(db.select(Signee).where(Signee.email == email)).scalar()
    if not signee:
        print(f"User not found, {email}")
        raise UserNotFoundError
    # if isinstance(info.get('profile_pic'), str):
    # match = re.match(r"data:image/[^;]+;base64,(.*)", info.get('profile_pic'))
    # if match:
    #     base64_data = match.group(1)
    #     profile_picture = base64.b64decode(base64_data)
    # else:
    #     profile_picture = None
    #
    #
    # if profile_picture:
    #     try:
    #         image = Image.open(io.BytesIO(profile_picture))
    #         image_format = image.format.lower()  # 'png', 'jpeg', etc.
    #         content_type = f"image/{image_format}"
    #
    #         email_username = email.split('@')[0]
    #         extension = 'jpg' if image_format == 'jpeg' else image_format
    #         s3_key = f"profile-pics/{email_username}.{extension}"
    #
    #         # Upload to S3
    #         s3.put_object(
    #             Bucket="lms-mini-storage",
    #             Key=s3_key,
    #             Body=profile_picture,
    #             ContentType=content_type
    #         )
    #         pfp_url = f"https://lms-mini-storage.s3.eu-north-1.amazonaws.com/{s3_key}"
    #         print("Upload successful!")
    #     except Exception as e:
    #         print(f"Image processing/upload failed: {e}")
    #         raise ValueError
    # else:
    #     pfp_url = None

    pfp_url = store_pfp(info.get('profile_pic'), email)

    new_student = Student(
        first_name=signee.first_name,
        last_name=signee.last_name,
        title=signee.title,
        email=email,
        reg_no=f"1331{year_code:04d}{serial_code:04d}",
        password=signee.password,
        acca_reg_no=acca_reg_no,
        birth_date=signee.birth_date,
        profile_photo=pfp_url,
        phone_number=signee.phone_number,
        gender=signee.gender,
        joined=signee.created_at,#r
        house_address=info.get("address"),
        referral_source=info.get("referral_source"),
        referrer=info.get("friend"),
        employment_status=employment,
        oxford_brookes=info.get("oxford"),
        accurate_data=info.get("accuracy"),
        alp_consent=info.get("alp_consent"),
        terms_and_cond=info.get("terms"),
    )
    print("diet assigned to enrollment:", diet, diet.id)
    new_enrollment = Enrollment(
        student_reg_no=f"1331{year_code:04d}{serial_code:04d}",
        new_student=True,
        sponsored=sponsored,
        sponsor=sponsor,
        sponsored_papers=sponsored_papers,
        total_fee=full_payment,
        amount_paid=paid,
        payment_status=payment_status,
        discount=sum(info.get("discount", [0])) / len(info.get("discount", [0])) if discount_amount > 0 else 0,
        discount_papers=info.get("discount_papers", []),
        refund=paid-full_payment if payment_status == "Overpaid" else 0,
        receivable=full_payment-paid if payment_status == "Partly paid" else 0,
        papers=papers,
        student=new_student,
        diet=diet
    )

    db.session.add(new_student)
    db.session.add(new_enrollment)
    print("Deleting signee")
    db.session.delete(signee)
    transaction_details = []
    # scholarships = db.session.query(Scholarship).filter_by(email=email).all()
    try:
        scholarships = db.session.execute(db.select(Scholarship).where(Scholarship.email == email)).scalars().all()
    except SQLAlchemyError as e:
        print("❌ Error while querying scholarships:", str(e))
        # Optionally log or re-raise the error
        scholarships = []
    if info.get("discount_papers") and scholarships:
        for scholarship in scholarships:
            if scholarship.paper in info.get("discount_papers") and scholarship.diet_name == diet.name:
                transaction_details.append({
                    "purpose": "Discount",
                    "desc": f"{scholarship.discount}% discount on {scholarship.paper}",
                    "amount": f"-{[(scholarship.discount/100)*i.price for i in papers if i.code == scholarship.paper][0]}"
                })
                scholarship.email = scholarship.email + " |used"
                scholarship.used = True
    if sponsored:
        spons_details.used = True
    db.session.commit()
    return  transaction_details


def update_action(email, action, details):
    print("In update action")
    new_action = Action(
        actor=email,
        action=action,
        description=details
    )
    db.session.add(new_action)
    db.session.commit()


def update_payment(sponsored: bool, email: str, payment_data: dict=None, spons_details: any=None, **kwargs):
    print("In update payment")
    student = db.session.execute(db.select(Student).where(Student.email == email)).scalar()

    if len(kwargs.get("context", [])) < 1 or not kwargs.get("purpose") or len(kwargs.get("user_info", [])) != 5:
        raise ValueError # Create custom error later

    max_id = db.session.execute(db.select(func.max(Payment.id))).scalar() or 0
    new_receipt_no = f"RCPT-{max_id + 1:06d}"
    user_details = kwargs.get("user_info")
    user_info = {
        "users_name": f"{user_details[0]} {user_details[1]}",
        "phone_no": user_details[2],
        "email": user_details[3],
        "reg_no": user_details[4]
    }
    if sponsored:
        papers = db.session.execute(db.select(Paper).where(Paper.code.in_(spons_details.papers))).scalars().all()
        transaction_details = [{
            "purpose": kwargs.get("purpose"),
            "desc": f"{sponsored_paper.name} Lectures",
            "amount": f"{sponsored_paper.price}",
        } for sponsored_paper in papers]
        from pprint import pprint
        pprint(transaction_details)
        stmt = (
            db.select(Enrollment)
            .join(Diet)  # Explicit join to the related Diet table
            .where(Diet.name == spons_details.diet_name)
        )
        enrollment = db.session.execute(stmt).scalar()

        receipt_file = send_receipt(receipt_no=new_receipt_no, user_data=user_info, details=transaction_details, spons=True)
        new_payment = Payment(
            amount=sum([paper.price for paper in papers]),
            payment_reference=spons_details.token,
            student_reg=student.reg_no,
            sponsored=sponsored,
            context=kwargs.get("context"),
            purpose=kwargs.get("purpose"),
            paystack_id=0000000000,
            medium=spons_details.company,
            fee=0,
            currency="Unknown",
            created_at=datetime.now(timezone.utc),
            paid_at=datetime(2060, 12, 31),
            receipt_number=new_receipt_no,
            receipt=receipt_file.getvalue(),
            enrollment=enrollment
        )
    else:
        from pprint import pprint
        print("in", type(payment_data))
        pprint(payment_data)
        payment_metadata = payment_data.get("metadata")
        skip_log = False if payment_data.get("log") else True
        transaction_details = [{
            "purpose": kwargs.get("purpose"),
            "desc": f"{paper.name} Lectures",
            "amount": f"{paper.price}",
        } for paper in db.session.execute(db.select(Paper).where(Paper.code.in_(kwargs.get("context")))).scalars().all()]
        other_transactions = kwargs.get("discount_transactions")
        other_transactions and transaction_details.extend(other_transactions) # will append if other_trans not None
        stmt = (
            db.select(Enrollment)
            .join(Diet)  # Explicit join to the related Diet table
            .where(Diet.name == payment_metadata.get("diet_name"))
        )
        enrollment = db.session.execute(stmt).scalar()


        receipt_file = send_receipt(receipt_no=new_receipt_no, user_data=user_info, details=transaction_details)
        new_payment = Payment(
            amount=payment_data.get("amount")/100,
            payment_reference=payment_data.get("reference"),
            student_reg=student.reg_no,
            context=kwargs.get("context"),
            purpose=kwargs.get("purpose"),
            paystack_id=payment_data.get("id"),
            medium=payment_data.get("channel"),
            currency=payment_data.get("currency"),
            ip=payment_data.get("ip_address"),
            attempts=payment_data.get("log")["attempts"] if not skip_log else 0,
            history=payment_data.get("log")["history"] if not skip_log else {},
            fee=payment_data.get("fees")/100 if payment_data.get("fees") else 0,
            auth_data=payment_data.get("authorization"),
            fee_breakdown=payment_data.get("fees_split"), # "fees_split" or "fees_breakdown"
            customer_data=payment_data.get("customer"),
            created_at=payment_data.get("created_at"),
            paid_at=payment_data.get("paid_at"),
            receipt_number=new_receipt_no,
            receipt=receipt_file.getvalue(),
            enrollment=enrollment
        )
    db.session.add(new_payment)
    db.session.commit()


def insert_sponsored_row(firstname, lastname, org, papers, token, diet_name):
    new_sponsor = Sponsored(
        first_name=firstname,
        last_name=lastname,
        company=org,
        papers=papers,
        token=token,
        diet_name=diet_name
    )
    db.session.add(new_sponsor)
    db.session.commit()


def post_payment_executions(reference: str, payment_data: dict) -> tuple:
    """ This function is currently only capable of processing payments for registrations """
    print("In Post payment func")
    # attempt = db.session.query(Attempt).filter_by(payment_reference=reference).first()
    attempt = db.session.execute(db.select(Attempt).where(Attempt.payment_reference == reference)).scalar()
    if not attempt:
        return jsonify(
            error={"Error": f"Unknown user reference."}
        ), 400
    # print(reference)
    payment_metadata = payment_data.get("metadata")
    user_type = attempt.user_type
    email = attempt.email
    amount_paid = payment_data["amount"]
    if user_type.lower() == "signee":
        try:
            res = move_signee(attempt.other_data, sponsored=False, paid=amount_paid, email=email)
            user = db.session.execute(db.select(Student).where(Student.email == email)).scalar()
            # currently_enrolled = [paper for entry in user.enrollments if entry.diet.completion_date > datetime.now(timezone.utc) for paper in entry.papers]
            currently_enrolled = [
                (paper, entry.diet)
                for entry in user.enrollments
                for paper in entry.papers
                if entry.diet.completion_date > datetime.now(timezone.utc)
            ]
            update_payment(sponsored=False,
                           email=email,
                           payment_data=payment_data,
                           context=attempt.context,
                           purpose=attempt.purpose,
                           user_info=[user.first_name, user.last_name, user.phone_number, user.email, user.reg_no],
                           discount_transactions=res
                           )
            operation_details = f"User registered their first ever course, payments made, [{attempt.context} | Refr: {reference}]"
            update_action(email, "Registered a course.", operation_details)
        except Exception as e:
            # pprint(attempt.other_data)
            return jsonify(
                error={"Error in post payment func": f"Unknown error {e}"}
            ), 500
        else: #User registered their first ever course, payments made, [['TX-std', 'SBL-std']]
            print("Deleting attempt")
            db.session.delete(attempt)
            db.session.commit()
            return jsonify({
                "title": user.title,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email,
                "gender": user.gender,
                "profile_pic": user.profile_photo, #base64.b64encode(user.profile_photo).decode('utf-8'),
                "reg_no": user.reg_no,
                "acca_reg_no": user.acca_reg_no,
                "papers": [{paper[0].code: (paper[0].name, paper[1].name)} for paper in currently_enrolled],
                "user_status": "student",
            }), 200
    elif user_type.lower() == "student":
        try:
            student = db.session.execute(db.select(Student).where(Student.email == email)).scalar()
            stmt = (
                db.select(Enrollment)
                .join(Diet)  # Explicit join to the related Diet table
                .where(Diet.name == payment_metadata.get("diet_name"))
            )
            print("Diet name in post payment func", payment_metadata.get("diet_name"))
            enrollment = db.session.execute(stmt).scalar()
            print("enrollment is", enrollment)
            papers = db.session.execute(db.select(Paper).where(Paper.code.in_(attempt.other_data.get("papers")))).scalars().all()

            discount_amount = calculate_discount_amount(attempt.other_data.get("discount", []), attempt.other_data.get("discount_papers", []))
            full_payment = sum([paper.price for paper in papers])
            full_payment -= discount_amount
            retaking = attempt.other_data.get("retaking")
            if enrollment is None:
                payment_status = calculate_payment_status(full_payment, int(amount_paid/100))
                diet = db.session.execute(db.select(Diet).where(Diet.name == payment_metadata.get("diet_name"))).scalar()
                new_enrollment = Enrollment(
                    student_reg_no=student.reg_no,
                    new_student=False,
                    sponsored=False,
                    sponsor=None,
                    sponsored_papers="",
                    total_fee=full_payment,
                    amount_paid=int(amount_paid/100),
                    payment_status=payment_status,
                    discount=sum(attempt.other_data.get("discount", [0])) / len(
                        attempt.other_data.get("discount", [0])) if discount_amount > 0 else 0,
                    discount_papers=attempt.other_data.get("discount_papers", []),
                    refund=int(amount_paid/100) - full_payment if payment_status == "Overpaid" else 0,
                    receivable=full_payment - int(amount_paid/100) if payment_status == "Partly paid" else 0,
                    papers=papers,
                    student=student,
                    diet=diet
                )
                db.session.add(new_enrollment)
                stmt = (
                    db.select(Enrollment)
                    .join(Diet)  # Explicit join to the related Diet table
                    .where(Diet.name == payment_metadata.get("diet_name"))
                )
                enrollment = db.session.execute(stmt).scalar()
                print("enrollment is now:", enrollment)

            enrollment.papers.extend(papers) # Relevant ones in the absence of sponsors
            enrollment.total_fee += full_payment # Relevant ones in the absence of sponsors
            enrollment.amount_paid += amount_paid/100 # Relevant ones in the absence of sponsors
            payment_status = calculate_payment_status(enrollment.total_fee, enrollment.amount_paid)
            enrollment.payment_status = payment_status
            enrollment.retake = retaking if not enrollment.retake else enrollment.retake
            enrollment.discount += sum(attempt.other_data.get("discount", [0])) / len(attempt.other_data.get("discount", [])) if discount_amount > 0 else 0
            enrollment.discount_papers = attempt.other_data.get("discount_papers")
            enrollment.refund=enrollment.amount_paid-enrollment.total_fee if payment_status == "Overpaid" else 0,
            enrollment.receivable=enrollment.total_fee-enrollment.amount_paid if payment_status == "Partly paid" else 0,
            # db.session.commit()

            transaction_discounts = []
            scholarships = db.session.execute(db.select(Scholarship).where(Scholarship.email == attempt.email)).scalars().all()
            if attempt.other_data.get("discount_papers") and scholarships:
                for scholarship in scholarships:
                    if scholarship.paper in attempt.other_data.get("discount_papers") and scholarship.diet_name == payment_metadata.get("diet_name"):
                        transaction_discounts.append({
                            "purpose": "Discount",
                            "desc": f"{scholarship.discount}% discount on {scholarship.paper}",
                            "amount": f"-{[(scholarship.discount/100)*i.price for i in papers if i.code == scholarship.paper][0]}"
                        })
                        scholarship.email = scholarship.email + " |used"
                        scholarship.used = True
            update_payment(sponsored=False,
                           email=email,
                           payment_data=payment_data,
                           context=attempt.context,
                           purpose=attempt.purpose,
                           user_info=[student.first_name, student.last_name, student.phone_number, student.email, student.reg_no],
                           discount_transactions=transaction_discounts
                           )
            operation_details = f"User registered a new course, they were a student already, payments made, [{attempt.context} | Refr: {reference}]"
            update_action(email, "Registered a course.", operation_details)
        except Exception as e:
            print(e)
            return jsonify(
                error={"Error in post payment func": f"Unknown error {e}"}
            ), 400
        else:
            db.session.delete(attempt)
            db.session.commit()
            user = db.session.execute(db.select(Student).where(Student.email == email)).scalar()
            print("Before suspect in post payment")
            # currently_enrolled = [paper for entry in user.enrollments if entry.diet.completion_date > datetime.now(timezone.utc) for paper in entry.papers]
            currently_enrolled = [
                (paper, entry.diet)
                for entry in user.enrollments
                for paper in entry.papers
                if entry.diet.completion_date > datetime.now(timezone.utc)
            ]
            print("After suspect in post payment")
            return jsonify({
                "title": user.title,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email,
                "gender": user.gender,
                "profile_pic": user.profile_photo, #base64.b64encode(user.profile_photo).decode('utf-8'),
                "reg_no": user.reg_no,
                "acca_reg_no": user.acca_reg_no,
                "papers": [{paper[0].code: (paper[0].name, paper[1].name)} for paper in currently_enrolled],
                "user_status": "student",

            }), 200
    elif user_type.lower() == "old_student":
        return False, 500 # This functionality is not available yet
    else:
        return jsonify(
            error={"Error in post payment func": f"Unknown user type"}
        ), 400


# @copy_current_request_context
def post_webhook_process(app, ref, data):
    with app.app_context():
        res = post_payment_executions(ref, data)
        print(res)
        print(res[0].json)
        print(res[0].json)
        # print(post_payment_executions(ref, data))


# -----------------------------
# Initialize Payment
# -----------------------------
# @app.route("/initialize-payment", methods=["POST"])
def initialize_payment(data: dict, type_:str):
    """ type: as in what are they paying for? reg? rev? vid? kit? etc """
    print("From init payment")
    amount = data.get("amount")
    email = data.get("email")
    reference_id = generate_payment_reference(type_.split()[1]) #type_ can be REG, REV, KIT
    try:
        log_attempt(data, type_.split()[0], reference_id)
    except Exception as e:
        return jsonify(
            error={
                "Initialization Error": f"Error logging payment attempt [{e}]",
            }
        ), 403

    headers = {
        "Authorization": f"Bearer {Config.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    print("amount sent to PAystack", amount*100)
    body = {
        "amount": amount * 100,  # Convert to kobo
        "email": email,
        "reference": reference_id,
        "metadata": {"diet_name": data["user_data"].get("diet_name"),}
    }
    print("Diet name while initializing", data["user_data"].get("diet_name"))

    try:
        response = requests.post(f"{Config.BASE_URL}/transaction/initialize", json=body, headers=headers)
    except ConnectionError as e:
        attempt = db.session.execute(db.select(Attempt).where(Attempt.payment_reference == reference_id)).scalar()
        attempt.closed_at = datetime.now(timezone.utc)
        attempt.payment_status = "failed"
        attempt.failure_cause = "Failed transaction initialization, Connection Error."
        db.session.commit()
        return jsonify(
            error={
                "Connection Error": "Failed to connect to paystack"
            }
        )
    if response.status_code != 200:
        attempt = db.session.execute(db.select(Attempt).where(Attempt.payment_reference == reference_id)).scalar()
        attempt.closed_at = datetime.now(timezone.utc)
        attempt.payment_status = "failed"
        attempt.failure_cause = "Failed transaction initialization"
        db.session.commit()
        return jsonify(
            error={
                "Initialization Error": f"Failed to initialize transaction"
            }
        ), response.status_code
    else:
        return jsonify(response.json()), 200

def exists_in_models(type_, obj, *models):
    if type_ == "email":
        for model in models:
            if db.session.execute(db.select(model).where(model.email == obj)).scalar():
                return True, model
        return False
    else:
        for model in models:
            if db.session.query(model).filter_by(phone_number=obj).scalar():
                return True, model
        return False


def generate_student_data():
    # Query all students
    students = db.session.execute(db.select(Student)).scalars().all()

    # Prepare data for DataFrame
    data = []
    for s in students:
        total_paid = sum([entry.amount_paid for entry in s.enrollments])
        total_owing = sum([entry.receivable for entry in s.enrollments])
        total_owed = sum([entry.refund for entry in s.enrollments])
        data.append({
            "ID": s.id,
            "Title": s.title,
            "First Name": s.first_name,
            "Last Name": s.last_name,
            "Email": s.email,
            "Registration Number": s.reg_no,
            "Registration Date": s.reg_date,
            "ACCA Reg No": s.acca_reg_no,
            "Birth Date": s.birth_date,
            "Phone Number": s.phone_number,
            "Gender": s.gender,
            "Joined": s.joined,
            "Total Payments": total_paid,
            "Total Receivables": total_owing,
            "Total Owed": total_owed,
            "House Address": s.house_address,
            "Referral Source": s.referral_source,
            "Referrer": s.referrer,
            "Employment Status": s.employment_status,
            "Oxford Brookes": s.oxford_brookes,
            "Accurate Data": s.accurate_data,
            "ALP Consent": s.alp_consent,
            "Terms and Conditions": s.terms_and_cond,
        })

    # Create DataFrame
    df = pd.DataFrame(data)

    # Create an in-memory Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')

    output.seek(0)
    return output


def staff_activities():
    stmt = select(StaffActivity).options(joinedload(StaffActivity.staff))
    activities = db.session.execute(stmt).scalars().all()
    checked_activities = []
    for activity in activities:
        try:
            checked_activities.append(
                {
                    "code": activity.staff.code,
                    "title": activity.title,
                    "description": activity.description,
                    "staff_firstname": activity.staff.first_name,
                    "time": activity.time,
                    "object": activity.object_type,
                }
            )
        except ZeroDivisionError:
            pass
    return checked_activities

def folder_access(directory, student_id):
    if not directory:
        raise AttributeError
    if directory.path.count("/") == 1:
        return True, "" # Root folder
    diet_name, level = directory.path.split("/")[1:3]
    directories = db.session.execute(
        db.select(DirectoryInstance)
        .where(DirectoryInstance.course_spec == diet_name)
        .order_by(DirectoryInstance.id)
    ).scalars().all()

    level_directories = [directory for  directory in directories if directory.path.count("/") == 2]
    if level_directories[0].name == level:
        return True, "First level" # First level requires no checks
    for i, dir in enumerate(level_directories):
        if dir.name != level:
            continue
        else:
            former_level = level_directories[i-1].name
            gateway = db.session.execute(
                db.select(GatewayTest)
                .where(GatewayTest.level == former_level)
            ).scalar_one_or_none()

            if not gateway:
                return True, "No gateway" # No gateway test set, so no barrier
            gateway_tests = db.session.execute(
                db.select(McqHistory)
                .where(
                    McqHistory.student_id == student_id,
                    McqHistory.code == gateway.gateway_code
                )
            ).scalars().all()
            if not gateway_tests:
                return False, "Gateway test of the previous section hasn't been taken."
            for test in gateway_tests:
                if test.status == "passed":
                    return True, "E pass"
            return False, "Has not passed the gateway test of the previous section."
            # if i+1 == len(level_directories):
            #     return True, ""
    print(level_directories[level_directories.index(level) + 1].name)
    pass


def platform_access(student_id):
    try:
        student = db.session.execute(db.select(Student).where(Student.id == student_id)).scalar()
        if student.access is None:
            return True
        elif student.access:
            return True
        else:
            return False
    except Exception:
        pass
# with app.app_context():
#     attempts = db.session.query(Attempt).filter(Attempt.payment_status == "pending").all()
#     for attempt in attempts:
#         if attempt.created_at.isoweekday == datetime.now(timezone.utc).isoweekday():
#             attempt.closed_at = datetime.now(timezone.utc)
#             attempt.payment_status = "failed"
#             attempt.failure_cause = "7 day timeout"
#             db.session.commit()
