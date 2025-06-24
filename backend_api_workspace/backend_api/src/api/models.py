from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()


class RoleEnum(str, enum.Enum):
    student = "student"
    admin = "admin"


# PUBLIC_INTERFACE
class User(Base):
    """User model with roles for student/admin, authentication fields, timestamps."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    full_name = Column(String(100))
    class_name = Column(String(40))  # Optional: student's class (if student)
    role = Column(Enum(RoleEnum), default=RoleEnum.student, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    timetables = relationship("Timetable", back_populates="uploaded_by_user")
    score_cards = relationship("ScoreCard", back_populates="student")


# PUBLIC_INTERFACE
class Timetable(Base):
    """Exam timetable with meta and reference to PDF file."""
    __tablename__ = "timetables"

    id = Column(Integer, primary_key=True)
    class_name = Column(String(40), nullable=False, index=True)
    exam_name = Column(String(80), nullable=False)
    pdf_filename = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    uploaded_by_user = relationship("User", back_populates="timetables")


# PUBLIC_INTERFACE
class ScoreCard(Base):
    """Score/mark sheet for a student."""
    __tablename__ = "score_cards"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    exam_name = Column(String(80), nullable=False)
    marks_json = Column(Text, nullable=False)  # Flexible: subject->score
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="score_cards")


# PUBLIC_INTERFACE
class Announcement(Base):
    """Paper distribution/PTA/other announcements."""
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    audience = Column(String(50), nullable=True)  # 'all', 'students', 'admin', 'class:X' etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
