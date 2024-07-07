import os

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

USERNAME = os.getenv("USERNAME", "")
PASSWORD = os.getenv("PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "")
MYSQL_PORT = os.getenv("MYSQL_PORT", "")

db = declarative_base()


class Member(db):
    __tablename__ = "member"
    user_id = Column(Integer, ForeignKey('user.user_id', name='fk_member_user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    course_id = Column(Integer, ForeignKey('course.course_id', name='fk_member_course_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    role = Column(Integer)

    user = relationship('User', back_populates='courses')
    course = relationship('Course', back_populates='users')


class User(db):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)

    courses = relationship('Member', back_populates='user')


class Course(db):
    __tablename__ = "course"
    course_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), unique=True, nullable=False)

    users = relationship('Member', back_populates='course')


if __name__ == "__main__":
    engine = create_engine(f'mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/roster')
    # === 建立資料庫 ===
    db.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    # insert the data, Instructor 0 and Learner 1
    with open('./data.txt', "r") as f:
        raw_data = f.readlines()

    users_data = []
    courses_data = []
    members_data = []

    for r in raw_data:
        row_data = r.replace("\n", "")
        if row_data:
            user, title, role = row_data.split(", ")
            role = 0 if role == "Instructor" else 1
            users_data.append( {'name': user})
            courses_data.append({'title': title})
            members_data.append({'user_name': user, 'course_title': title, 'role': role})

    print(users_data, courses_data, members_data)
    try:
        # Begin a transaction
        session.begin()
        # Insert or update Users and Courses
        users_dict = {}
        courses_dict = {}

        print("Start insert the users")
        # Insert or update Users
        for user_data in users_data:
            existing_user = session.query(User).filter_by(name=user_data['name']).first()
            print(existing_user.user_id)
            if not existing_user:
                new_user = User(name=user_data['name'])
                session.add(new_user)
                session.flush()  # Ensure the user_id is populated
                users_dict[user_data['name']] = new_user
            else:
                users_dict[user_data['name']] = existing_user

        print("Start insert the courses")
        # Insert or update Courses
        for course_data in courses_data:
            existing_course = session.query(Course).filter_by(title=course_data['title']).first()
            if not existing_course:
                new_course = Course(title=course_data['title'])
                session.add(new_course)
                session.flush()  # Ensure the course_id is populated
                courses_dict[course_data['title']] = new_course
            else:
                courses_dict[course_data['title']] = existing_course

        print("Start insert the members")
        # Insert Members
        for member_data in members_data:
            user_id = users_dict[member_data['user_name']].user_id
            course_id = courses_dict[member_data['course_title']].course_id
            existing_member = session.query(Member).filter_by(user_id=user_id, course_id=course_id).first()
            if not existing_member:
                session.add(Member(user_id=user_id, course_id=course_id, role=member_data['role']))

        # Commit the transaction
        session.commit()
        print("Data inserted successfully.")

    except Exception as e:
        # Rollback the transaction on error
        session.rollback()
        print(f"Error: {e}")

    # query the data
    results = session.query(
        User.name,
        Course.title,
        Member.role
    ).join(
        Member, User.user_id == Member.user_id
    ).join(
        Course, Member.course_id == Course.course_id
    ).all()

    for user_name, course_title, role in results:
        print(f'User: {user_name}, Course: {course_title}, Role: {role}')