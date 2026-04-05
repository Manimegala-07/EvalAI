"""
Full test seed script — creates:
- 1 teacher
- 5 students
- 10 questions with difficulty, blooms_level, co_mapping
- 1 test with CO outcomes
- Student submissions with varied answers (good, average, poor)
- Evaluates all submissions so analytics charts show data

Run: python -m app.seed_test
"""

import json
from app.db.database import SessionLocal, engine, Base
from app.db.models import User, Question, Test, TestQuestion, Submission, Answer
from app.auth.security import hash_password
from app.services.scoring_service import ScoringService
from app.services.llm_service import LLMService
from app.services.translation_service import detect_language

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("🌱 Starting full test seed...")

# ── Clean existing test data ───────────────────────────────────
print("🧹 Cleaning old seed data...")
for model in [Answer, Submission, TestQuestion, Test, Question, User]:
    db.query(model).delete()
db.commit()

# ── Users ──────────────────────────────────────────────────────
print("👤 Creating users...")
teacher = User(name="Teacher A", email="teacher1@test.com", password=hash_password("1234"), role="teacher", institution="Anna University")

students = [
    User(name="Arun Kumar",    email="stu1@test.com", password=hash_password("1234"), role="student", institution="Anna University"),
    User(name="Priya Sharma",  email="stu2@test.com", password=hash_password("1234"), role="student", institution="Anna University"),
    User(name="Rahul Singh",   email="stu3@test.com", password=hash_password("1234"), role="student", institution="Anna University"),
    User(name="Divya Nair",    email="stu4@test.com", password=hash_password("1234"), role="student", institution="Anna University"),
    User(name="Karthik Raja",  email="stu5@test.com", password=hash_password("1234"), role="student", institution="Anna University"),
]

db.add(teacher)
db.add_all(students)
db.flush()

# ── Questions ──────────────────────────────────────────────────
print("❓ Creating questions...")

CO_OUTCOMES = {
    "CO1": "Knowledge & Recall — Recall facts, definitions, and basic concepts",
    "CO2": "Comprehension — Explain and describe concepts in own words",
    "CO3": "Application — Apply concepts to solve problems",
    "CO4": "Analysis — Break down, compare, and examine relationships",
    "CO5": "Evaluation — Justify, assess, and make judgments",
    "CO6": "Creation — Design, construct, or produce something new",
}

questions_data = [
    {
        "text": "What is a variable in Java?",
        "model_answer": "A variable in Java is a named memory location that stores a value. It must be declared with a data type before use. Variables can store different types of data such as integers, strings, and decimals.",
        "difficulty": 1, "blooms_level": "L1", "co_mapping": "CO1",
        "student_answers": [
            "A variable in Java is a named memory location that stores a value. It must be declared with a data type before use. Variables can hold integers, strings, and other data types.",
            "A variable stores a value in memory and has a data type. We declare it before using it in the program.",
            "Variable is used to store values in Java program.",
            "A variable is a name given to store something.",
            "Variable is a function that returns values in Java.",
        ]
    },
    {
        "text": "What is the difference between int and double in Java?",
        "model_answer": "int stores whole numbers without decimal points while double stores numbers with decimal points. int uses 4 bytes of memory and double uses 8 bytes. int is used for counting while double is used for precise calculations.",
        "difficulty": 2, "blooms_level": "L2", "co_mapping": "CO1",
        "student_answers": [
            "int stores whole numbers without decimals while double stores numbers with decimal points. int uses 4 bytes and double uses 8 bytes of memory. int is for counting and double is for precise calculations.",
            "int is for whole numbers and double is for decimal numbers. double takes more memory than int.",
            "int and double are data types. int is for numbers and double is for bigger numbers.",
            "int and double both store numbers in Java.",
            "int is used for text and double is used for numbers in Java.",
        ]
    },
    {
        "text": "Explain how a for loop works in Java.",
        "model_answer": "A for loop in Java executes a block of code repeatedly for a fixed number of times. It has three parts: initialization which sets the starting value, condition which checks if the loop should continue, and increment which updates the counter. The loop stops when the condition becomes false.",
        "difficulty": 2, "blooms_level": "L2", "co_mapping": "CO2",
        "student_answers": [
            "A for loop executes a block of code repeatedly for a fixed number of times. It has three parts: initialization sets the starting value, condition checks if loop should continue, and increment updates the counter. Loop stops when condition is false.",
            "For loop repeats code. It has init, condition and increment parts. It stops when condition becomes false.",
            "For loop is used to repeat something in Java for a certain number of times.",
            "For loop repeats code many times in Java.",
            "For loop is used to declare variables in Java.",
        ]
    },
    {
        "text": "How does exception handling work in Java?",
        "model_answer": "Exception handling in Java uses try, catch, and finally blocks. Code that may throw an exception is placed in the try block. If an exception occurs, the catch block handles it and prevents the program from crashing. The finally block always executes regardless of whether an exception occurred.",
        "difficulty": 4, "blooms_level": "L3", "co_mapping": "CO3",
        "student_answers": [
            "Exception handling uses try, catch, and finally blocks. Code that may throw exception goes in try block. If exception occurs catch block handles it and prevents crash. Finally block always executes regardless of exception.",
            "Exception handling uses try and catch. Try block has risky code and catch handles the exception. Finally always runs.",
            "Exception handling is used to handle errors in Java using try catch blocks.",
            "Try catch is used for exceptions in Java.",
            "Exception handling stops the program from running when there is an error.",
        ]
    },
    {
        "text": "What is the difference between ArrayList and LinkedList in Java?",
        "model_answer": "ArrayList uses a dynamic array to store elements and provides fast random access using index. LinkedList uses a doubly linked list structure and provides fast insertion and deletion. ArrayList is better for frequent access operations while LinkedList is better for frequent insertions and deletions.",
        "difficulty": 4, "blooms_level": "L4", "co_mapping": "CO4",
        "student_answers": [
            "ArrayList uses dynamic array for fast random access using index. LinkedList uses doubly linked list for fast insertion and deletion. ArrayList is better for access operations while LinkedList is better for insertions and deletions.",
            "ArrayList is array based and LinkedList is node based. ArrayList is faster for access and LinkedList is faster for insert and delete.",
            "ArrayList and LinkedList are both lists. ArrayList uses array and LinkedList uses links between nodes.",
            "ArrayList and LinkedList store data differently in Java.",
            "ArrayList is faster than LinkedList for all operations in Java.",
        ]
    },
    {
        "text": "How would you use an array to store and calculate the average of 5 student marks?",
        "model_answer": "To store 5 student marks we declare an integer array of size 5. We then assign marks to each index from 0 to 4. To calculate average we use a for loop to sum all elements and divide by 5. This gives the average mark of all students.",
        "difficulty": 3, "blooms_level": "L3", "co_mapping": "CO3",
        "student_answers": [
            "We declare an integer array of size 5 to store marks. Assign marks to each index from 0 to 4. Use for loop to sum all elements and divide by 5 to get average mark.",
            "Create an array of size 5, store marks in it, loop through to add all marks and divide by 5 for average.",
            "Use array to store marks and loop to calculate sum then divide by number of students.",
            "Store marks in array and add them to get average.",
            "Use a variable to store marks and calculate average by adding all.",
        ]
    },
    {
        "text": "Compare the performance of bubble sort and merge sort algorithms.",
        "model_answer": "Bubble sort has a time complexity of O(n²) in worst case making it inefficient for large datasets. Merge sort has a time complexity of O(n log n) making it much more efficient. Bubble sort is simple to implement but slow while merge sort is faster but requires extra memory space for merging.",
        "difficulty": 5, "blooms_level": "L4", "co_mapping": "CO4",
        "student_answers": [
            "Bubble sort has O(n²) time complexity making it inefficient for large data. Merge sort has O(n log n) which is much better. Bubble sort is simple but slow while merge sort is faster but needs extra memory.",
            "Bubble sort is slower with O(n²) and merge sort is faster with O(n log n). Merge sort needs more memory.",
            "Bubble sort compares adjacent elements and merge sort divides and merges. Merge sort is faster.",
            "Bubble sort is slow and merge sort is fast for sorting.",
            "Bubble sort is better than merge sort because it is simpler to code.",
        ]
    },
    {
        "text": "Evaluate whether using a static variable is a good practice in Java. Justify your answer.",
        "model_answer": "Static variables are shared across all instances of a class which can be useful for constants or counters. However overusing static variables is bad practice because it creates tight coupling, makes testing difficult, and can cause unexpected behavior in multithreaded applications. Static variables should be used sparingly and only when truly needed.",
        "difficulty": 5, "blooms_level": "L5", "co_mapping": "CO5",
        "student_answers": [
            "Static variables are shared across all instances which is useful for constants and counters. But overusing them is bad practice because it creates tight coupling, makes testing hard, and causes issues in multithreaded apps. They should be used sparingly only when needed.",
            "Static variables are useful for shared data but can cause problems in multithreading. They should be used carefully.",
            "Static variables are class level variables shared by all objects. They are useful sometimes but can cause problems.",
            "Static variables are used when we need to share data between objects in Java.",
            "Static variables are always good to use because they save memory in Java.",
        ]
    },
    {
        "text": "What is a string in Java and what makes it immutable?",
        "model_answer": "A String in Java is a sequence of characters and is an object of the String class. Strings are immutable meaning once created their value cannot be changed. When you modify a string Java creates a new string object instead of changing the original. This immutability makes strings thread safe and allows string pooling for memory efficiency.",
        "difficulty": 3, "blooms_level": "L2", "co_mapping": "CO2",
        "student_answers": [
            "String in Java is a sequence of characters and object of String class. Strings are immutable meaning their value cannot be changed after creation. Modifying a string creates a new object. Immutability makes strings thread safe and allows string pooling.",
            "String is a sequence of characters. It is immutable so we cannot change it after creation. Java creates new string when we modify.",
            "String stores text in Java. It is immutable which means it cannot be changed.",
            "String is used to store words and sentences in Java.",
            "String is mutable in Java and can be changed anytime using methods.",
        ]
    },
    {
        "text": "Design a simple class in Java to represent a Student with name, age, and grade attributes.",
        "model_answer": "A Student class in Java should have private attributes name, age, and grade to follow encapsulation. We add a constructor to initialize these values and getter and setter methods to access and modify them. This design follows object oriented principles of encapsulation and abstraction making the code maintainable and reusable.",
        "difficulty": 5, "blooms_level": "L6", "co_mapping": "CO6",
        "student_answers": [
            "Student class should have private attributes name, age, and grade for encapsulation. Add constructor to initialize values and getter setter methods to access them. This follows OOP principles of encapsulation and abstraction making code maintainable.",
            "Create Student class with name, age, grade as private fields. Add constructor and getters setters. This follows encapsulation principle.",
            "Student class has name, age, grade attributes. We use constructor to set values and methods to get them.",
            "Make a class Student with name age grade and add methods to get and set values.",
            "Student class needs name and age variables and a method to print them.",
        ]
    },
]

questions = []
for qd in questions_data:
    q = Question(
        text=qd["text"],
        model_answer=qd["model_answer"],
        teacher_id=teacher.id,
        difficulty=qd["difficulty"],
        blooms_level=qd["blooms_level"],
    )
    db.add(q)
    questions.append((q, qd))

db.flush()

# ── Test ───────────────────────────────────────────────────────
print("📋 Creating test...")
test = Test(
    title="Java Programming — Unit Test 1",
    teacher_id=teacher.id,
    co_outcomes=CO_OUTCOMES,
)
db.add(test)
db.flush()

# Add all questions to test with CO mapping
for q, qd in questions:
    tq = TestQuestion(
        test_id=test.id,
        question_id=q.id,
        max_score=10,
        co_mapping=qd["co_mapping"],
    )
    db.add(tq)

db.flush()

# ── Submissions ────────────────────────────────────────────────
print("📝 Creating submissions...")
submissions = []
for i, student in enumerate(students):
    sub = Submission(student_id=student.id, test_id=test.id, status="pending")
    db.add(sub)
    db.flush()

    for j, (q, qd) in enumerate(questions):
        ans = Answer(
            submission_id=sub.id,
            question_id=q.id,
            student_answer=qd["student_answers"][i],
            score=0.0,
            feedback="Pending evaluation",
        )
        db.add(ans)

    submissions.append(sub)

db.commit()
print(f"✅ Created {len(submissions)} submissions")

# ── Evaluate all submissions ───────────────────────────────────
print("⚡ Evaluating all submissions (this may take a few minutes)...")
scorer = ScoringService()
llm    = LLMService()

for sub_idx, sub in enumerate(submissions):
    student = students[sub_idx]
    print(f"\n  📊 Evaluating {student.name}...")
    answers     = db.query(Answer).filter(Answer.submission_id == sub.id).all()
    total_score = 0.0

    for ans in answers:
        question = db.query(Question).filter(Question.id == ans.question_id).first()
        mapping  = db.query(TestQuestion).filter(TestQuestion.test_id == test.id, TestQuestion.question_id == ans.question_id).first()
        max_score = mapping.max_score if mapping else 10

        student_text = (ans.student_answer or "").strip()
        if not student_text or len(student_text.split()) < 3:
            ans.score = 0.0
            ans.feedback = "No meaningful answer provided."
            continue

        lang_info     = detect_language(student_text)
        detected_lang = lang_info.get("lang_code", "en")

        result = scorer.grade_single(question.model_answer, student_text, max_score=max_score, skip_translation=False)
        score           = result["score"]
        concept_results = result["concept_results"]
        total_score    += score

        covered = [c["concept"] for c in concept_results if c["status"] == "matched"]
        partial = [c["concept"] for c in concept_results if c["status"] == "partial"]
        missing = [c["concept"] for c in concept_results if c["status"] == "missing"]
        wrong   = [c["concept"] for c in concept_results if c["status"] == "wrong"]
        concept_details = [{"concept": c["concept"], "status": c["status"], "coverage": c["coverage"], "covered_kws": c.get("covered_kws", []), "missing_kws": c.get("missing_kws", [])} for c in concept_results]

        prompt = f"""You are an academic evaluator giving feedback to a student.
Question: {question.text}
Student Answer: {student_text}
Score: {score} / {max_score}
Write 2-3 sentences of constructive feedback."""
        try:
            feedback = llm.model.generate_content(prompt).text
        except Exception:
            feedback = f"Score: {score}/{max_score}. {'Good coverage of: ' + ', '.join(covered[:2]) + '.' if covered else ''} {'Missed: ' + ', '.join(missing[:2]) + '.' if missing else ''}"

        ans.score            = score
        ans.similarity       = result["similarity"]
        ans.entailment       = result["entailment"]
        ans.coverage         = result["coverage"]
        ans.length_ratio     = result["length_ratio"]
        ans.confidence       = result["confidence"]
        ans.rf_score         = result.get("rf_score")
        ans.feedback         = feedback
        ans.concept_data     = {"covered": covered, "partial": partial, "missing": missing, "wrong": wrong, "concept_details": concept_details, "coverage": result["coverage"], "wrong_ratio": result["wrong_ratio"], "status": "strong" if result["coverage"] > 0.65 else "partial" if result["coverage"] > 0.35 else "weak"}
        ans.sentence_heatmap = result["sentence_heatmap"]

        print(f"     Q{questions.index((question, next(qd for q2, qd in questions if q2.id == question.id))) + 1 if False else ''}: {score:.1f}/{max_score}")

    sub.total_score = round(total_score, 2)
    sub.status      = "evaluated"
    db.commit()
    print(f"  ✅ {student.name}: {sub.total_score} / {len(questions) * 10}")

db.commit()

print("\n" + "="*60)
print("✅ SEED COMPLETE!")
print("="*60)
print(f"  Teacher  : teacher1@test.com / 1234")
print(f"  Students : stu1@test.com to stu5@test.com / 1234")
print(f"  Test     : Java Programming — Unit Test 1")
print(f"  Questions: {len(questions)} questions")
print(f"  Students : {len(students)} students evaluated")
print("="*60)
print("\nNow open Analytics → Select 'Java Programming — Unit Test 1' to see all charts!")
db.close()
