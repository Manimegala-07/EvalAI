"""
Populate Question Bank with 20 Java questions
- English + Tamil reference answers
- Difficulty levels 1-5
- Bloom's taxonomy L1-L6
- CO mapping CO1-CO6

Run: python -m app.populate_questions
"""

from app.db.database import SessionLocal, engine, Base
from app.db.models import Question, User
from app.auth.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Get or create teacher
teacher = db.query(User).filter(User.email == "teacher1@test.com").first()
if not teacher:
    teacher = User(name="Teacher A", email="teacher1@test.com", password=hash_password("1234"), role="teacher", institution="Anna University")
    db.add(teacher)
    db.flush()

questions = [
    # ── CO1 — Knowledge & Recall ───────────────────────────────
    {
        "text": "What is Java?",
        "model_answer": "Java is a high-level, object-oriented programming language developed by Sun Microsystems. It is platform-independent meaning Java programs can run on any operating system using the Java Virtual Machine (JVM). Java is widely used for web, mobile, and enterprise applications.",
        "model_answer_ta": "ஜாவா என்பது Sun Microsystems நிறுவனத்தால் உருவாக்கப்பட்ட உயர்நிலை, பொருள்-சார்ந்த நிரலாக்க மொழி. இது தளம்-சுதந்திரமானது, அதாவது ஜாவா நிரல்கள் Java Virtual Machine (JVM) மூலம் எந்த இயக்க முறைமையிலும் இயங்கும். ஜாவா வலை, மொபைல் மற்றும் நிறுவன பயன்பாடுகளுக்கு பரவலாக பயன்படுத்தப்படுகிறது.",
        "difficulty": 1, "blooms_level": "L1", "co_mapping": "CO1",
    },
    {
        "text": "What is a variable in Java?",
        "model_answer": "A variable in Java is a named memory location that stores a value. It must be declared with a data type before use. Variables can store integers, strings, decimals, and other data types.",
        "model_answer_ta": "ஜாவாவில் மாறி என்பது ஒரு மதிப்பை சேமிக்கும் பெயரிடப்பட்ட நினைவக இடம். பயன்படுத்துவதற்கு முன் தரவு வகையுடன் அறிவிக்கப்பட வேண்டும். மாறிகள் முழு எண்கள், சரங்கள், தசம எண்கள் மற்றும் பிற தரவு வகைகளை சேமிக்கலாம்.",
        "difficulty": 1, "blooms_level": "L1", "co_mapping": "CO1",
    },
    {
        "text": "What are the primitive data types in Java?",
        "model_answer": "Java has eight primitive data types: byte, short, int, long, float, double, char, and boolean. int stores whole numbers, double stores decimal numbers, char stores a single character, and boolean stores true or false values.",
        "model_answer_ta": "ஜாவாவில் எட்டு ஆதிம தரவு வகைகள் உள்ளன: byte, short, int, long, float, double, char மற்றும் boolean. int முழு எண்களை சேமிக்கிறது, double தசம எண்களை சேமிக்கிறது, char ஒரு எழுத்தை சேமிக்கிறது, boolean true அல்லது false மதிப்புகளை சேமிக்கிறது.",
        "difficulty": 1, "blooms_level": "L1", "co_mapping": "CO1",
    },
    {
        "text": "What is the difference between int and double in Java?",
        "model_answer": "int stores whole numbers without decimal points while double stores numbers with decimal points. int uses 4 bytes of memory and double uses 8 bytes. int is used for counting while double is used for precise calculations involving decimals.",
        "model_answer_ta": "int என்பது தசம புள்ளிகள் இல்லாத முழு எண்களை சேமிக்கிறது, double என்பது தசம புள்ளிகளுடன் எண்களை சேமிக்கிறது. int 4 bytes நினைவகம் பயன்படுத்துகிறது, double 8 bytes பயன்படுத்துகிறது. int எண்ணிக்கைக்கும் double தசம கணக்கீடுகளுக்கும் பயன்படுகிறது.",
        "difficulty": 2, "blooms_level": "L2", "co_mapping": "CO1",
    },

    # ── CO2 — Comprehension ────────────────────────────────────
    {
        "text": "Explain how a for loop works in Java.",
        "model_answer": "A for loop in Java executes a block of code repeatedly for a fixed number of times. It has three parts: initialization which sets the starting value, condition which checks if the loop should continue, and increment which updates the counter. The loop stops when the condition becomes false.",
        "model_answer_ta": "ஜாவாவில் for loop ஒரு குறிப்பிட்ட எண்ணிக்கையிலான முறைகளுக்கு குறியீட்டு தொகுதியை மீண்டும் மீண்டும் இயக்குகிறது. இதில் மூன்று பகுதிகள் உள்ளன: துவக்க மதிப்பை அமைக்கும் துவக்கம், loop தொடர வேண்டுமா என சரிபார்க்கும் நிபந்தனை, மற்றும் கவுண்டரை புதுப்பிக்கும் அதிகரிப்பு. நிபந்தனை பொய்யாகும்போது loop நிறுத்தப்படும்.",
        "difficulty": 2, "blooms_level": "L2", "co_mapping": "CO2",
    },
    {
        "text": "What is a string in Java and what makes it immutable?",
        "model_answer": "A String in Java is a sequence of characters and is an object of the String class. Strings are immutable meaning once created their value cannot be changed. When you modify a string Java creates a new string object instead of changing the original. This immutability makes strings thread safe and allows string pooling for memory efficiency.",
        "model_answer_ta": "ஜாவாவில் String என்பது எழுத்துகளின் வரிசை மற்றும் String வகுப்பின் ஒரு பொருள். Strings மாறாதவை, அதாவது உருவாக்கப்பட்டதும் அதன் மதிப்பை மாற்ற முடியாது. ஒரு string ஐ மாற்றும்போது ஜாவா அசல் string ஐ மாற்றாமல் புதிய string பொருளை உருவாக்குகிறது. இந்த மாறாத தன்மை strings ஐ thread safe ஆக்குகிறது.",
        "difficulty": 3, "blooms_level": "L2", "co_mapping": "CO2",
    },
    {
        "text": "Explain the difference between while loop and do-while loop in Java.",
        "model_answer": "A while loop checks the condition before executing the loop body so it may not execute at all if the condition is false initially. A do-while loop executes the loop body at least once before checking the condition. The key difference is that do-while guarantees at least one execution.",
        "model_answer_ta": "while loop உடல் இயக்கும் முன் நிபந்தனையை சரிபார்க்கிறது, எனவே நிபந்தனை ஆரம்பத்திலேயே பொய்யாக இருந்தால் அது இயங்காமல் போகலாம். do-while loop நிபந்தனையை சரிபார்க்கும் முன் குறைந்தது ஒரு முறையாவது loop உடலை இயக்குகிறது. முக்கிய வேறுபாடு என்னவென்றால் do-while குறைந்தது ஒரு முறை இயக்கத்தை உறுதி செய்கிறது.",
        "difficulty": 3, "blooms_level": "L2", "co_mapping": "CO2",
    },
    {
        "text": "What is an array in Java?",
        "model_answer": "An array in Java is a collection of elements of the same data type stored in contiguous memory locations. It is declared with a fixed size that cannot be changed after creation. Elements are accessed using an index starting from zero. Arrays are useful for storing and processing multiple values of the same type.",
        "model_answer_ta": "ஜாவாவில் அணி என்பது தொடர்ச்சியான நினைவக இடங்களில் சேமிக்கப்பட்ட ஒரே தரவு வகையின் உறுப்புகளின் தொகுப்பு. இது உருவாக்கப்பட்ட பிறகு மாற்ற முடியாத நிலையான அளவுடன் அறிவிக்கப்படுகிறது. உறுப்புகள் பூஜ்ஜியத்திலிருந்து தொடங்கும் குறியீட்டைப் பயன்படுத்தி அணுகப்படுகின்றன.",
        "difficulty": 2, "blooms_level": "L2", "co_mapping": "CO2",
    },

    # ── CO3 — Application ──────────────────────────────────────
    {
        "text": "How would you use an array to store and calculate the average of 5 student marks?",
        "model_answer": "To store 5 student marks we declare an integer array of size 5. We assign marks to each index from 0 to 4. To calculate average we use a for loop to sum all elements and divide the total by 5. This gives the average mark of all students.",
        "model_answer_ta": "5 மாணவர் மதிப்பெண்களை சேமிக்க 5 அளவுள்ள முழு எண் அணியை அறிவிக்கிறோம். 0 முதல் 4 வரையிலான ஒவ்வொரு குறியீட்டிலும் மதிப்பெண்களை ஒதுக்குகிறோம். சராசரியை கணக்கிட அனைத்து உறுப்புகளையும் கூட்ட for loop பயன்படுத்தி மொத்தத்தை 5 ஆல் வகுக்கிறோம்.",
        "difficulty": 3, "blooms_level": "L3", "co_mapping": "CO3",
    },
    {
        "text": "How does exception handling work in Java?",
        "model_answer": "Exception handling in Java uses try, catch, and finally blocks. Code that may throw an exception is placed in the try block. If an exception occurs the catch block handles it and prevents the program from crashing. The finally block always executes regardless of whether an exception occurred and is used for cleanup operations.",
        "model_answer_ta": "ஜாவாவில் விதிவிலக்கு கையாளுதல் try, catch மற்றும் finally தொகுதிகளை பயன்படுத்துகிறது. விதிவிலக்கை எறியக்கூடிய குறியீடு try தொகுதியில் வைக்கப்படுகிறது. விதிவிலக்கு ஏற்பட்டால் catch தொகுதி அதை கையாண்டு நிரல் செயலிழப்பதை தடுக்கிறது. finally தொகுதி விதிவிலக்கு ஏற்பட்டாலும் இல்லாவிட்டாலும் எப்போதும் இயங்கும்.",
        "difficulty": 4, "blooms_level": "L3", "co_mapping": "CO3",
    },
    {
        "text": "How would you use a method in Java to find the maximum of two numbers?",
        "model_answer": "We define a method with return type int that takes two integer parameters. Inside the method we use an if-else statement to compare the two numbers. If the first number is greater we return it otherwise we return the second number. We call this method from the main method by passing two values.",
        "model_answer_ta": "இரண்டு முழு எண் அளவுருக்களை எடுக்கும் int திரும்பும் வகையுடன் ஒரு முறையை வரையறுக்கிறோம். முறைக்குள் இரண்டு எண்களை ஒப்பிட if-else அறிக்கையை பயன்படுத்துகிறோம். முதல் எண் பெரியதாக இருந்தால் அதை திரும்பப் பெறுகிறோம் இல்லையெனில் இரண்டாவது எண்ணை திரும்பப் பெறுகிறோம்.",
        "difficulty": 3, "blooms_level": "L3", "co_mapping": "CO3",
    },

    # ── CO4 — Analysis ─────────────────────────────────────────
    {
        "text": "What is the difference between ArrayList and LinkedList in Java?",
        "model_answer": "ArrayList uses a dynamic array to store elements and provides fast random access with O(1) time complexity. LinkedList uses a doubly linked list structure and provides fast insertion and deletion with O(1) time. ArrayList is better for frequent access operations while LinkedList is better for frequent insertions and deletions at any position.",
        "model_answer_ta": "ArrayList உறுப்புகளை சேமிக்க dynamic array பயன்படுத்தி O(1) நேர சிக்கலுடன் வேகமான random access வழங்குகிறது. LinkedList doubly linked list அமைப்பை பயன்படுத்தி O(1) நேரத்தில் வேகமான செருகல் மற்றும் நீக்கம் வழங்குகிறது. ArrayList அடிக்கடி access செய்வதற்கும் LinkedList அடிக்கடி செருகல் நீக்கத்திற்கும் சிறந்தது.",
        "difficulty": 4, "blooms_level": "L4", "co_mapping": "CO4",
    },
    {
        "text": "Compare bubble sort and merge sort algorithms in Java.",
        "model_answer": "Bubble sort has a time complexity of O(n squared) in worst case making it inefficient for large datasets. Merge sort has a time complexity of O(n log n) making it much more efficient. Bubble sort is simple to implement but slow while merge sort is faster but requires extra memory space for merging. Merge sort is preferred for large datasets.",
        "model_answer_ta": "Bubble sort மோசமான நிலையில் O(n squared) நேர சிக்கலை கொண்டுள்ளது, இது பெரிய தரவுத்தொகுப்புகளுக்கு திறனற்றதாக ஆக்குகிறது. Merge sort O(n log n) நேர சிக்கலை கொண்டுள்ளது, இது மிகவும் திறனுள்ளதாக உள்ளது. Bubble sort எளிதாக செயல்படுத்தலாம் ஆனால் மெதுவாக இருக்கும், merge sort வேகமாக இருக்கும் ஆனால் கூடுதல் நினைவகம் தேவைப்படும்.",
        "difficulty": 5, "blooms_level": "L4", "co_mapping": "CO4",
    },
    {
        "text": "What is the difference between stack and queue data structures?",
        "model_answer": "A stack follows Last In First Out (LIFO) principle where the last element added is the first to be removed. A queue follows First In First Out (FIFO) principle where the first element added is the first to be removed. Stack uses push and pop operations while queue uses enqueue and dequeue operations.",
        "model_answer_ta": "Stack கடைசியாக சேர்க்கப்பட்ட உறுப்பு முதலில் நீக்கப்படும் Last In First Out (LIFO) கொள்கையை பின்பற்றுகிறது. Queue முதலில் சேர்க்கப்பட்ட உறுப்பு முதலில் நீக்கப்படும் First In First Out (FIFO) கொள்கையை பின்பற்றுகிறது. Stack push மற்றும் pop செயல்பாடுகளை பயன்படுத்துகிறது, queue enqueue மற்றும் dequeue செயல்பாடுகளை பயன்படுத்துகிறது.",
        "difficulty": 4, "blooms_level": "L4", "co_mapping": "CO4",
    },

    # ── CO5 — Evaluation ───────────────────────────────────────
    {
        "text": "Evaluate whether using static variables is good practice in Java. Justify your answer.",
        "model_answer": "Static variables are useful for constants and shared counters but overusing them creates tight coupling and makes testing difficult. In multithreaded applications static variables can cause unexpected behavior due to shared state. They should be used sparingly only when truly necessary such as for constants or utility counters.",
        "model_answer_ta": "Static மாறிகள் மாறிலிகள் மற்றும் பகிரப்பட்ட கவுண்டர்களுக்கு பயனுள்ளவை ஆனால் அதிகமாக பயன்படுத்துவது tight coupling உருவாக்கி சோதனையை கடினமாக்கும். பல நூல் பயன்பாடுகளில் பகிரப்பட்ட நிலை காரணமாக static மாறிகள் எதிர்பாராத நடத்தையை ஏற்படுத்தலாம். மாறிலிகள் அல்லது பயன்பாட்டு கவுண்டர்களுக்கு மட்டுமே பயன்படுத்த வேண்டும்.",
        "difficulty": 5, "blooms_level": "L5", "co_mapping": "CO5",
    },
    {
        "text": "Is it better to use an array or ArrayList in Java? Justify with reasons.",
        "model_answer": "ArrayList is generally better than arrays for most use cases because it is dynamic and can grow or shrink in size. Arrays have fixed size which can waste memory or cause overflow. However arrays are faster for simple indexed access and use less memory overhead. For most applications ArrayList is preferred due to its flexibility and built-in methods.",
        "model_answer_ta": "ArrayList பெரும்பாலான பயன்பாடுகளுக்கு arrays ஐ விட சிறந்தது ஏனெனில் இது dynamic மற்றும் அளவில் வளரலாம் அல்லது சுருங்கலாம். Arrays நிலையான அளவைக் கொண்டுள்ளன, இது நினைவகத்தை வீணாக்கலாம் அல்லது overflow ஏற்படுத்தலாம். இருப்பினும் arrays எளிய indexed access க்கு வேகமாகவும் குறைந்த நினைவக overhead உடனும் இருக்கும். பெரும்பாலான பயன்பாடுகளுக்கு ArrayList விரும்பப்படுகிறது.",
        "difficulty": 4, "blooms_level": "L5", "co_mapping": "CO5",
    },

    # ── CO6 — Creation ─────────────────────────────────────────
    {
        "text": "Design a simple class in Java to represent a Student with name, age, and grade attributes.",
        "model_answer": "A Student class in Java should have private attributes name, age, and grade to follow encapsulation. We add a constructor to initialize these values and getter and setter methods to access and modify them. This design follows object oriented principles of encapsulation and abstraction making the code maintainable and reusable.",
        "model_answer_ta": "ஜாவாவில் Student வகுப்பு encapsulation பின்பற்ற name, age மற்றும் grade என்ற private பண்புகளை கொண்டிருக்க வேண்டும். இந்த மதிப்புகளை துவக்க constructor மற்றும் அவற்றை அணுக மற்றும் மாற்ற getter setter முறைகளை சேர்க்கிறோம். இந்த வடிவமைப்பு encapsulation மற்றும் abstraction என்ற OOP கொள்கைகளை பின்பற்றுகிறது.",
        "difficulty": 5, "blooms_level": "L6", "co_mapping": "CO6",
    },
    {
        "text": "Design a Java program to manage a simple library with add book and search book operations.",
        "model_answer": "We create a Book class with title and author attributes. A Library class maintains an ArrayList of Book objects. The addBook method creates a new Book and adds it to the list. The searchBook method loops through the list and returns the book whose title matches the search query. This design uses encapsulation and separation of concerns.",
        "model_answer_ta": "title மற்றும் author பண்புகளுடன் Book வகுப்பை உருவாக்குகிறோம். Library வகுப்பு Book பொருட்களின் ArrayList ஐ பராமரிக்கிறது. addBook முறை புதிய Book உருவாக்கி பட்டியலில் சேர்க்கிறது. searchBook முறை பட்டியலை சுற்றி தேடல் வினவலுடன் பொருந்தும் புத்தகத்தை திரும்பப் பெறுகிறது. இந்த வடிவமைப்பு encapsulation மற்றும் பொறுப்புகளின் பிரிவினையை பயன்படுத்துகிறது.",
        "difficulty": 5, "blooms_level": "L6", "co_mapping": "CO6",
    },
    {
        "text": "How would you design a Java method to check if a given string is a palindrome?",
        "model_answer": "A palindrome is a string that reads the same forwards and backwards. We create a method that takes a string parameter. We reverse the string using StringBuilder and compare it with the original using equals method. If both are equal the string is a palindrome and we return true otherwise we return false.",
        "model_answer_ta": "Palindrome என்பது முன்னும் பின்னும் ஒரே மாதிரி படிக்கப்படும் சரம். ஒரு string அளவுருவை எடுக்கும் முறையை உருவாக்குகிறோம். StringBuilder பயன்படுத்தி string ஐ தலைகீழாக மாற்றி equals முறை மூலம் அசல் string உடன் ஒப்பிடுகிறோம். இரண்டும் சமமாக இருந்தால் string palindrome ஆகும் மற்றும் true திரும்பப் பெறுகிறோம்.",
        "difficulty": 4, "blooms_level": "L6", "co_mapping": "CO6",
    },
]

print("Adding questions to database...")
added = 0
for qd in questions:
    # Check if question already exists
    existing = db.query(Question).filter(Question.text == qd["text"]).first()
    if existing:
        print(f"  Skipping (exists): {qd['text'][:50]}")
        continue

    q = Question(
        text            = qd["text"],
        model_answer    = qd["model_answer"],
        model_answer_ta = qd["model_answer_ta"],
        teacher_id      = teacher.id,
        difficulty      = qd["difficulty"],
        blooms_level    = qd["blooms_level"],
        co_mapping      = qd["co_mapping"],
    )
    db.add(q)
    added += 1
    print(f"  Added: {qd['text'][:60]}")

db.commit()
db.close()

print(f"\nDone! Added {added} questions.")
print(f"Total: {len(questions)} questions defined ({len(questions)-added} already existed)")
