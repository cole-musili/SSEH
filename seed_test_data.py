"""
SSEH - Complete Test Data Seeder

Run:
    python manage.py shell < seed_test_data.py

Passwords:
    Teachers     -> Teacher@123
    Students     -> Student@123
    Parents      -> Parent@123
    Admin        -> Admin@123
"""

from datetime import date, time, timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.contrib.auth import get_user_model

from school.models import (
    School,
    AcademicYear,
    Term,
    GradeLevel,
    Stream,
    Subject,
    Enrollment,
    TeacherAssignment,
)

from teachers.models import TeacherProfile, TeacherQuiz

from students.models import (
    StudentProfile,
    QuizResult,
    Answer,
)

from parents.models import ParentProfile

from school_admin.models import (
    SchoolAdminProfile,
    TeacherRecord,
    Timetable,
)

from quizzes.models import Quiz, Question

from announcements.models import Announcement

from communications.models import (
    Message,
    ParentMessage,
    MessageReply,
)

from resources.models import Resource


User = get_user_model()


# ============================================================
# HELPERS
# ============================================================

def create_user(
    username,
    password,
    first_name,
    last_name,
    email,
    **flags,
):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            **flags,
        },
    )

    # Make sure existing users get the correct information too.
    user.first_name = first_name
    user.last_name = last_name
    user.email = email

    for key, value in flags.items():
        setattr(user, key, value)

    user.set_password(password)
    user.save()

    return user


def create_quiz(title, description, teacher, questions):
    quiz, created = Quiz.objects.get_or_create(
        title=title,
        defaults={
            "description": description,
            "created_by": teacher,
        },
    )

    quiz.description = description
    quiz.created_by = teacher
    quiz.save()

    # Remove old questions so rerunning the script doesn't duplicate them.
    quiz.questions.all().delete()

    for question in questions:
        Question.objects.create(
            quiz=quiz,
            text=question["text"],
            option_a=question["A"],
            option_b=question["B"],
            option_c=question["C"],
            option_d=question["D"],
            correct_answer=question["correct"],
        )

    return quiz


# ============================================================
# PASSWORDS
# ============================================================

TEACHER_PASSWORD = "Teacher@123"
STUDENT_PASSWORD = "Student@123"
PARENT_PASSWORD = "Parent@123"
ADMIN_PASSWORD = "Admin@123"


print("\n")
print("=" * 70)
print("SMART SCHOOL ENGAGEMENT HUB - TEST DATA")
print("=" * 70)


# ============================================================
# 1. SCHOOL
# ============================================================

school, _ = School.objects.get_or_create(
    name="Bright Future Academy",
    defaults={
        "address": "Mombasa Road, Nairobi",
        "email": "info@brightfuture.test",
        "phone": "+254700000001",
    },
)

school.address = "Mombasa Road, Nairobi"
school.email = "info@brightfuture.test"
school.phone = "+254700000001"
school.save()

print(f"✓ School: {school.name}")


# ============================================================
# 2. ACADEMIC YEAR
# ============================================================

academic_year, _ = AcademicYear.objects.get_or_create(
    school=school,
    name="2026/2027",
    defaults={
        "start_date": date(2026, 1, 5),
        "end_date": date(2026, 11, 27),
        "is_current": True,
    },
)

academic_year.start_date = date(2026, 1, 5)
academic_year.end_date = date(2026, 11, 27)
academic_year.is_current = True
academic_year.save()


# ============================================================
# 3. TERMS
# ============================================================

terms = {}

term_data = [
    ("Term 1", date(2026, 1, 5), date(2026, 4, 3)),
    ("Term 2", date(2026, 5, 4), date(2026, 8, 7)),
    ("Term 3", date(2026, 8, 24), date(2026, 11, 27)),
]

for name, start, end in term_data:
    term, _ = Term.objects.get_or_create(
        year=academic_year,
        name=name,
        defaults={
            "start_date": start,
            "end_date": end,
        },
    )

    term.start_date = start
    term.end_date = end
    term.save()

    terms[name] = term

print("✓ Academic year and terms created")


# ============================================================
# 4. USERS
# ============================================================

# ------------------------------------------------------------
# SCHOOL ADMIN
# ------------------------------------------------------------

admin_user = create_user(
    "schooladmin",
    ADMIN_PASSWORD,
    "Daniel",
    "Kamau",
    "admin@brightfuture.test",
    is_school_admin=True,
    is_staff=False,
    is_superuser=False,
)

admin_profile, _ = SchoolAdminProfile.objects.get_or_create(
    user=admin_user,
)

admin_profile.full_name = "Daniel Kamau"
admin_profile.phone = "+254711000001"
admin_profile.status = "active"
admin_profile.save()


# ------------------------------------------------------------
# TEACHERS
# ------------------------------------------------------------

teacher_data = [
    (
        "teacher.john",
        "John",
        "Mwangi",
        "john@brightfuture.test",
        "TCH001",
    ),
    (
        "teacher.mary",
        "Mary",
        "Wanjiku",
        "mary@brightfuture.test",
        "TCH002",
    ),
    (
        "teacher.peter",
        "Peter",
        "Otieno",
        "peter@brightfuture.test",
        "TCH003",
    ),
    (
        "teacher.grace",
        "Grace",
        "Akinyi",
        "grace@brightfuture.test",
        "TCH004",
    ),
]

teachers = {}

for username, first, last, email, teacher_id in teacher_data:

    user = create_user(
        username,
        TEACHER_PASSWORD,
        first,
        last,
        email,
        is_teacher=True,
    )

    profile, _ = TeacherProfile.objects.get_or_create(
        user=user,
    )

    profile.teacher_id = teacher_id
    profile.status = "active"
    profile.save()

    teachers[username] = user


# ------------------------------------------------------------
# PARENTS
# ------------------------------------------------------------

parent_data = [
    (
        "parent.james",
        "James",
        "Mwangi",
        "james@parents.test",
        "+254722100001",
    ),
    (
        "parent.mary",
        "Mary",
        "Otieno",
        "mary@parents.test",
        "+254722100002",
    ),
    (
        "parent.david",
        "David",
        "Kamau",
        "david@parents.test",
        "+254722100003",
    ),
    (
        "parent.susan",
        "Susan",
        "Achieng",
        "susan@parents.test",
        "+254722100004",
    ),
]

parents = {}

for username, first, last, email, phone in parent_data:

    user = create_user(
        username,
        PARENT_PASSWORD,
        first,
        last,
        email,
        is_parent=True,
    )

    profile, _ = ParentProfile.objects.get_or_create(
        user=user,
    )

    profile.first_name = first
    profile.last_name = last
    profile.phone = phone
    profile.address = "Nairobi, Kenya"
    profile.occupation = "Business"
    profile.status = "active"
    profile.save()

    parents[username] = user


# ------------------------------------------------------------
# STUDENTS
# ------------------------------------------------------------

student_data = [
    (
        "student.brian",
        "Brian",
        "Mwangi",
        "STU001",
        "parent.james",
    ),
    (
        "student.alice",
        "Alice",
        "Mwangi",
        "STU002",
        "parent.james",
    ),
    (
        "student.kevin",
        "Kevin",
        "Otieno",
        "STU003",
        "parent.mary",
    ),
    (
        "student.sharon",
        "Sharon",
        "Otieno",
        "STU004",
        "parent.mary",
    ),
    (
        "student.brian2",
        "Brian",
        "Kamau",
        "STU005",
        "parent.david",
    ),
    (
        "student.emily",
        "Emily",
        "Kamau",
        "STU006",
        "parent.david",
    ),
    (
        "student.daniel",
        "Daniel",
        "Achieng",
        "STU007",
        "parent.susan",
    ),
    (
        "student.lucy",
        "Lucy",
        "Achieng",
        "STU008",
        "parent.susan",
    ),
]

students = {}

for username, first, last, student_id, parent_username in student_data:

    user = create_user(
        username,
        STUDENT_PASSWORD,
        first,
        last,
        f"{username}@students.test",
        is_student=True,
    )

    student, _ = StudentProfile.objects.get_or_create(
        user=user,
    )

    student.student_id = student_id
    student.parent = parents[parent_username]
    student.grade = "Grade 7"
    student.date_of_birth = date(2013, 3, 15)
    student.address = "Nairobi, Kenya"
    student.status = "active"
    student.save()

    students[username] = student


print("✓ Users and profiles created")


# ============================================================
# 5. GRADES
# ============================================================

grade7, _ = GradeLevel.objects.get_or_create(
    school=school,
    name="Grade 7",
    defaults={"order": 7},
)

grade8, _ = GradeLevel.objects.get_or_create(
    school=school,
    name="Grade 8",
    defaults={"order": 8},
)


# ============================================================
# 6. STREAMS
# ============================================================

streams = {}

stream_data = [
    ("Grade 7", grade7, "North"),
    ("Grade 7", grade7, "South"),
    ("Grade 8", grade8, "North"),
    ("Grade 8", grade8, "South"),
]

homeroom_map = {
    "Grade 7 North": teachers["teacher.john"],
    "Grade 7 South": teachers["teacher.mary"],
    "Grade 8 North": teachers["teacher.peter"],
    "Grade 8 South": teachers["teacher.grace"],
}

for label, grade, code in stream_data:

    key = f"{label} {code}"

    stream, _ = Stream.objects.get_or_create(
        school=school,
        grade=grade,
        code=code,
        year=academic_year,
    )

    stream.homeroom_teacher = homeroom_map[key]
    stream.save()

    streams[key] = stream


# ============================================================
# 7. SUBJECTS
# ============================================================

subject_data = [
    ("Mathematics", "MATH"),
    ("English", "ENG"),
    ("Science", "SCI"),
    ("Social Studies", "SST"),
    ("Computer Studies", "ICT"),
    ("Kiswahili", "KIS"),
]

subjects = {}

for name, code in subject_data:

    subject, _ = Subject.objects.get_or_create(
        school=school,
        name=name,
        short_code=code,
    )

    subjects[code] = subject


print("✓ School structure created")


# ============================================================
# 8. STUDENT ENROLLMENT
# ============================================================

student_streams = {
    "student.brian": streams["Grade 7 North"],
    "student.alice": streams["Grade 7 North"],
    "student.kevin": streams["Grade 7 South"],
    "student.sharon": streams["Grade 7 South"],
    "student.brian2": streams["Grade 8 North"],
    "student.emily": streams["Grade 8 North"],
    "student.daniel": streams["Grade 8 South"],
    "student.lucy": streams["Grade 8 South"],
}

for username, stream in student_streams.items():

    student = students[username]

    student.stream = stream
    student.grade = stream.grade.name
    student.save()

    Enrollment.objects.get_or_create(
        student=student,
        stream=stream,
        year=academic_year,
    )


# ============================================================
# 9. PARENT ↔ STUDENT MANY-TO-MANY
# ============================================================

parent_children = {
    "parent.james": [
        "student.brian",
        "student.alice",
    ],
    "parent.mary": [
        "student.kevin",
        "student.sharon",
    ],
    "parent.david": [
        "student.brian2",
        "student.emily",
    ],
    "parent.susan": [
        "student.daniel",
        "student.lucy",
    ],
}

for parent_username, child_list in parent_children.items():

    parent_profile = ParentProfile.objects.get(
        user=parents[parent_username]
    )

    parent_profile.students.clear()

    for student_username in child_list:
        parent_profile.students.add(
            students[student_username]
        )


# ============================================================
# 10. TEACHER ASSIGNMENTS
# ============================================================

assignment_data = [
    ("teacher.john", "MATH", "Grade 7 North"),
    ("teacher.john", "SCI", "Grade 7 North"),

    ("teacher.mary", "ENG", "Grade 7 South"),
    ("teacher.mary", "KIS", "Grade 7 South"),

    ("teacher.peter", "MATH", "Grade 8 North"),
    ("teacher.peter", "ICT", "Grade 8 North"),

    ("teacher.grace", "ENG", "Grade 8 South"),
    ("teacher.grace", "SST", "Grade 8 South"),

    # Extra assignments
    ("teacher.john", "ICT", "Grade 7 North"),
    ("teacher.mary", "SCI", "Grade 7 South"),
    ("teacher.peter", "SCI", "Grade 8 North"),
    ("teacher.grace", "MATH", "Grade 8 South"),
]

for teacher_username, subject_code, stream_key in assignment_data:

    TeacherAssignment.objects.get_or_create(
        teacher=teachers[teacher_username],
        subject=subjects[subject_code],
        stream=streams[stream_key],
        term=terms["Term 1"],
    )


# ============================================================
# 11. TEACHER RECORDS
# ============================================================

teacher_records = {}

specializations = {
    "teacher.john": subjects["MATH"],
    "teacher.mary": subjects["ENG"],
    "teacher.peter": subjects["ICT"],
    "teacher.grace": subjects["SCI"],
}

for username, teacher in teachers.items():

    record, _ = TeacherRecord.objects.get_or_create(
        user=teacher,
        defaults={
            "full_name": teacher.get_full_name(),
            "phone": "+254700100000",
            "email": teacher.email,
            "gender": "M" if username in [
                "teacher.john",
                "teacher.peter",
            ] else "F",
            "qualification": "Bachelor of Education",
            "specialization": specializations[username],
            "employment_date": date(2022, 1, 10),
            "status": "active",
        },
    )

    record.full_name = teacher.get_full_name()
    record.specialization = specializations[username]
    record.save()

    teacher_records[username] = record


# ============================================================
# 12. TIMETABLE
# ============================================================

timetable_data = [
    ("Grade 7 North", "Mon", time(8, 0), time(9, 0), "MATH", "teacher.john", "Room 7"),
    ("Grade 7 North", "Mon", time(9, 0), time(10, 0), "SCI", "teacher.john", "Lab 1"),
    ("Grade 7 North", "Tue", time(8, 0), time(9, 0), "ICT", "teacher.john", "Computer Lab"),
    ("Grade 7 North", "Wed", time(10, 0), time(11, 0), "ENG", "teacher.mary", "Room 7"),

    ("Grade 7 South", "Mon", time(8, 0), time(9, 0), "ENG", "teacher.mary", "Room 8"),
    ("Grade 7 South", "Tue", time(9, 0), time(10, 0), "KIS", "teacher.mary", "Room 8"),
    ("Grade 7 South", "Wed", time(8, 0), time(9, 0), "SCI", "teacher.mary", "Lab 1"),

    ("Grade 8 North", "Mon", time(8, 0), time(9, 0), "MATH", "teacher.peter", "Room 9"),
    ("Grade 8 North", "Tue", time(10, 0), time(11, 0), "ICT", "teacher.peter", "Computer Lab"),
    ("Grade 8 North", "Thu", time(8, 0), time(9, 0), "SCI", "teacher.peter", "Lab 1"),

    ("Grade 8 South", "Mon", time(9, 0), time(10, 0), "ENG", "teacher.grace", "Room 10"),
    ("Grade 8 South", "Tue", time(8, 0), time(9, 0), "SST", "teacher.grace", "Room 10"),
    ("Grade 8 South", "Fri", time(9, 0), time(10, 0), "MATH", "teacher.grace", "Room 10"),
]

for stream_key, day, start, end, subject_code, teacher_username, room in timetable_data:

    Timetable.objects.get_or_create(
        stream=streams[stream_key],
        day_of_week=day,
        start_time=start,
        end_time=end,
        defaults={
            "subject": subjects[subject_code],
            "teacher_record": teacher_records[teacher_username],
            "room": room,
        },
    )


# ============================================================
# 13. QUIZZES + QUESTIONS
# ============================================================

quiz1 = create_quiz(
    "Grade 7 Mathematics - Algebra Basics",
    "A short assessment covering basic algebra concepts.",
    teachers["teacher.john"],
    [
        {
            "text": "What is 2 + 3?",
            "A": "4",
            "B": "5",
            "C": "6",
            "D": "7",
            "correct": "B",
        },
        {
            "text": "If x + 4 = 10, what is x?",
            "A": "4",
            "B": "5",
            "C": "6",
            "D": "7",
            "correct": "C",
        },
        {
            "text": "What is 5 × 6?",
            "A": "11",
            "B": "20",
            "C": "25",
            "D": "30",
            "correct": "D",
        },
        {
            "text": "What is half of 20?",
            "A": "5",
            "B": "10",
            "C": "15",
            "D": "20",
            "correct": "B",
        },
    ],
)

quiz2 = create_quiz(
    "Grade 7 Science - Matter",
    "Test your understanding of matter and its states.",
    teachers["teacher.john"],
    [
        {
            "text": "Which state of matter has a fixed shape?",
            "A": "Solid",
            "B": "Liquid",
            "C": "Gas",
            "D": "Plasma",
            "correct": "A",
        },
        {
            "text": "Water changes into ice through what process?",
            "A": "Melting",
            "B": "Freezing",
            "C": "Evaporation",
            "D": "Condensation",
            "correct": "B",
        },
        {
            "text": "Which state takes the shape of its container?",
            "A": "Solid",
            "B": "Liquid",
            "C": "Crystal",
            "D": "None",
            "correct": "B",
        },
    ],
)

quiz3 = create_quiz(
    "Grade 8 Computer Studies - Hardware",
    "Basic computer hardware assessment.",
    teachers["teacher.peter"],
    [
        {
            "text": "Which device is used to type text?",
            "A": "Monitor",
            "B": "Printer",
            "C": "Keyboard",
            "D": "Speaker",
            "correct": "C",
        },
        {
            "text": "Which component performs calculations?",
            "A": "CPU",
            "B": "Mouse",
            "C": "Monitor",
            "D": "Keyboard",
            "correct": "A",
        },
        {
            "text": "Which device displays information?",
            "A": "Keyboard",
            "B": "Monitor",
            "C": "Scanner",
            "D": "Mouse",
            "correct": "B",
        },
    ],
)

quiz4 = create_quiz(
    "Grade 8 English - Grammar",
    "Grammar and sentence structure assessment.",
    teachers["teacher.grace"],
    [
        {
            "text": "Which word is a noun?",
            "A": "Run",
            "B": "Beautiful",
            "C": "School",
            "D": "Quickly",
            "correct": "C",
        },
        {
            "text": "Choose the correct sentence.",
            "A": "She go to school.",
            "B": "She goes to school.",
            "C": "She going school.",
            "D": "She gone school.",
            "correct": "B",
        },
        {
            "text": "What is the opposite of 'early'?",
            "A": "Fast",
            "B": "Late",
            "C": "Soon",
            "D": "Quick",
            "correct": "B",
        },
    ],
)


# ============================================================
# 14. ASSIGN QUIZZES TO STREAMS
# ============================================================

quiz_assignments = [
    (teachers["teacher.john"], quiz1, streams["Grade 7 North"]),
    (teachers["teacher.john"], quiz2, streams["Grade 7 North"]),
    (teachers["teacher.peter"], quiz3, streams["Grade 8 North"]),
    (teachers["teacher.grace"], quiz4, streams["Grade 8 South"]),
]

for teacher, quiz, stream in quiz_assignments:

    TeacherQuiz.objects.get_or_create(
        quiz=quiz,
        defaults={
            "teacher": teacher,
            "stream": stream,
        },
    )


# ============================================================
# 15. QUIZ RESULTS
# ============================================================

# Delete existing seeded results for clean reruns.
QuizResult.objects.filter(
    quiz__in=[quiz1, quiz2, quiz3, quiz4]
).delete()


def create_result(student, quiz, selected_answers, approved=True):

    questions = list(quiz.questions.all())

    score = 0

    for question, selected in zip(questions, selected_answers):

        if selected == question.correct_answer:
            score += 1

    result = QuizResult.objects.create(
        student=student,
        quiz=quiz,
        score=score,
        is_approved=approved,
    )

    for question, selected in zip(questions, selected_answers):

        Answer.objects.create(
            result=result,
            question=question,
            selected_option=selected,
            is_correct=(selected == question.correct_answer),
        )

    return result


create_result(
    students["student.brian"],
    quiz1,
    ["B", "C", "D", "B"],
    approved=True,
)

create_result(
    students["student.alice"],
    quiz1,
    ["B", "A", "D", "C"],
    approved=False,
)

create_result(
    students["student.kevin"],
    quiz2,
    ["A", "B", "B"],
    approved=True,
)

create_result(
    students["student.sharon"],
    quiz2,
    ["A", "C", "B"],
    approved=False,
)

create_result(
    students["student.brian2"],
    quiz3,
    ["C", "A", "B"],
    approved=True,
)

create_result(
    students["student.emily"],
    quiz3,
    ["C", "B", "B"],
    approved=True,
)

create_result(
    students["student.daniel"],
    quiz4,
    ["C", "B", "B"],
    approved=True,
)

create_result(
    students["student.lucy"],
    quiz4,
    ["A", "B", "C"],
    approved=False,
)


# ============================================================
# 16. ANNOUNCEMENTS
# ============================================================

announcement_data = [
    (
        "Welcome to the New Academic Year",
        "Welcome students, parents and teachers to the 2026/2027 academic year. We wish everyone a successful year.",
    ),
    (
        "Parent-Teacher Meeting",
        "The next parent-teacher meeting will be held this Friday. Parents are encouraged to attend.",
    ),
    (
        "Continuous Assessment Tests",
        "Students are reminded to prepare for the upcoming continuous assessment tests.",
    ),
]

for title, body in announcement_data:

    Announcement.objects.update_or_create(
        title=title,
        defaults={
            "body": body,
            "posted_by": admin_user,
            "is_published": True,
        },
    )


# ============================================================
# 17. COMMUNICATION MESSAGES
# ============================================================

# Remove only messages created by these seeded teachers.
Message.objects.filter(
    sender__in=list(teachers.values())
).delete()


message1 = Message.objects.create(
    sender=teachers["teacher.john"],
    scope="stream",
    stream=streams["Grade 7 North"],
    title="Mathematics Assignment",
    body="Please complete the algebra exercises before Friday.",
)

message2 = Message.objects.create(
    sender=teachers["teacher.peter"],
    scope="stream",
    stream=streams["Grade 8 North"],
    title="Computer Studies Reminder",
    body="Remember to revise the computer hardware notes before the next lesson.",
)

message3 = Message.objects.create(
    sender=teachers["teacher.grace"],
    scope="student",
    student=students["student.lucy"],
    title="English Performance",
    body="Please continue practicing grammar exercises.",
)


# ============================================================
# 18. DELIVER MESSAGES TO PARENTS
# ============================================================

pm1 = ParentMessage.objects.create(
    message=message1,
    parent=parents["parent.james"],
    is_read=False,
)

pm2 = ParentMessage.objects.create(
    message=message2,
    parent=parents["parent.david"],
    is_read=True,
)

pm3 = ParentMessage.objects.create(
    message=message3,
    parent=parents["parent.susan"],
    is_read=False,
)


# ============================================================
# 19. MESSAGE REPLIES
# ============================================================

MessageReply.objects.create(
    parent_message=pm1,
    sender=parents["parent.james"],
    body="Thank you. I will make sure Brian completes the assignment.",
)

MessageReply.objects.create(
    parent_message=pm2,
    sender=parents["parent.david"],
    body="Received. Thank you for the reminder.",
)


# ============================================================
# 20. RESOURCE FILES
# ============================================================

resource_directory = Path(settings.MEDIA_ROOT) / "test_resources"
resource_directory.mkdir(parents=True, exist_ok=True)


def create_dummy_file(filename, content):

    path = resource_directory / filename

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return path


resource_data = [
    (
        "Grade 7 Mathematics Notes",
        "math_notes.txt",
        "Mathematics revision notes - Algebra Basics.",
        teachers["teacher.john"],
        "students",
    ),
    (
        "Science Matter Revision",
        "science_notes.txt",
        "Science revision material - States of Matter.",
        teachers["teacher.john"],
        "all",
    ),
    (
        "Computer Hardware Notes",
        "computer_hardware.txt",
        "Computer Studies notes - Hardware.",
        teachers["teacher.peter"],
        "students",
    ),
    (
        "Teacher Planning Document",
        "teacher_planning.txt",
        "Teacher planning material for Term 1.",
        teachers["teacher.mary"],
        "teachers",
    ),
]

for title, filename, content, uploader, visibility in resource_data:

    existing = Resource.objects.filter(
        title=title,
        uploader=uploader,
    ).first()

    if existing:
        resource = existing
    else:
        resource = Resource(
            title=title,
            description=f"Test resource: {title}",
            uploader=uploader,
            visibility=visibility,
            download_count=0,
        )

    path = create_dummy_file(filename, content)

    with open(path, "rb") as file_handle:
        resource.file.save(
            filename,
            File(file_handle),
            save=False,
        )

    resource.description = f"Test resource: {title}"
    resource.visibility = visibility
    resource.save()


# ============================================================
# 21. SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("TEST DATA CREATED SUCCESSFULLY")
print("=" * 70)

print("\nSCHOOL")
print("  Bright Future Academy")

print("\nADMIN")
print("  Username : schooladmin")
print("  Password : Admin@123")

print("\nTEACHERS")
for username in teachers:
    print(f"  {username:<20} Password: {TEACHER_PASSWORD}")

print("\nSTUDENTS")
for username in students:
    print(f"  {username:<20} Password: {STUDENT_PASSWORD}")

print("\nPARENTS")
for username in parents:
    print(f"  {username:<20} Password: {PARENT_PASSWORD}")

print("\nRELATIONSHIPS")
print("  ✓ Students linked to parents")
print("  ✓ Students assigned to streams")
print("  ✓ Students enrolled in academic year")
print("  ✓ Homeroom teachers assigned")
print("  ✓ Teachers assigned to subjects and streams")
print("  ✓ Timetables created")
print("  ✓ Quizzes created")
print("  ✓ Quizzes assigned to streams")
print("  ✓ Quiz questions created")
print("  ✓ Quiz results created")
print("  ✓ Approved and unapproved results created")
print("  ✓ Announcements created")
print("  ✓ Parent messages created")
print("  ✓ Message replies created")
print("  ✓ Learning resources created")

print("\n" + "=" * 70)
print("READY FOR TESTING")
print("=" * 70)