from app.db.database import SessionLocal, engine, Base
from app.db.models import User, Question, Test, TestQuestion
from app.auth.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Users ──────────────────────────────────────────────────────
teacher1 = User(name="Teacher A", email="teacher1@test.com", password=hash_password("1234"), role="teacher", institution="Anna Univ")
teacher2 = User(name="Teacher B", email="teacher2@test.com", password=hash_password("1234"), role="teacher", institution="Anna Univ")
student1 = User(name="Student A", email="stu1@test.com",     password=hash_password("1234"), role="student", institution="Anna Univ")
student2 = User(name="Student B", email="stu2@test.com",     password=hash_password("1234"), role="student", institution="Anna Univ")
student3 = User(name="Student C", email="stu3@test.com",     password=hash_password("1234"), role="student", institution="Anna Univ")

db.add_all([teacher1, teacher2, student1, student2, student3])
db.flush()

# ── Questions ──────────────────────────────────────────────────
questions = [
    # Java Basics
    Question(
        text="What is a variable in Java?",
        model_answer="A variable in Java is a named memory location that stores a value. It must be declared with a data type before use.",
        model_answer_ta="ஜாவாவில் ஒரு மாறி என்பது ஒரு மதிப்பை சேமிக்கும் பெயரிடப்பட்ட நினைவக இடம். பயன்படுத்துவதற்கு முன் தரவு வகையுடன் அறிவிக்கப்பட வேண்டும்.",
        model_answer_hi="जावा में एक वेरिएबल एक नामित मेमोरी स्थान है जो एक मान संग्रहीत करता है। उपयोग से पहले इसे डेटा प्रकार के साथ घोषित किया जाना चाहिए।",
        teacher_id=teacher1.id, difficulty=1, blooms_level="L1", co_mapping="CO1"
    ),
    Question(
        text="What is the difference between int and double in Java?",
        model_answer="int stores whole numbers without decimal points while double stores numbers with decimal points. double uses more memory than int.",
        model_answer_ta="int என்பது தசம புள்ளிகள் இல்லாத முழு எண்களை சேமிக்கிறது, double என்பது தசம புள்ளிகளுடன் எண்களை சேமிக்கிறது. double, int ஐ விட அதிக நினைவகத்தை பயன்படுத்துகிறது.",
        model_answer_hi="int दशमलव बिंदुओं के बिना पूर्ण संख्याएं संग्रहीत करता है जबकि double दशमलव बिंदुओं के साथ संख्याएं संग्रहीत करता है। double, int से अधिक मेमोरी उपयोग करता है।",
        teacher_id=teacher1.id, difficulty=2, blooms_level="L2", co_mapping="CO1"
    ),
    Question(
        text="What is an array in Java?",
        model_answer="An array in Java is a collection of elements of the same data type stored in contiguous memory locations. Elements are accessed using an index starting from zero.",
        model_answer_ta="ஜாவாவில் ஒரு அணி என்பது தொடர்ச்சியான நினைவக இடங்களில் சேமிக்கப்பட்ட ஒரே தரவு வகையின் உறுப்புகளின் தொகுப்பு. உறுப்புகள் பூஜ்ஜியத்திலிருந்து தொடங்கும் குறியீட்டைப் பயன்படுத்தி அணுகப்படுகின்றன.",
        model_answer_hi="जावा में एक ऐरे एक ही डेटा प्रकार के तत्वों का संग्रह है जो सन्निहित मेमोरी स्थानों में संग्रहीत होता है। तत्वों को शून्य से शुरू होने वाले इंडेक्स का उपयोग करके एक्सेस किया जाता है।",
        teacher_id=teacher1.id, difficulty=2, blooms_level="L2", co_mapping="CO2"
    ),
    Question(
        text="What is a for loop in Java?",
        model_answer="A for loop in Java is used to execute a block of code repeatedly for a fixed number of times. It has three parts — initialization, condition, and increment.",
        model_answer_ta="ஜாவாவில் for loop என்பது ஒரு குறிப்பிட்ட எண்ணிக்கையிலான முறைகளுக்கு குறியீட்டு தொகுதியை மீண்டும் மீண்டும் இயக்க பயன்படுகிறது. இதில் மூன்று பகுதிகள் உள்ளன — துவக்கம், நிபந்தனை மற்றும் அதிகரிப்பு.",
        model_answer_hi="जावा में for loop का उपयोग एक निश्चित संख्या में कोड के एक ब्लॉक को बार-बार निष्पादित करने के लिए किया जाता है। इसके तीन भाग हैं — इनिशियलाइज़ेशन, कंडीशन और इंक्रीमेंट।",
        teacher_id=teacher1.id, difficulty=3, blooms_level="L3", co_mapping="CO2"
    ),
    Question(
        text="What is the use of if-else in Java?",
        model_answer="The if-else statement in Java is used for decision making. If the condition is true the if block executes, otherwise the else block executes.",
        model_answer_ta="ஜாவாவில் if-else அறிக்கை முடிவெடுப்பதற்கு பயன்படுகிறது. நிபந்தனை உண்மையாக இருந்தால் if தொகுதி இயங்கும், இல்லையெனில் else தொகுதி இயங்கும்.",
        model_answer_hi="जावा में if-else स्टेटमेंट का उपयोग निर्णय लेने के लिए किया जाता है। यदि शर्त सत्य है तो if ब्लॉक निष्पादित होता है, अन्यथा else ब्लॉक निष्पादित होता है।",
        teacher_id=teacher1.id, difficulty=2, blooms_level="L3", co_mapping="CO2"
    ),
    Question(
        text="What is a method in Java?",
        model_answer="A method in Java is a block of code that performs a specific task. It is defined with a name, return type, and optional parameters. Methods help in code reusability.",
        model_answer_ta="ஜாவாவில் ஒரு முறை என்பது ஒரு குறிப்பிட்ட பணியை செய்யும் குறியீட்டு தொகுதி. இது பெயர், திரும்பும் வகை மற்றும் விருப்பமான அளவுருக்களுடன் வரையறுக்கப்படுகிறது.",
        model_answer_hi="जावा में एक मेथड कोड का एक ब्लॉक है जो एक विशिष्ट कार्य करता है। इसे नाम, रिटर्न टाइप और वैकल्पिक पैरामीटर के साथ परिभाषित किया जाता है।",
        teacher_id=teacher1.id, difficulty=3, blooms_level="L2", co_mapping="CO3"
    ),
    Question(
        text="What is the difference between while loop and do-while loop in Java?",
        model_answer="A while loop checks the condition before executing the loop body. A do-while loop executes the loop body at least once before checking the condition.",
        model_answer_ta="while loop உடல் இயக்கும் முன் நிபந்தனையை சரிபார்க்கிறது. do-while loop நிபந்தனையை சரிபார்க்கும் முன் குறைந்தது ஒரு முறையாவது loop உடலை இயக்குகிறது.",
        model_answer_hi="while loop, लूप बॉडी को निष्पादित करने से पहले शर्त की जांच करता है। do-while loop, शर्त की जांच करने से पहले कम से कम एक बार लूप बॉडी को निष्पादित करता है।",
        teacher_id=teacher1.id, difficulty=3, blooms_level="L4", co_mapping="CO2"
    ),
    Question(
        text="What is a string in Java?",
        model_answer="A String in Java is a sequence of characters. It is an object of the String class and is immutable meaning its value cannot be changed after creation.",
        model_answer_ta="ஜாவாவில் String என்பது எழுத்துகளின் வரிசை. இது String வகுப்பின் ஒரு பொருள் மற்றும் மாறாதது, அதாவது உருவாக்கப்பட்ட பிறகு அதன் மதிப்பை மாற்ற முடியாது.",
        model_answer_hi="जावा में String वर्णों का एक अनुक्रम है। यह String क्लास का एक ऑब्जेक्ट है और अपरिवर्तनीय है अर्थात निर्माण के बाद इसका मान नहीं बदला जा सकता।",
        teacher_id=teacher1.id, difficulty=2, blooms_level="L1", co_mapping="CO1"
    ),
    Question(
        text="How does exception handling work in Java?",
        model_answer="Exception handling in Java uses try, catch, and finally blocks. Code that may throw an exception is placed in the try block. The catch block handles the exception. The finally block always executes.",
        model_answer_ta="ஜாவாவில் விதிவிலக்கு கையாளுதல் try, catch மற்றும் finally தொகுதிகளை பயன்படுத்துகிறது. விதிவிலக்கை எறியக்கூடிய குறியீடு try தொகுதியில் வைக்கப்படுகிறது. catch தொகுதி விதிவிலக்கை கையாளுகிறது.",
        model_answer_hi="जावा में अपवाद हैंडलिंग try, catch और finally ब्लॉक का उपयोग करती है। जो कोड अपवाद फेंक सकता है उसे try ब्लॉक में रखा जाता है। catch ब्लॉक अपवाद को संभालता है।",
        teacher_id=teacher1.id, difficulty=4, blooms_level="L3", co_mapping="CO3"
    ),
    Question(
        text="What is the difference between ArrayList and LinkedList in Java?",
        model_answer="ArrayList uses a dynamic array to store elements and provides fast random access. LinkedList uses a doubly linked list and provides fast insertion and deletion. ArrayList is better for accessing elements while LinkedList is better for frequent insertions.",
        model_answer_ta="ArrayList உறுப்புகளை சேமிக்க dynamic array பயன்படுத்துகிறது மற்றும் வேகமான random access வழங்குகிறது. LinkedList doubly linked list பயன்படுத்துகிறது மற்றும் வேகமான செருகல் மற்றும் நீக்கம் வழங்குகிறது.",
        model_answer_hi="ArrayList तत्वों को संग्रहीत करने के लिए dynamic array का उपयोग करता है और तेज़ random access प्रदान करता है। LinkedList doubly linked list का उपयोग करता है और तेज़ insertion और deletion प्रदान करता है।",
        teacher_id=teacher1.id, difficulty=4, blooms_level="L4", co_mapping="CO4"
    ),
]

db.add_all(questions)
db.flush()

# ── Test ───────────────────────────────────────────────────────
test1 = Test(title="Java Fundamentals - Unit 1", teacher_id=teacher1.id)
db.add(test1)
db.flush()

for i, q in enumerate(questions[:5]):
    db.add(TestQuestion(test_id=test1.id, question_id=q.id, max_score=10))

db.commit()
print("✅ Seed data inserted!")
print(f"   Teachers : teacher1@test.com, teacher2@test.com (password: 1234)")
print(f"   Students : stu1@test.com, stu2@test.com, stu3@test.com (password: 1234)")
print(f"   Questions: {len(questions)} questions added")
print(f"   Test     : Java Fundamentals - Unit 1 (5 questions)")
db.close()
