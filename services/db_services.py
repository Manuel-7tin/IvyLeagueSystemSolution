import re
import uuid
import requests
import sqlalchemy
from pprint import pprint

# from run import app
from app.models import db
from config import Config
from flask import jsonify, copy_current_request_context
from datetime import datetime
from sqlalchemy import func, select
from app.errors import UserNotFoundError
from requests.exceptions import ConnectionError
from services.account_services import send_receipt
from app.models import Attempt, Student, Paper, Action, Signee, Payment, Sponsored, Scholarship


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


def generate_payment_reference(prefix: str):
    unique_part = uuid.uuid4().hex  # 32-char hex string
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
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
        discount_papers = db.session.query(Paper).filter(Paper.code.in_(papers)).all()
    except Exception as e:
        print(f"error: {e}, {discount}, {papers}")
        return jsonify({
            "error": f"{e}, {discount}, {papers}"
        })
    for i in range(len(discount_papers)):
        amount += discount_papers[i].price * (discount[i]/100)
    return amount

def move_signee(info: dict, sponsored: bool, email: str, paid: any, spons_details: any=None):
    stmt = select(func.count()).select_from(Student)
    stmt2 = sqlalchemy.text("SELECT last_value FROM students_id_seq")
    ser = db.session.execute(stmt2).scalar()
    total_students = db.session.execute(stmt).scalar()
    print(ser, total_students)
    year_code = encode_year(datetime.now().year)  # e.g., 6318
    serial_code = encode_serial(total_students)
    if sponsored:
        sponsor = spons_details.company
        sponsored_papers = ",".join([paper.split("-")[0] for paper in spons_details.papers])
        employment = "Fully/Self employed"
        papers = db.session.query(Paper).filter(Paper.code.in_(spons_details.papers)).all()
        paid = sum([paper.price for paper in papers])
    else:
        sponsor = None
        sponsored_papers = ""
        employment = info.get("employed")
        papers = db.session.query(Paper).filter(Paper.code.in_(info.get("papers"))).all()
        paid = int(paid/100)

    print(info)
    full_payment = sum([paper.price for paper in papers])
    discount_amount = calculate_discount_amount(info.get("discount", [0]), info.get("discount_papers", []))
    full_payment = full_payment - discount_amount
    payment_status = calculate_payment_status(full_payment, paid-5000)
    acca_reg_no = info.get("acca_reg") + "~" + uuid.uuid4().hex[:9] if info.get("acca_reg") == "001" else info.get("acca_reg")

    signee = db.session.execute(db.select(Signee).where(Signee.email == email)).scalar()
    if not signee:
        print(f"User not found, {email}")
        raise UserNotFoundError
    new_student = Student(
        first_name=signee.first_name,
        last_name=signee.last_name,
        title=signee.title,
        email=email,
        reg_no=f"1331{year_code:04d}{serial_code:04d}",
        password=signee.password,
        acca_reg_no=acca_reg_no,
        birth_date=signee.birth_date,
        phone_number=signee.phone_number,
        gender=signee.gender,
        joined=signee.created_at,
        new_student=True,
        sponsored=sponsored,
        sponsor=sponsor,
        sponsored_papers=sponsored_papers,
        total_fee=full_payment,
        amount_paid=paid,
        payment_status=payment_status,
        house_address=info.get("address"),
        referral_source=info.get("referral_source"),
        referrer=info.get("friend"),
        employment_status=employment,
        discount=sum(info.get("discount", [0])) / len(info.get("discount", [0])) if discount_amount > 0 else 0,
        discount_papers=info.get("discount_papers", []),
        oxford_brookes=info.get("oxford"),
        accurate_data=info.get("accuracy"),
        alp_consent=info.get("alp_consent"),
        terms_and_cond=info.get("terms"),
        refund=paid-full_payment if payment_status == "Overpaid" else 0,
        receivable=full_payment-paid if payment_status == "Partly paid" else 0,
        papers=papers,
    )
    db.session.add(new_student)
    print("Deleting signee")
    db.session.delete(signee)
    transaction_details = []
    scholarships = db.session.query(Scholarship).filter_by(email=email).all()
    if info.get("discount_papers") and scholarships:
        for scholarship in scholarships:
            if scholarship.paper in info.get("discount_papers"):
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
    new_action = Action(
        actor=email,
        action=action,
        description=details
    )
    db.session.add(new_action)
    db.session.commit()


def update_payment(sponsored: bool, email: str, payment_data: dict=None, spons_details: any=None):
    student = db.session.execute(db.select(Student).where(Student.email == email)).scalar()
    if sponsored:
        papers = db.session.query(Paper).filter(Paper.code.in_(spons_details.papers)).all()
        new_payment = Payment(
            amount=sum([paper.price for paper in papers]),
            payment_reference=spons_details.token,
            sponsored=sponsored,
            paystack_id=0000000000,
            medium=spons_details.company,
            fee=0,
            currency="Unknown",
            created_at=datetime.now(),
            paid_at=datetime(2060, 12, 31),
            student=student
        )
    else:
        from pprint import pprint
        print("in", type(payment_data))
        pprint(payment_data)
        skip_log = False if payment_data.get("log") else True
        new_payment = Payment(
            amount=payment_data.get("amount")/100,
            payment_reference=payment_data.get("reference"),
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
            student=student
        )
    db.session.add(new_payment)
    db.session.commit()


def insert_sponsored_row(firstname, lastname, org, papers, token):
    new_sponsor = Sponsored(
        first_name=firstname,
        last_name=lastname,
        company=org,
        papers=papers,
        token=token
    )
    db.session.add(new_sponsor)
    db.session.commit()


def post_payment_executions(reference: str, payment_data: dict) -> tuple:
    """ This function is currently only capable of processing payments for registrations """
    # attempt = db.session.query(Attempt).filter_by(payment_reference=reference).first()
    attempt = db.session.query(Attempt).filter_by(payment_reference=reference).scalar()
    if not attempt:
        return jsonify(
            error={"Error": f"Unknown user reference."}
        ), 400
    print(reference)
    user_type = attempt.user_type
    email = attempt.email
    amount_paid = payment_data["amount"]
    if user_type.lower() == "signee":
        try:
            res = move_signee(attempt.other_data, sponsored=False, paid=amount_paid, email=email)
            update_payment(sponsored=False, email=email, payment_data=payment_data)
        except Exception as e:
            pprint(attempt.other_data)
            return jsonify(
                error={"Error in post payment func": f"Unknown error {e}"}
            ), 500
        else: #User registered their first ever course, payments made, [['TX-std', 'SBL-std']]
            operation_details = f"User registered their first ever course, payments made, [{attempt.context} | Refr: {reference}]"
            update_action(email, "Registered a course.", operation_details)
            papers = attempt.other_data.get("papers")
            papers = db.session.query(Paper).filter(Paper.code.in_(papers))
            print("Deleting attempt")
            db.session.delete(attempt)
            db.session.commit()
            user = db.session.query(Student).filter_by(email=email).scalar()
            user_info = {
                "users_name": f"{user.first_name} {user.last_name}",
                "phone_no": user.phone_number,
                "email": user.email,
                "reg_no": user.reg_no
            }
            transaction_details = [{
                            "purpose": "Tuition",
                            "desc": f"{paper.name} Lectures",
                            "amount": f"{paper.price}",
                        } for paper in papers]
            transaction_details.extend(res)
            send_receipt(user_data=user_info, details=transaction_details)
            return jsonify({
                "title": user.title,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email,
                "sex": user.gender,
                "reg_no": user.reg_no,
                "acca_reg_no": user.acca_reg_no,
                "papers": [{paper.code: paper.name} for paper in user.papers],
                "user_status": "student",
            }), 200
    elif user_type.lower() == "student":
        try:
            student = db.session.query(Student).filter_by(email=email).scalar()
            papers = db.session.query(Paper).filter(Paper.code.in_(attempt.other_data.get("papers"))).all()

            discount_amount = calculate_discount_amount(attempt.other_data.get("discount", []), attempt.other_data.get("discount_papers", []))
            full_payment = sum([paper.price for paper in papers])
            full_payment -= discount_amount
            retaking = attempt.other_data.get("retaking")

            student.papers.extend(papers) # Relevant ones in the absence of sponsors
            student.total_fee += full_payment # Relevant ones in the absence of sponsors
            student.amount_paid += amount_paid/100 # Relevant ones in the absence of sponsors
            payment_status = calculate_payment_status(student.total_fee, student.amount_paid)
            student.payment_status = payment_status
            student.retake = retaking if not student.retake else student.retake
            student.discount += sum(attempt.other_data.get("discount", [0])) / len(attempt.other_data.get("discount", [])) if discount_amount > 0 else 0
            student.discount_papers = attempt.other_data.get("discount_papers")
            student.refund=student.amount_paid-student.total_fee if payment_status == "Overpaid" else 0,
            student.receivable=student.total_fee-student.amount_paid if payment_status == "Partly paid" else 0,
            # db.session.commit()
            update_payment(sponsored=False, email=email, payment_data=payment_data)
        except Exception as e:
            return jsonify(
                error={"Error in post payment func": f"Unknown error {e}"}
            ), 400
        else:
            operation_details = f"User registered a new course, they were a student already, payments made, [{attempt.context} | Refr: {reference}]"
            update_action(email, "Registered a course.", operation_details)
            transaction_details = [{
                                        "purpose": "Tuition",
                                        "desc": f"{paper.name} Lectures",
                                        "amount": f"{paper.price}",
                                    } for paper in papers]
            scholarships = db.session.query(Scholarship).filter_by(email=attempt.email).all()
            if attempt.other_data.get("discount_papers") and scholarships:
                for scholarship in scholarships:
                    if scholarship.paper in attempt.other_data.get("discount_papers"):
                        transaction_details.append({
                            "purpose": "Discount",
                            "desc": f"{scholarship.discount}% discount on {scholarship.paper}",
                            "amount": f"-{[(scholarship.discount/100)*i.price for i in papers if i.code == scholarship.paper][0]}"
                        })
                        scholarship.email = scholarship.email + " |used"
                        scholarship.used = True
            db.session.delete(attempt)
            db.session.commit()
            user = db.session.query(Student).filter_by(email=email).scalar()
            user_info = {
                "users_name": f"{user.first_name} {user.last_name}",
                "phone_no": user.phone_number,
                "email": user.email,
                "reg_no": user.reg_no
            }
            send_receipt(user_data=user_info, details=transaction_details)
            return jsonify({
                "title": user.title,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email,
                "sex": user.gender,
                "reg_no": user.reg_no,
                "acca_reg_no": user.acca_reg_no,
                "papers": [{paper.code: paper.name} for paper in user.papers],
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
    pprint(data) #To Remove
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
    body = {
        "amount": amount * 100,  # Convert to kobo
        "email": email,
        "reference": reference_id,
        # "metadata": {"cart_id": 398,}
    }

    try:
        response = requests.post(f"{Config.BASE_URL}/transaction/initialize", json=body, headers=headers)
    except ConnectionError as e:
        attempt = db.session.execute(db.select(Attempt).where(Attempt.payment_reference == reference_id)).scalar()
        attempt.closed_at = datetime.now()
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
        attempt.closed_at = datetime.now()
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
            if db.session.query(model).filter_by(email=obj).scalar():
                return True, model
        return False
    else:
        for model in models:
            if db.session.query(model).filter_by(phone_number=obj).scalar():
                return True, model
        return False


# with app.app_context():
#     attempts = db.session.query(Attempt).filter(Attempt.payment_status == "pending").all()
#     for attempt in attempts:
#         if attempt.created_at.isoweekday == datetime.now().isoweekday():
#             attempt.closed_at = datetime.now()
#             attempt.payment_status = "failed"
#             attempt.failure_cause = "7 day timeout"
#             db.session.commit()
