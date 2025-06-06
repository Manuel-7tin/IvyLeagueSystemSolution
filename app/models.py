from typing import Dict, Any, Optional
from flask_login import UserMixin
from flask_migrate import Migrate
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Table, ForeignKey, BigInteger
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Text, LargeBinary, DateTime, Boolean, Date, Column, ARRAY


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)
migrate = Migrate()

student_paper = Table(
    "registrations",
    db.metadata,
    Column("student_id", Integer, ForeignKey("students.id")),
    Column("paper_id", Integer, ForeignKey("papers.id"))
)


class All(db.Model):
    __tablename__ = "all-students"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    reg_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    year: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    diet: Mapped[list] = mapped_column(ARRAY(String), nullable=False)


# Create a Staff table for all your registered staffs
class Staff(UserMixin, db.Model):
    __tablename__ = "staffs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    photo: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    # This will act like a list of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    tasks = relationship("Task", back_populates="DoneBy")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    # comments = relationship("Comment", back_populates="comment_author")


class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    DoneBy_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("staffs.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    DoneBy = relationship("Staff", back_populates="tasks")
    category: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    # Parent relationship to the comments
    comments: Mapped[str] = mapped_column(String(250), nullable=False)


class Student(db.Model):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(5), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    reg_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    reg_date: Mapped[date] = mapped_column(Date, nullable=False, default=datetime.now())
    acca_reg_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    gender = mapped_column(String(5), nullable=False)
    joined: Mapped[date] = mapped_column(Date, nullable=False)
    new_student: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sponsored: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sponsor: Mapped[str] = mapped_column(String(10), nullable=True)
    sponsored_papers: Mapped[str] = mapped_column(String(30), nullable=True)
    total_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20))
    house_address: Mapped[str] = mapped_column(String(200))
    referral_source: Mapped[str] = mapped_column(String(100)) # friend, (tiktok/insta/fb/tw) ad, flyer etc
    referrer: Mapped[str] = mapped_column(String(100), nullable=True)
    employment_status:  Mapped[str] = mapped_column(String(30))
    can_pay_partially: Mapped[bool] = mapped_column(Boolean, default=False)
    revision: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    retake: Mapped[bool] = mapped_column(Boolean, default=False)
    discount: Mapped[float] = mapped_column(Float, default=0.0)
    discount_papers: Mapped[list] = mapped_column(ARRAY(String), default=[])
    oxford_brookes: Mapped[str] = mapped_column(String(15), nullable=False)
    accurate_data: Mapped[bool] = mapped_column(Boolean, nullable=False)
    alp_consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    terms_and_cond: Mapped[bool] = mapped_column(Boolean, nullable=False)
    refund: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    receivable: Mapped[int] = mapped_column(Integer, nullable=False)
    papers = relationship("Paper", secondary=student_paper, back_populates="students")
    payments = relationship("Payment", back_populates="student")


# Create a table for the comments on the blog posts
class Payment(db.Model):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_reference: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    sponsored: Mapped[bool] = mapped_column(Boolean, default=False)
    paystack_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message : Mapped[Optional[str]] = mapped_column(String(100))
    medium : Mapped[Optional[str]] = mapped_column(String(100), nullable=False)
    currency : Mapped[Optional[str]] = mapped_column(String(100), nullable=False)
    ip : Mapped[Optional[str]] = mapped_column(String(100))
    attempts: Mapped[Optional[int]] = mapped_column(Integer)
    history: Mapped[Optional[dict]] = mapped_column(db.JSON)
    fee: Mapped[int] = mapped_column(Integer, nullable=False)
    auth_data: Mapped[Optional[dict]] = mapped_column(db.JSON)
    fee_breakdown: Mapped[Optional[dict]] = mapped_column(db.JSON)
    customer_data: Mapped[Optional[dict]] = mapped_column(db.JSON)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    paid_at: Mapped[date] = mapped_column(Date, nullable=False)
    student_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("students.id"))
    student = relationship("Student", back_populates="payments")


class Paper(db.Model):
    __tablename__ = "papers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    students = relationship("Student", secondary=student_paper, back_populates="papers")
    code: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Attempt(db.Model):
    __tablename__ = "attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    user_type: Mapped[str] = mapped_column(String(20), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[date] = mapped_column(DateTime, default=datetime.now)
    purpose: Mapped[str] = mapped_column(String(30), nullable=False)
    context: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    closed_at: Mapped[Optional[date]] = mapped_column(DateTime)
    payment_reference: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    payment_status: Mapped[str] = mapped_column(String(20), default='pending')
    failure_cause: Mapped[Optional[str]] = mapped_column(String(200))
    # Store everything else here
    other_data: Mapped[dict] = mapped_column(db.JSON, nullable=False)  # holds dob, courses, etc.
    # payment_data: Mapped[dict] = mapped_column(db.JSON)


class Signee(db.Model):
    __tablename__ = "signees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(5), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), unique=True)
    created_at = mapped_column(DateTime, default=datetime.now)
    email_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender = mapped_column(String(5), nullable=False)
    can_pay_partially: Mapped[bool] = mapped_column(Boolean, default=False)


class Sponsored(db.Model):
    __tablename__ = "sponsored"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    company: Mapped[str] = mapped_column(String(20), nullable=False)
    papers: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    token: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Action(db.Model):
    __tablename__ = "actions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(DateTime, default=datetime.now())
    actor: Mapped[str] = mapped_column(String(40), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(150), nullable=False)


class SystemData(db.Model):
    __tablename__ = "system_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_name: Mapped[str] = mapped_column(String, nullable=False)
    data: Mapped[Dict[str, Any]] = mapped_column(db.JSON, default={})


class Scholarship(db.Model):
    __tablename__ = "scholarships"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    paper: Mapped[str] = mapped_column(String, nullable=False)
    discount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
