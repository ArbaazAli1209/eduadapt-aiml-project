"""Curriculum content: topics, prerequisites, lessons, UI strings and a curated question bank.

Class 8 Mathematics (NCERT-aligned topics). English + Hindi. The question bank is the
offline fallback for the LLM quiz generator, so the app works with no model or internet.
"""

TOPICS = [
    "Squares and Square Roots",
    "Rational Numbers",
    "Algebraic Expressions",
    "Linear Equations",
    "Percentages",
    "Mensuration",
]

# topic -> topics that should be understood first
PREREQS = {
    "Linear Equations": ["Algebraic Expressions"],
    "Percentages": ["Rational Numbers"],
    "Mensuration": ["Squares and Square Roots"],
}

TOPIC_HI = {
    "Squares and Square Roots": "वर्ग और वर्गमूल",
    "Rational Numbers": "परिमेय संख्याएँ",
    "Algebraic Expressions": "बीजीय व्यंजक",
    "Linear Equations": "रैखिक समीकरण",
    "Percentages": "प्रतिशत",
    "Mensuration": "क्षेत्रमिति",
}

LESSONS = {
    "Squares and Square Roots": {
        "en": "The square of a number is the number multiplied by itself, for example 5 x 5 = 25. The square root is the reverse: the square root of 25 is 5. Perfect squares such as 1, 4, 9, 16 and 25 have whole-number square roots.",
        "hi": "किसी संख्या का वर्ग वह संख्या स्वयं से गुणा करने पर मिलता है, जैसे 5 x 5 = 25। वर्गमूल इसका उल्टा है: 25 का वर्गमूल 5 है। 1, 4, 9, 16, 25 जैसे पूर्ण वर्गों के वर्गमूल पूर्ण संख्याएँ होते हैं।",
    },
    "Rational Numbers": {
        "en": "A rational number can be written as p/q where p and q are integers and q is not zero, such as 3/5 or -2/7. Add fractions by making denominators equal. The additive inverse of a is -a and the multiplicative inverse of a/b is b/a.",
        "hi": "परिमेय संख्या को p/q के रूप में लिखा जा सकता है, जहाँ p और q पूर्णांक हैं और q शून्य नहीं है, जैसे 3/5 या -2/7। भिन्नों को जोड़ने के लिए हर बराबर करें। a का योज्य प्रतिलोम -a और a/b का गुणात्मक प्रतिलोम b/a होता है।",
    },
    "Algebraic Expressions": {
        "en": "An algebraic expression is made of variables, constants and operations, such as 3x + 2. Like terms (same variable and power) can be added or subtracted. To multiply two expressions, multiply every term of one by every term of the other.",
        "hi": "बीजीय व्यंजक चर, अचर और संक्रियाओं से बनता है, जैसे 3x + 2। समान पदों (वही चर और घात) को जोड़ा या घटाया जा सकता है। दो व्यंजकों का गुणा करने के लिए एक के हर पद को दूसरे के हर पद से गुणा करें।",
    },
    "Linear Equations": {
        "en": "A linear equation in one variable has the form ax + b = c. To solve it, do the same operation on both sides until x is alone. Move constants to one side, then divide by the coefficient of x. Always check the answer by putting it back in the equation.",
        "hi": "एक चर वाला रैखिक समीकरण ax + b = c के रूप का होता है। इसे हल करने के लिए दोनों पक्षों पर एक ही संक्रिया करें जब तक x अकेला न रह जाए। अचरों को एक ओर ले जाएँ, फिर x के गुणांक से भाग दें। उत्तर को समीकरण में रखकर जाँच अवश्य करें।",
    },
    "Percentages": {
        "en": "Percent means per hundred. To find a percentage of a number, multiply the number by the percent and divide by 100. Discount is subtracted from the marked price. Percentage change equals the change divided by the original value, times 100.",
        "hi": "प्रतिशत का अर्थ है प्रति सैकड़ा। किसी संख्या का प्रतिशत निकालने के लिए संख्या को प्रतिशत से गुणा करके 100 से भाग दें। छूट अंकित मूल्य में से घटाई जाती है। प्रतिशत परिवर्तन = परिवर्तन / मूल मान x 100।",
    },
    "Mensuration": {
        "en": "Mensuration is the measurement of shapes. Area of a rectangle is length x breadth, of a triangle is half x base x height, and of a circle is pi x r x r. Circumference of a circle is 2 x pi x r. Volume of a cuboid is length x breadth x height.",
        "hi": "क्षेत्रमिति आकृतियों की माप है। आयत का क्षेत्रफल लंबाई x चौड़ाई, त्रिभुज का आधा x आधार x ऊँचाई और वृत्त का pi x r x r होता है। वृत्त की परिधि 2 x pi x r होती है। घनाभ का आयतन लंबाई x चौड़ाई x ऊँचाई होता है।",
    },
}

UI = {
    "English": {
        "title": "EduAdapt",
        "tagline": "Your AI learning companion: it finds what you need to learn and teaches exactly that.",
        "language": "Language",
        "your_name": "Your name",
        "enter_name": "Enter your name in the sidebar to begin.",
        "mastery": "Your topic mastery",
        "recommended": "Today's focus",
        "new_student": "Welcome! Let's start with a short diagnostic quiz (one question from each topic).",
        "start_diag": "Start diagnostic quiz",
        "start_quiz": "Start practice quiz",
        "submit": "Submit answers",
        "correct": "Correct!",
        "incorrect": "Not quite.",
        "explanation": "Explanation",
        "next_quiz": "Next quiz",
        "lesson": "Quick lesson",
        "listen": "Listen",
        "ask_doubt": "Ask a doubt",
        "doubt_hint": "Type your doubt, for example: how do I find the area of a circle?",
        "answer": "Answer",
        "weak": "Needs practice",
        "strong": "Strong",
        "attempts": "Questions answered",
        "accuracy": "Accuracy",
        "select_all": "Please answer every question before submitting.",
        "difficulty": "Difficulty",
        "related": "Related topics to revise",
        "mastery_axis": "Mastery (0 to 1)",
        "voice_doubt": "Or ask by voice",
        "topic": "Topic",
    },
    "हिन्दी": {
        "title": "EduAdapt",
        "tagline": "आपका AI सीखने का साथी: यह पता लगाता है कि आपको क्या सीखना है और वही सिखाता है।",
        "language": "भाषा",
        "your_name": "आपका नाम",
        "enter_name": "शुरू करने के लिए साइडबार में अपना नाम लिखें।",
        "mastery": "आपकी विषय-निपुणता",
        "recommended": "आज का ध्यान",
        "new_student": "स्वागत है! पहले एक छोटी जाँच प्रश्नोत्तरी करें (हर विषय से एक प्रश्न)।",
        "start_diag": "जाँच प्रश्नोत्तरी शुरू करें",
        "start_quiz": "अभ्यास प्रश्नोत्तरी शुरू करें",
        "submit": "उत्तर जमा करें",
        "correct": "सही!",
        "incorrect": "सही नहीं।",
        "explanation": "व्याख्या",
        "next_quiz": "अगली प्रश्नोत्तरी",
        "lesson": "छोटा पाठ",
        "listen": "सुनें",
        "ask_doubt": "अपना संदेह पूछें",
        "doubt_hint": "अपना संदेह लिखें, जैसे: वृत्त का क्षेत्रफल कैसे निकालें?",
        "answer": "उत्तर",
        "weak": "अभ्यास की ज़रूरत",
        "strong": "मज़बूत",
        "attempts": "हल किए गए प्रश्न",
        "accuracy": "सटीकता",
        "select_all": "कृपया जमा करने से पहले हर प्रश्न का उत्तर दें।",
        "difficulty": "कठिनाई",
        "related": "दोहराने के लिए संबंधित विषय",
        "mastery_axis": "निपुणता (0 से 1)",
        "voice_doubt": "या बोलकर पूछें",
        "topic": "विषय",
    },
}

DIFF_HI = {"easy": "आसान", "medium": "मध्यम", "hard": "कठिन"}

# (topic, difficulty, question_en, question_hi, options, answer_index, explanation_en, explanation_hi)
_BANK = [
    # ---- Squares and Square Roots
    ("Squares and Square Roots", "easy", "What is the square of 12?", "12 का वर्ग क्या है?",
     ["124", "144", "132", "164"], 1, "12 x 12 = 144.", "12 x 12 = 144।"),
    ("Squares and Square Roots", "easy", "What is the square root of 81?", "81 का वर्गमूल क्या है?",
     ["8", "7", "9", "11"], 2, "9 x 9 = 81, so the square root of 81 is 9.", "9 x 9 = 81, इसलिए 81 का वर्गमूल 9 है।"),
    ("Squares and Square Roots", "medium", "Which of these numbers is a perfect square?", "इनमें से कौन-सी संख्या पूर्ण वर्ग है?",
     ["50", "72", "64", "99"], 2, "64 = 8 x 8, so it is a perfect square.", "64 = 8 x 8, इसलिए यह पूर्ण वर्ग है।"),
    ("Squares and Square Roots", "medium", "Find the value of the square root of 169 plus the square root of 25.", "169 के वर्गमूल और 25 के वर्गमूल का योग ज्ञात कीजिए।",
     ["18", "13", "15", "20"], 0, "The square root of 169 is 13 and of 25 is 5, and 13 + 5 = 18.", "169 का वर्गमूल 13 और 25 का 5 है, और 13 + 5 = 18।"),
    ("Squares and Square Roots", "hard", "What is the smallest number by which 72 must be multiplied to get a perfect square?", "वह सबसे छोटी संख्या क्या है जिससे 72 को गुणा करने पर पूर्ण वर्ग मिले?",
     ["2", "3", "6", "8"], 0, "72 = 2 x 2 x 2 x 3 x 3. The prime 2 appears three times, so multiply by 2 to get 144 = 12 x 12.", "72 = 2 x 2 x 2 x 3 x 3। अभाज्य 2 तीन बार आता है, इसलिए 2 से गुणा करने पर 144 = 12 x 12 मिलता है।"),
    ("Squares and Square Roots", "hard", "What is the square root of 0.0144?", "0.0144 का वर्गमूल क्या है?",
     ["0.12", "0.012", "1.2", "0.0012"], 0, "0.12 x 0.12 = 0.0144.", "0.12 x 0.12 = 0.0144।"),
    # ---- Rational Numbers
    ("Rational Numbers", "easy", "Which of these is a rational number?", "इनमें से कौन-सी परिमेय संख्या है?",
     ["square root of 2", "pi", "3/5", "square root of 3"], 2, "3/5 is in the form p/q with integers p and q, so it is rational.", "3/5, p/q के रूप में है जहाँ p और q पूर्णांक हैं, इसलिए यह परिमेय है।"),
    ("Rational Numbers", "easy", "What is the additive inverse of 5/7?", "5/7 का योज्य प्रतिलोम क्या है?",
     ["7/5", "-5/7", "-7/5", "5/7"], 1, "A number plus its additive inverse is 0, and 5/7 + (-5/7) = 0.", "किसी संख्या और उसके योज्य प्रतिलोम का योग 0 होता है, और 5/7 + (-5/7) = 0।"),
    ("Rational Numbers", "medium", "What is 1/2 + 1/3?", "1/2 + 1/3 का मान क्या है?",
     ["2/5", "1/5", "5/6", "2/6"], 2, "Make the denominators 6: 3/6 + 2/6 = 5/6.", "हर 6 करें: 3/6 + 2/6 = 5/6।"),
    ("Rational Numbers", "medium", "What is the multiplicative inverse of 3/4?", "3/4 का गुणात्मक प्रतिलोम क्या है?",
     ["-3/4", "4/3", "3/4", "-4/3"], 1, "3/4 x 4/3 = 1, so the multiplicative inverse is 4/3.", "3/4 x 4/3 = 1, इसलिए गुणात्मक प्रतिलोम 4/3 है।"),
    ("Rational Numbers", "hard", "Which rational number lies between 1/4 and 1/2?", "1/4 और 1/2 के बीच कौन-सी परिमेय संख्या है?",
     ["1/8", "5/8", "3/4", "3/8"], 3, "1/4 = 0.25 and 1/2 = 0.5, and 3/8 = 0.375 lies between them.", "1/4 = 0.25 और 1/2 = 0.5, तथा 3/8 = 0.375 इनके बीच है।"),
    ("Rational Numbers", "hard", "What is (-2/3) x (9/4)?", "(-2/3) x (9/4) का मान क्या है?",
     ["3/2", "-3/2", "1/2", "-1/2"], 1, "(-2 x 9) / (3 x 4) = -18/12 = -3/2.", "(-2 x 9) / (3 x 4) = -18/12 = -3/2।"),
    # ---- Algebraic Expressions
    ("Algebraic Expressions", "easy", "What is the coefficient of x in 7x + 3?", "7x + 3 में x का गुणांक क्या है?",
     ["3", "7", "10", "21"], 1, "The number multiplying x is 7.", "x को गुणा करने वाली संख्या 7 है।"),
    ("Algebraic Expressions", "easy", "Add: 2x + 3x", "जोड़िए: 2x + 3x",
     ["5x", "6x", "5x squared", "23x"], 0, "Like terms add: 2 + 3 = 5, so 5x.", "समान पद जुड़ते हैं: 2 + 3 = 5, इसलिए 5x।"),
    ("Algebraic Expressions", "medium", "Simplify: 4a - 2a + 5", "सरल कीजिए: 4a - 2a + 5",
     ["2a + 5", "6a + 5", "2a - 5", "7a"], 0, "4a - 2a = 2a, so the result is 2a + 5.", "4a - 2a = 2a, इसलिए परिणाम 2a + 5 है।"),
    ("Algebraic Expressions", "medium", "What is the value of 3x + 2 when x = 4?", "x = 4 होने पर 3x + 2 का मान क्या है?",
     ["12", "14", "10", "18"], 1, "3 x 4 + 2 = 12 + 2 = 14.", "3 x 4 + 2 = 12 + 2 = 14।"),
    ("Algebraic Expressions", "hard", "Expand: (x + 3)(x + 2)", "गुणनफल ज्ञात कीजिए: (x + 3)(x + 2)",
     ["x^2 + 5x + 6", "x^2 + 6", "x^2 + 5x + 5", "2x + 5"], 0, "x*x + 2x + 3x + 6 = x^2 + 5x + 6.", "x*x + 2x + 3x + 6 = x^2 + 5x + 6।"),
    ("Algebraic Expressions", "hard", "(a + b) squared is equal to", "(a + b) का वर्ग किसके बराबर है?",
     ["a^2 + b^2", "a^2 + 2ab + b^2", "a^2 - 2ab + b^2", "2a + 2b"], 1, "(a + b)(a + b) = a^2 + ab + ab + b^2 = a^2 + 2ab + b^2.", "(a + b)(a + b) = a^2 + ab + ab + b^2 = a^2 + 2ab + b^2।"),
    # ---- Linear Equations
    ("Linear Equations", "easy", "Solve: x + 7 = 15", "हल कीजिए: x + 7 = 15",
     ["22", "8", "7", "9"], 1, "Subtract 7 from both sides: x = 15 - 7 = 8.", "दोनों पक्षों से 7 घटाएँ: x = 15 - 7 = 8।"),
    ("Linear Equations", "easy", "Solve: 3x = 21", "हल कीजिए: 3x = 21",
     ["63", "18", "7", "24"], 2, "Divide both sides by 3: x = 7.", "दोनों पक्षों को 3 से भाग दें: x = 7।"),
    ("Linear Equations", "medium", "Solve: 2x + 5 = 17", "हल कीजिए: 2x + 5 = 17",
     ["11", "6", "5", "12"], 1, "2x = 17 - 5 = 12, so x = 6.", "2x = 17 - 5 = 12, इसलिए x = 6।"),
    ("Linear Equations", "medium", "Solve: x/3 - 2 = 4", "हल कीजिए: x/3 - 2 = 4",
     ["6", "2", "12", "18"], 3, "x/3 = 4 + 2 = 6, so x = 18.", "x/3 = 4 + 2 = 6, इसलिए x = 18।"),
    ("Linear Equations", "hard", "Solve: 3(x - 2) = 2x + 5", "हल कीजिए: 3(x - 2) = 2x + 5",
     ["11", "1", "7", "9"], 0, "3x - 6 = 2x + 5, so x = 11.", "3x - 6 = 2x + 5, इसलिए x = 11।"),
    ("Linear Equations", "hard", "The sum of two consecutive integers is 41. What is the smaller integer?", "दो क्रमागत पूर्णांकों का योग 41 है। छोटा पूर्णांक क्या है?",
     ["19", "21", "20", "22"], 2, "x + (x + 1) = 41 gives 2x = 40, so x = 20.", "x + (x + 1) = 41 से 2x = 40, इसलिए x = 20।"),
    # ---- Percentages
    ("Percentages", "easy", "What is 50% of 80?", "80 का 50% कितना होता है?",
     ["40", "50", "30", "25"], 0, "50% is half, and half of 80 is 40.", "50% आधा होता है, और 80 का आधा 40 है।"),
    ("Percentages", "easy", "What is 10% of 250?", "250 का 10% कितना होता है?",
     ["10", "50", "2.5", "25"], 3, "10/100 x 250 = 25.", "10/100 x 250 = 25।"),
    ("Percentages", "medium", "A shirt marked at Rs 500 is sold at a 20% discount. What is the selling price?", "Rs 500 अंकित मूल्य की एक कमीज़ 20% छूट पर बेची जाती है। विक्रय मूल्य क्या है?",
     ["Rs 400", "Rs 480", "Rs 100", "Rs 450"], 0, "Discount = 20% of 500 = 100, so the price is 500 - 100 = Rs 400.", "छूट = 500 का 20% = 100, इसलिए मूल्य 500 - 100 = Rs 400।"),
    ("Percentages", "medium", "Convert 3/4 into a percentage.", "3/4 को प्रतिशत में बदलिए।",
     ["34%", "60%", "75%", "80%"], 2, "3/4 = 0.75 = 75%.", "3/4 = 0.75 = 75%।"),
    ("Percentages", "hard", "A price rises from Rs 80 to Rs 100. What is the percentage increase?", "मूल्य Rs 80 से बढ़कर Rs 100 हो गया। प्रतिशत वृद्धि क्या है?",
     ["20%", "25%", "30%", "125%"], 1, "Increase = 20, and 20/80 x 100 = 25%.", "वृद्धि = 20, और 20/80 x 100 = 25%।"),
    ("Percentages", "hard", "After a 10% discount a bag costs Rs 900. What was its marked price?", "10% छूट के बाद एक बैग Rs 900 का है। उसका अंकित मूल्य क्या था?",
     ["Rs 990", "Rs 910", "Rs 1000", "Rs 810"], 2, "90% of the marked price is 900, so the marked price is 900 / 0.9 = Rs 1000.", "अंकित मूल्य का 90% = 900, इसलिए अंकित मूल्य 900 / 0.9 = Rs 1000।"),
    # ---- Mensuration
    ("Mensuration", "easy", "What is the area of a rectangle with length 8 cm and breadth 5 cm?", "8 cm लंबाई और 5 cm चौड़ाई वाले आयत का क्षेत्रफल क्या है?",
     ["13 cm2", "26 cm2", "40 cm2", "80 cm2"], 2, "Area = 8 x 5 = 40 square cm.", "क्षेत्रफल = 8 x 5 = 40 वर्ग cm।"),
    ("Mensuration", "easy", "What is the perimeter of a square of side 6 cm?", "6 cm भुजा वाले वर्ग का परिमाप क्या है?",
     ["12 cm", "36 cm", "24 cm", "18 cm"], 2, "Perimeter = 4 x 6 = 24 cm.", "परिमाप = 4 x 6 = 24 cm।"),
    ("Mensuration", "medium", "What is the area of a triangle with base 10 cm and height 6 cm?", "10 cm आधार और 6 cm ऊँचाई वाले त्रिभुज का क्षेत्रफल क्या है?",
     ["60 cm2", "30 cm2", "16 cm2", "15 cm2"], 1, "Area = half x 10 x 6 = 30 square cm.", "क्षेत्रफल = आधा x 10 x 6 = 30 वर्ग cm।"),
    ("Mensuration", "medium", "What is the area of a circle of radius 7 cm? (use pi = 22/7)", "7 cm त्रिज्या वाले वृत्त का क्षेत्रफल क्या है? (pi = 22/7 लें)",
     ["44 cm2", "154 cm2", "49 cm2", "308 cm2"], 1, "Area = 22/7 x 7 x 7 = 154 square cm.", "क्षेत्रफल = 22/7 x 7 x 7 = 154 वर्ग cm।"),
    ("Mensuration", "hard", "What is the circumference of a circle of radius 14 cm? (use pi = 22/7)", "14 cm त्रिज्या वाले वृत्त की परिधि क्या है? (pi = 22/7 लें)",
     ["44 cm", "88 cm", "616 cm", "28 cm"], 1, "Circumference = 2 x 22/7 x 14 = 88 cm.", "परिधि = 2 x 22/7 x 14 = 88 cm।"),
    ("Mensuration", "hard", "A cuboid has volume 120 cubic cm, length 6 cm and breadth 5 cm. What is its height?", "एक घनाभ का आयतन 120 घन cm, लंबाई 6 cm और चौड़ाई 5 cm है। उसकी ऊँचाई क्या है?",
     ["3 cm", "5 cm", "4 cm", "6 cm"], 2, "Height = 120 / (6 x 5) = 4 cm.", "ऊँचाई = 120 / (6 x 5) = 4 cm।"),
]


def build_bank():
    bank = []
    for i, (topic, diff, q, q_hi, options, ans, expl, expl_hi) in enumerate(_BANK):
        bank.append({
            "id": f"bank-{i:03d}", "topic": topic, "difficulty": diff,
            "question": q, "question_hi": q_hi,
            "options": list(options), "answer": options[ans],
            "explanation": expl, "explanation_hi": expl_hi, "source": "bank",
        })
    return bank


QUESTION_BANK = build_bank()
