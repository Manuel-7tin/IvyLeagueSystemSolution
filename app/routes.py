import json
import os

import requests
import pandas as pd
from io import BytesIO
from config import Config
from threading import Thread
from datetime import datetime
from .errors import UserNotFoundError
from sqlalchemy.exc import IntegrityError
from flask import jsonify, request, send_file
from services.other_services import check_api, auth_required
from werkzeug.security import generate_password_hash, check_password_hash
from services.db_services import insert_sponsored_row, is_valid_password
from services.db_services import move_signee, update_action, update_payment, initialize_payment
from services.db_services import post_payment_executions, post_webhook_process, exists_in_models
from services.account_services import send_signup_message, verify_email, send_password_reset_message
from .models import db, All, Payment, Signee, Student, Sponsored, Paper, SystemData, Scholarship, Attempt


def register_routes(app):
    api_key = os.getenv("API_KEY")


    # -----------------------------
    # Verify Payment
    # -----------------------------
    @app.route("/api/v1/verify/<reference>", methods=["GET"])
    @auth_required
    def verify_payment(reference):
        verified = db.session.query(Payment).filter_by(payment_reference=reference).scalar()
        if verified:
            user = verified.student
            return jsonify({
                "title": user.title,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email,
                "gender": user.gender,
                "reg_no": user.reg_no,
                "acca_reg_no": user.acca_reg_no,
                "papers": [{paper.code: paper.name} for paper in user.papers],
                "user_status": "student",
            }), 200

        headers = {
            "Authorization": f"Bearer {Config.PAYSTACK_SECRET_KEY}"
        }

        try:
            response = requests.get(f"{Config.BASE_URL}/transaction/verify/{reference}", headers=headers)
        except ConnectionError as e:
            return jsonify(
                error={
                    "Connection Error": "Failed to connect to paystack"
                }
            )

        if response.status_code != 200 or not response.json().get("status"):
            return jsonify(error={"error": "Verification failed"}), 500
        else:
            from pprint import pprint
            feedback = response.json()["data"]
            pprint(feedback)
            if feedback.get("status") == "success":
                exec_response = post_payment_executions(reference, feedback)
                if exec_response[1] != 200:
                    # key = list(exec_response[0].json["error"].keys())[0]
                    key, value = list(exec_response[0].json["error"].items())[0]
                    return jsonify(
                        error = {
                            "message": "Payment confirmed but internal db error, na gbese be this.",
                            "paystack_says": response.json()["message"],
                            key: value #exec_response[0].json["error"][key]
                        }
                    ), exec_response[1]
                return jsonify(
                    {
                        "status": "success",
                        "message": "Payment confirmed, all db updated",
                        "paystack_says": response.json()["message"],
                        "user_data": exec_response[0].json
                    }
                ), 200
            elif feedback.get("status") in ["ongoing", "pending", "processing", "queued"]:
                return jsonify(
                    {
                        "status": "patience",
                        "message": "Payment underway, exercise patience bros.",
                        "paystack_says": response.json()["message"],
                    }
                ), 202
            elif feedback.get("status") == "abandoned":
                return jsonify(
                    {
                        "status": "some patience needed",
                        "message": "Payment underway, it probably hasn't started.",
                        "paystack_says": response.json()["message"],
                    }
                ), 202
            elif feedback.get("status") in ["failed", "reversed"]:
                attempt = db.session.execute(db.select(Attempt).where(Attempt.payment_reference == reference)).scalar()
                attempt.closed_at = datetime.now()
                attempt.payment_status = "failed"
                attempt.failure_cause = "Transaction declined or reversed"
                db.session.commit()
                return jsonify(
                    {
                        "status": "obliterated",
                        "message": "The payment is either failed or reversed.",
                        "paystack_says": response.json()["message"],
                    }
                ),410
        # data = response.json()
        # return jsonify(data), 200


    # -----------------------------
    # Webhook
    # -----------------------------
    @app.route("/api/v1/webhook", methods=["POST"])
    @auth_required
    def handle_webhook():
        print("They don call webhook oo")
        event = request.json
        event_type = event.get("event")
        reference = event.get("data", {}).get("reference")

        print(f"Webhook event: {event_type} for reference: {reference}")

        # Here you’d typically update the DB
        # Example:
        # if event_type == 'charge.success':
        #     update_payment_status(reference, status='completed')
        # with app.app_context():
        thread = Thread(target=post_webhook_process, args=(app, reference, event.get("data", {})))
        thread.start()

        return jsonify({"status": "received"}), 200


    @app.route("/api/v1/signup", methods=["POST"])
    @auth_required
    def sign_up():
        print("i dey come")
        # if request.args.get("api-key") != api_key:
        #     # g = request.args.get("api-key")
        #     return jsonify(
        #         error={
        #             "Access Denied": f"You do not have access to this resource"  # \n type:{type(g)}. it is {g}",
        #         }
        #     ), 403
        data = request.get_json()

        # Check if they are already signed up
        already_exists = [False]
        if exists_in_models("email", data.get("email"), Signee, Student, All):
            already_exists = [True, "Email"]
        elif exists_in_models("phone", data.get("phone"), Signee, Student):
            already_exists = [True, "Phone number"]
        if already_exists[0]:
            return jsonify(
                error={
                    "Tautology,": f"{already_exists[1]} already in use!"
                }
            ), 403
        if isinstance(data.get("dob"), str):
            try:
                d_o_b = datetime.fromisoformat(data.get("dob").replace("Z", "+00:00"))
            except:
                d_o_b = datetime.strptime(data.get("dob"), "%d/%m/%Y")
        else:
            d_o_b = data.get("dob")
        ver_pword = is_valid_password(data.get("password"))
        if not ver_pword[0]:
            return jsonify(
                error={
                    "Invalid Password": f"Error cause: [{ver_pword[1]}]",
                }
            ), 400
        if len(data.get("phone")) > 15:
            return jsonify(
                error={
                    "Invalid PhoneNUmber": f"{data.get('phone')} is not a valid number!",
                }
            ), 400

        hash_and_salted_password = generate_password_hash(
            data.get("password"),
            method='pbkdf2:sha256',
            salt_length=8
        )

        try:
            print(f"data is {request.method}")
            new_signee = Signee(
                # id=random.randint(3, 9),
                title=data.get("title"),
                email=data.get("email"),
                first_name=data.get("firstname").title(),
                last_name=data.get("lastname").title(),
                phone_number=data.get("phone"),
                birth_date=d_o_b,
                gender=data.get("gender"),
                password=hash_and_salted_password
            )
            send_signup_message(data.get("firstname").title(), data.get("email"))
            with app.app_context():
                db.session.add(new_signee)
                db.session.commit()
        except IntegrityError as e:
            print(str(e))
            print(data)
            return jsonify(
                error={
                    "DB Integrity Compromise": f"User email or phone number already exists",
                }
            ), 409
        except AttributeError as e:
            print(type(data), data)
            return jsonify(
                error={
                    "Invalid Key": f"You missed a key.\n{e} required keys: [firstname, lastname, title, email, gender, dob, phone, password",
                }
            ), 409
        except Exception as e:
            return jsonify(
                error={
                    "Uncaught Error": f"This error wasn't expected or planned for.\n{e}",
                }
            ), 422
        else:
            return jsonify({
                "status": "success",
                "message": "Signup successful",
            }), 201


    @app.route("/api/v1/signin", methods=["POST"])
    @auth_required
    def sign_in():
        # if request.args.get("api-key") != api_key:
        #     # g = request.args.get("api-key")
        #     return jsonify(
        #         error={
        #             "Access Denied": f"You do not have access to this resource"  # \n type:{type(g)}. it is {g}",
        #         }
        #     ), 403
        data = request.get_json()
        login_type = data.get("type")

        if login_type == "email":
            result = db.session.execute(db.select(Student).where(Student.email == data.get("email")))
            user = result.scalar()

            if not user:  # User is not a registered student
                result = db.session.execute(db.select(Signee).where(Signee.email == data.get("email")))
                user = result.scalar()
                if not user:  # User is not a signee either
                    return jsonify(
                        error={
                            "Incorrect Input": "Account does not exist" #f"Email or password incorrect"  # \n type:{type(g)}. it is {g}",
                        }
                    ), 403

                password = data.get("password")
                if check_password_hash(user.password, password):
                    return jsonify({
                        "title": user.title,
                        "firstname": user.first_name,
                        "lastname": user.last_name,
                        "email": user.email,
                        "gender": user.gender,
                        "user_status": "signee",
                        "dob": user.birth_date,
                        "phone_no": user.phone_number,
                        "email_verified": user.email_confirmed,
                        "address": "",
                        "reg_no": "",
                        "acca_reg": ""
                    })
                else:
                    password_incorrect = True
            else:
                password = data.get("password")
                if check_password_hash(user.password, password):
                    return jsonify({
                        "title": user.title,
                        "firstname": user.first_name,
                        "lastname": user.last_name,
                        "email": user.email,
                        "gender": user.gender,
                        "dob": user.birth_date,
                        "phone_no": user.phone_number,
                        "email_verified": True, # temporarily
                        "address": user.house_address,
                        "reg_no": user.reg_no,
                        "acca_reg": user.acca_reg_no,
                        "papers": [{paper.code: paper.name} for paper in user.papers],
                        "user_status": "student",
                    })
                else:
                    password_incorrect = True
            if password_incorrect:
                # print(data.get("password"))
                return jsonify(
                    error={
                        "Incorrect Input": f"Email or Password incorrect"  # \n type:{type(g)}. it is {g}",
                    }
                ), 403

        elif login_type == "reg":
            result = db.session.execute(db.select(Student).where(Student.reg_no == data.get("reg_no")))
            user = result.scalar()

            if not user:  # User is not a registered student
                return jsonify(
                    error={
                        "Incorrect Input": f"Registration number or password incorrect"
                        # \n type:{type(g)}. it is {g}",
                    }
                ), 403

            password = data.get("password")
            if check_password_hash(user.password, password):
                    return jsonify({
                        "title": user.title,
                        "firstname": user.first_name,
                        "lastname": user.last_name,
                        "email": user.email,
                        "gender": user.gender,
                        "dob": user.birth_date,
                        "phone_no": user.phone_number,
                        "email_verified": True, # temporarily
                        "address": user.house_address,
                        "reg_no": user.reg_no,
                        "acca_reg": user.acca_reg_no,
                        "papers": [{paper.code: paper.name} for paper in user.papers],
                        "user_status": "student",
                    })
            else:
                return jsonify(
                    error={
                        "Incorrect Input": f"Registration number or Password incorrect"
                        # \n type:{type(g)}. it is {g}",
                    }
                ), 403
        else:
            return jsonify(
                error={
                    "Unknown Login Type": f"Log-in type {login_type} is not accepted",
                }
            ), 409


    @app.route("/api/v1/refresh", methods=["GET"])
    @auth_required
    def send_data():
        output = db.session.execute(db.select(Student).where(Student.email == request.args.get("email")))
        person = output.scalar()

        if not person:  # User is not a registered student
            output = db.session.execute(db.select(Signee).where(Signee.email == request.args.get("email")))
            person = output.scalar()
            if not person:  # User is not a signee either
                return jsonify(
                    error={
                        "Incorrect Input": "Account does not exist"
                        # f"Email or password incorrect"  # \n type:{type(g)}. it is {g}",
                    }
                ), 403
            return jsonify({
                "title": person.title,
                "firstname": person.first_name,
                "lastname": person.last_name,
                "email": person.email,
                "gender": person.gender,
                "user_status": "signee",
                "dob": person.birth_date,
                "phone_no": person.phone_number,
                "email_verified": person.email_confirmed,
                "address": "",
                "reg_no": "",
                "acca_reg": ""
            })
        return jsonify({
            "title": person.title,
            "firstname": person.first_name,
            "lastname": person.last_name,
            "email": person.email,
            "gender": person.gender,
            "dob": person.birth_date,
            "phone_no": person.phone_number,
            "email_verified": True,  # temporarily
            "address": person.house_address,
            "reg_no": person.reg_no,
            "acca_reg": person.acca_reg_no,
            "papers": [{paper.code: paper.name} for paper in person.papers],
            "user_status": "student",
        })

    @app.route("/api/v1/register", methods=["POST"])
    @auth_required
    def register():
        # if request.args.get("api-key") != api_key:
        #     return jsonify(
        #         error={
        #             "Access Denied": "You do not have access to this resource",
        #         }
        #     ), 403
        data = request.get_json()
        keys = ["diet", "email", "firstname", "lastname", "sponsored", "user_status", "user_data"] #reg_no
        keys += ["amount", "phone"] if not data.get("sponsored") else []
        nested = {
            "user_data": []
        }
        nested["user_data"] += ["employed", "acca_reg", "address", "referral_source", "oxford", "accuracy", "alp_consent", "terms"] if data.get("user_status") == "signee" else []
        nested["user_data"] += ["papers", "discount", "discount_papers"] if not data.get("sponsored") else []
        valid, error_info, res_code = check_api(data=data, required_fields=keys, nested_fields=nested)
        print(error_info)
        if not valid:
            return jsonify(
                error={
                    error_info[0]: error_info[1]
                }
            ), res_code
        # Each diet has its own tables that would be named as such, the table to open will be determined by the diet
        # This is for future updates purposes
        print("tiypiee:", type(data.get("diet")))
        user_type = data.get("user_status", "None")
        if user_type.lower() != "signee" and user_type.lower() != "student":
            return jsonify(
                error={
                    "Unknown User Type": f"User type {user_type} is not accepted"
                }
            ), 400
        if data.get("sponsored"):  # User is sponsored by an organization
            sponsorship = db.session.execute(db.select(Sponsored).where(Sponsored.token == data.get("token"))).scalar()
            if not sponsorship:
                return jsonify(
                    error={
                        "Invalid Token": f"The code is invalid, try again.", # code refers to token in db # {(data.get("token"), Sponsored.token)}",
                    }
                ), 409
            elif not (sponsorship.first_name.title() == data.get("firstname") and sponsorship.last_name.title() == data.get("lastname")):
                hello = (sponsorship.first_name.title(), data.get("firstname"), sponsorship.last_name.title(), data.get("lastname"))
                return jsonify(
                    error={
                        "Name Mismatch": f"Your registered name contrasts with our records {hello}.",
                    }
                ), 409
            elif sponsorship.used:
                return jsonify(
                    error={
                        "Expired Token": "The inputted code is used, try again.",
                    }
                ), 409
            sponsored_papers = db.session.query(Paper).filter(Paper.code.in_(sponsorship.papers)).all()

            if user_type.lower() == "signee":
                try:
                    if not data.get("user_data"):
                        return jsonify(
                            error={
                                "Error": f"Missing user data.",
                            }
                        ), 400
                    move_signee(data.get("user_data"), sponsored=True, paid=None, spons_details=sponsorship,
                                email=data.get("email"))
                    operation_details = f"User registered their first ever course, courses are sponsored, [{sponsorship.papers}]"
                    update_action(data.get("email"), "Became a student.", operation_details)
                    student = db.session.execute(db.select(Student).where(Student.email == data.get("email"))).scalar()
                    update_payment(sponsored=True,
                                   email=data.get("email"),
                                   spons_details=sponsorship,
                                   context=sponsorship.papers,
                                   purpose="Tuition",
                                   user_info=[student.first_name, student.last_name, student.phone_number,
                                              data.get("email"), student.reg_no],
                                   )
                except UserNotFoundError as e:
                    return jsonify(
                        error={
                            "In-Existent User": f"User not found [{e}].",
                        }
                    ), 409
                # else:
                #     return jsonify({
                #         "status": "success",
                #         "message": "Registration successful",
                #     }), 201
            elif user_type.lower() == "student":
                try:
                    student = db.session.execute(db.select(Student).where(Student.reg_no == data.get("reg_no"))).scalar()
                    for j in sponsorship.papers:
                        if j in [paper.code for paper in student.papers]:
                            return  jsonify(
                                error={
                                    "User Error": f"You are already taking {j}, you can't take it twice concurrently. Contact Admin for support."
                                }
                            ), 404
                    if (len(sponsorship.papers) + len(student.papers)) > 4:
                        return jsonify(
                            error={
                                "Error": "User cannot register more than four papers in a diet.",
                            }
                        ), 409
                    student.sponsored = True
                    student.sponsors = sponsorship.company
                    student.sponsored_papers = ",".join([sponsored_paper.split("-")[0] for sponsored_paper in sponsorship.papers])
                    student.employment_status = "Fully/Self employed"
                    student.papers.extend(sponsored_papers)  # Relevant ones in the absence of sponsors
                    student.total_fee += sum([sponsored_paper.price for sponsored_paper in sponsored_papers])  # Relevant ones in the absence of sponsors
                    student.amount_paid += sum(
                        [sponsored_paper.price for sponsored_paper in sponsored_papers])  # Relevant ones in the absence of sponsors
                    sponsorship.used = True
                    db.session.commit()
                    operation_details = f"User registered a new course, they were a student already, courses are sponsored, [{sponsorship.papers}]"
                    update_payment(sponsored=True,
                                   email=data.get("email"),
                                   spons_details=sponsorship,
                                   context=sponsorship.papers,
                                   purpose="Tuition",
                                   user_info=[student.first_name, student.last_name, student.phone_number,
                                              data.get("email"), student.reg_no],
                                   )
                    update_action(data.get("email"), "Registered a course.", operation_details)
                except Exception as e:
                    print(e)
                    return jsonify(
                        error={
                            "Unknown Error": f"Error message: [{e}].",
                        }
                    ), 409
                # else:
            elif user_type == "old student":
                pass


            fresh_student = db.session.query(Student).filter_by(email=data.get("email")).scalar()
            if fresh_student and user_type != "old student":
                return jsonify({
                    "status": "success",
                    "message": "Registration successful",
                    "user_status": "student",
                    "reg_no": fresh_student.reg_no,
                    "acca_reg_no": fresh_student.acca_reg_no,
                    "papers": [{paper.code: paper.name} for paper in fresh_student.papers],
                    "fee": 0,
                    "scholarship": [] if not fresh_student.discount > 0 else fresh_student.discount_papers
                }), 201
            else:
                return jsonify(
                    error={
                        "Intense Confusion": f"😕 | 😵 | 💫 | 🤔 |  😶☁.",
                    }
                ), 409
        else:  # User is sponsoring themselves
            if data.get("user_status").lower() == "student":
                done_list = []
                student = db.session.query(Student).filter_by(email=data.get("email")).scalar()
                for i in data.get("user_data")["papers"]:
                    if i in [paper.code for paper in student.papers]:
                        done_list.append(i)
                if done_list:
                    return jsonify(
                        error={
                        "Error": "User cannot register a paper they are already taking."
                    }
                    ), 403
                if len(data.get("user_data")["papers"])+ len(student.papers) > 4:
                    return jsonify(
                        error={
                            "Error": "User cannot register more than four papers in a diet."
                        }
                    ), 409

            return initialize_payment(data, "Tuition REG")


    @app.route("/api/v1/required-info", methods=["GET"])
    @auth_required
    def needed_info():
        # if request.args.get("api-key") != api_key:
        #     return jsonify(
        #         error={
        #             "Access Denied": "You do not have access to this resource",
        #         }
        #     ), 403
        data_name = request.args.get("title")
        data = db.session.query(SystemData).filter_by(data_name=data_name).scalar()
        if data:
            return jsonify(data.data), 200
        else:
            return jsonify(
                error={
                    "Inexistent Data": f"The requested data {data_name} does not exist."
                }
            ), 400

    @app.route("/api/v1/courses", methods=["GET"])
    @auth_required
    def get_courses():
        # if request.args.get("api-key") != api_key:
        #     return jsonify(
        #         error={
        #             "Access Denied": f"You do not have access to this resource",
        #         }
        #     ), 403
        try:
            user_type = request.args.get("user_status").lower()
            if user_type.lower() not in ["signee", "student", "old_student"]:
                return jsonify(
                    error={
                        "Unknown User Type": f"User type {user_type} is not accepted"
                    }
                ), 400
        except AttributeError as e:
            return jsonify(
                error={
                    "Missing Data": "User status not found!!"
                }
            ), 400
        details = {}
        if request.args.get("reg").lower() in ["true", 1, "t", "y", "yes", "yeah"]:
            scholarships = db.session.query(Scholarship).filter_by(email=request.args.get("email")).all()
            details["scholarships"] = [{"paper": i.paper, "percentage": i.discount} for i in scholarships]
            details["fee"] = [{"amount":5000, "reason": "One time student registration."}] if user_type == "signee" else []
            acca_reg_no = request.args.get("acca_reg")
            if user_type ==  "signee":
                signee = db.session.query(Signee).filter_by(email=request.args.get("email")).scalar()
                if db.session.query(Student).filter_by(acca_reg_no=acca_reg_no).scalar() and acca_reg_no != "001" and acca_reg_no:
                    return jsonify(
                        error={
                            "Tautology": f"ACCA registration number already used."
                        }
                    ), 400
                elif len(acca_reg_no) < 7 and acca_reg_no != "001":
                    return jsonify(
                        error={
                            "Invalid Error": f"ACCA registration number invalid."
                        }
                    ), 400
                elif not signee:
                    print(request.args)
                    return jsonify(
                        error={
                            "Error": f"User doesn't exist."
                        }
                    ), 400
                details["course_limit"] = 4
                details["partial_payment"] = signee.can_pay_partially
            if user_type == "student":
                student = db.session.query(Student).filter_by(email=request.args.get("email")).scalar()
                if not student:
                    return jsonify(
                        error={
                            "Some Kinda Error": "Student not found!!"
                        }
                    ), 400
                details["current_papers"] = [paper.code for paper in student.papers]
                details["course_limit"] = 4 - len(student.papers)
                details["fee"].append({"amount": student.receivable, "reason": "One time student registration."})
                details["partial_payment"] = student.can_pay_partially
            #if student is scholarship qualified
        try:
            papers = db.session.query(Paper).all()
            paper_details = []
            taken_papers = []
            for i in papers:
                paper_name = " ".join(i.name.split()[:-1]) if "Standard" in i.name or "Intensive"in i.name else i.name
                if paper_name in taken_papers:
                    continue
                taken_papers.append(paper_name)
                if paper_name == i.name:
                    paper_types = []
                    prices = [i.price]
                    paper_codes = [i.code]
                else:
                    paper_types = [item.name.split()[-1] for item in papers if paper_name in item.name and len(item.name.split()) == len(paper_name.split())+1]
                    paper_codes = [item.code for item in papers if paper_name in item.name and len(item.name.split()) == len(paper_name.split())+1]
                    prices = [item.price for item in papers if paper_name in item.name and len(item.name.split()) == len(paper_name.split())+1]
                paper_details.append(
                    {
                        "name": paper_name,
                        "category": i.category,
                        "type": paper_types,
                        "code": paper_codes,
                        "price": prices,
                    }
                )
            details["papers"] = paper_details
        except Exception as e:
            return jsonify(
                error={
                    "Internal Error": f"Error message: [{e}]",
                }
            ), 500
        else:
            return jsonify(details), 200


    @app.route("/api/v1/confirm-email", methods=["POST"])
    @auth_required
    def confirm_email():
        # if request.args.get("api-key") != api_key:
        #     return jsonify(
        #         error={
        #             "Access Denied": f"You do not have access to this resource",
        #         }
        #     ), 403
        token = request.args.get("token")
        if token is None:
            data = request.get_json()
            user = db.session.query(Signee).filter_by(email=data.get("email")).scalar()
            if not user:
                return jsonify(error={"In-Existent User": "Email doesn't exist"}), 400
            send_signup_message("User", data.get("email"))
            return jsonify({"message": "Check your email to confirm your account."}), 200
        else:
            res = verify_email(token)
            if res[0] == "success":
                user = db.session.query(Signee).filter_by(email=res[1]).scalar()
                user.email_confirmed = True
                db.session.commit()
                return jsonify({
                    "status": "success",
                    "message": "Email verified successfully!"
                }), 200
            else:
                return jsonify(
                    error={
                    "Verification Failed": f"Email unverified, token is {res[0]}!"
                }
                ), 400

    @app.route("/api/v1/reset-password", methods=["POST"])
    @auth_required
    def reset_password():
        # if request.args.get("api-key") != api_key:
        #     return jsonify(
        #         error={
        #             "Access Denied": f"You do not have access to this resource",
        #         }
        #     ), 403
        token = request.args.get("token")
        data = request.get_json()
        if token:
            ver_pword = is_valid_password(data.get("password"))
            if not ver_pword[0]:
                return jsonify(
                    error={
                        "Invalid Password": f"Error cause: [{ver_pword[1]}]",
                    }
                ), 400
            res = verify_email(token)
            if res[0] == "success":
                user = db.session.query(Signee).filter_by(email=res[1]).scalar()
                user = db.session.query(Student).filter_by(email=res[1]).scalar() if not user else user
                hash_and_salted_password = generate_password_hash(
                    data.get("password"),
                    method='pbkdf2:sha256',
                    salt_length=8
                )
                user.password = hash_and_salted_password
                db.session.commit()
                return jsonify({
                    "status": "success",
                    "message": "Password updated successfully!"
                }), 200
            else:
                return jsonify(
                    error={
                    "Update Failed": f"Password not updated, token is {res[0]}!"
                }
                ), 400
        else:
            user = db.session.query(Signee).filter_by(email=data.get("email")).scalar()
            user = db.session.query(Student).filter_by(email=data.get("email")).scalar() if not user else user
            if not user:
                return jsonify(error={"In-Existent User": "Email doesn't exist"}), 400
            send_password_reset_message("there", data.get("email"))
            return jsonify({"message": "Check your email to change your account password."}), 200


    @app.route("/api/v1/temp", methods=["GET"])
    @auth_required
    def gy():
        s = request.args.get("api-key").lower() == "true"
        print(type(s), s)
        return jsonify({"res": s})

    @app.route("/api/v1/receipt", methods=["GET"])
    @auth_required
    def get_receipt():
        print("in get receipt")
        receipt_no = request.args.get("receipt_no")
        payment = db.session.query(Payment).filter_by(receipt_number=receipt_no).first()
        if not payment:
            print("receipt not found", receipt_no)
            return jsonify(
                error={
                    "MissingData Error": f"Receipt file not found."
                }
            ), 404
        return send_file(
            BytesIO(payment.receipt),
            mimetype='application/pdf',
            download_name=f"receipt_{payment.receipt_number}.pdf"
        )


    @app.route("/api/v1/all-payments", methods=["GET"])
    @auth_required
    def all_payments():
        reg_no = request.args.get("reg_no")
        if not reg_no:
            print("no reg no")
            return jsonify(
                error={
                    "Missing Argument": f"No registration number found."
                }
            ), 404
        payments = db.session.query(Payment).filter_by(student_reg=reg_no).all()
        if not payments:
            print(reg_no)
            return jsonify(
                error={
                    "In-Existent Data": f"No payment history found for this user."
                }
            ), 404
        response = []
        for payment in payments:
            response.append({
                "papers": payment.context,
                "ref_id": payment.payment_reference,
                "amount": payment.amount,
                "date": payment.paid_at
            })
        return jsonify(response)

    @app.route("/api/v1/receipts", methods=["GET"])
    @auth_required
    def all_receipts():
        reg_no = request.args.get("reg_no")
        payments = db.session.query(Payment).filter_by(student_reg=reg_no).all()
        response = []
        for payment in payments:
            response.append({
                "receipt_no": payment.receipt_number,
                "papers": payment.context,
                "amount": payment.amount,
                "date": payment.paid_at #Change after editing db
            })
        return response



    try:
        with app.app_context():
            papers = pd.read_excel("resource/ivy pricing.xlsx")
            """"""
            for i, paper in papers.iterrows():
                if not isinstance(paper["Knowledge papers"], float):
                    if "papers" in paper["Knowledge papers"].lower():
                        continue
                    variations = [(" Standard", "std"), (" Intensive", "int")]
                    for i in range(2):
                        code = paper["Knowledge papers"].split()[-1]
                        if code in ["BT", "FA", "MA", "CBL", "OBU", "DipIFRS"] and i != 0:
                            continue
                        if code in ["OBU", "DipIFRS"]:
                            revision = 0
                            extension = ""
                            category = "Additional"
                            price = paper.Standard
                        else:
                            if code in ["BT", "FA", "MA"]:
                                category = "Knowledge"
                            elif code in ["PM", "FR", "AA", "TAX", "FM", "CBL"]:
                                category = "Skill"
                            else:
                                category = "Professional"
                            code = "TX" if code == "TAX" else code
                            code = f"{code}-{variations[i][1]}"
                            extension = variations[i][0]
                            price = paper.Standard + (paper.revision if code[-3:] == "std" else 0)
                            revision = 20_000 if code[-3:] == "std" else 0

                        new_paper = Paper(
                            name=" ".join(paper["Knowledge papers"].split()[:-1]).title() + extension,
                            code=code,
                            price=int(price),
                            revision=revision,
                            category=category
                        )
                        db.session.add(new_paper)
                db.session.commit()

            with app.app_context():
                with open("resource/questions.json", mode="r") as file:
                    data = json.load(file)
                new_data = SystemData(
                    data_name="reg_form_info",
                    data=data
                )
                db.session.add(new_data)
                db.session.commit()
        with app.app_context():
            insert_sponsored_row("John", "Doe", "KPMG", ["APM-std", "BT-int"], "KPMG12345")
            insert_sponsored_row("Ayomide", "Ojutalayo", "Deloitte", ["AFM-std", "SBL-int"], "Deloitte789")
            insert_sponsored_row("Ayomide", "Ojutalayo", "AGBA", ["AFM-std", "PM-int"], "AGBA123")
            insert_sponsored_row("Jane", "Doe", "PWC", ["FM-std", "MA-int"], "PWC12345")

        for pp in ["TX-std", "CBL-int"]:
            with app.app_context():
                new_schols = Scholarship(
                    email="Jan@samp.com",
                    paper=pp,
                    discount=15,
                )
                db.session.add(new_schols)
                db.session.commit()

        with app.app_context():
            new_schols2 = Scholarship(
                email="ojutalayoayomide21@gmail.com",
                paper="TX-std",
                discount=20,
            )
            db.session.add(new_schols2)
            db.session.commit()
    except Exception as e:
        print(f"The expected error don show, i catch the werey. {e}")

