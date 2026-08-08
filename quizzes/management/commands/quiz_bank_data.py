"""Question bank data and generators for the quiz portal seed command.

Every category defines a `build` function that produces a pool of questions.
Each question is a dict: {'text': ..., 'correct': ..., 'wrongs': [...]}.
Quizzes sample unique questions from the pool.
"""

import random


def Q(text, correct, *wrongs):
    return {'text': text, 'correct': correct, 'wrongs': list(wrongs)}


def wrong_numbers(rng, correct, candidates, n=3, fallback_range=(1, 10000)):
    """Pick n distinct wrong numeric answers, padding if needed."""
    cands = [c for c in candidates if c != correct]
    if len(cands) < n:
        while len(cands) < n:
            extra = rng.randint(*fallback_range)
            if extra != correct and extra not in cands:
                cands.append(extra)
    return [str(w) for w in rng.sample(cands, n)]


def lookup_pool(rng, items, q_tpl, key_idx=0, val_idx=1):
    """Turn (key, value) pairs into questions like 'What is the X of Y?'."""
    vals = [it[val_idx] for it in items]
    pool = []
    for it in items:
        wrongs = rng.sample([v for v in vals if v != it[val_idx]], 3)
        pool.append(Q(q_tpl.format(it[key_idx]), it[val_idx], *wrongs))
    return pool


QUALIFIERS = [
    'Basics', 'Challenge', 'Quiz', 'Test', 'Trivia', 'Masterclass',
    'Fundamentals', 'Essentials', 'Expert Level', 'Practice Set',
    'Ultimate Guide', 'Rapid Fire', 'Deep Dive', '101', 'Intermediate',
    'Advanced', 'Pro Test', 'Concept Check', 'Bootcamp', 'Revision',
]


def build_titles(rng, fragments, needed, exclude=None):
    """Produce `needed` unique quiz titles not present in `exclude`."""
    exclude = set(exclude or [])
    titles = set(fragments)
    for frag in fragments:
        for qual in QUALIFIERS:
            titles.add('{} {}'.format(frag, qual))
    titles = list(titles)
    rng.shuffle(titles)
    result = [t for t in titles if t not in exclude]
    i = 1
    while len(result) < needed:
        cand = '{} Set {}'.format(fragments[i % len(fragments)], (i // len(fragments)) + 1)
        if cand not in exclude and cand not in result:
            result.append(cand)
        i += 1
    return result[:needed]


# =====================================================================
# Generator helpers
# =====================================================================

def arithmetic_pool(rng, count=90):
    pool = []
    for _ in range(count):
        a = rng.randint(12, 98)
        b = rng.randint(5, 40)
        op = rng.choice(['+', '-', '*'])
        if op == '+':
            c = a + b
            t = 'What is {} + {}?'.format(a, b)
        elif op == '-':
            c = a - b
            t = 'What is {} - {}?'.format(a, b)
        else:
            c = a * b
            t = 'What is {} x {}?'.format(a, b)
        wrongs = wrong_numbers(rng, c, [c + 1, c - 1, c + rng.randint(2, 9),
                                        c - rng.randint(2, 9), rng.randint(10, 5000)])
        pool.append(Q(t, str(c), *wrongs))
    return pool


def percent_pool(rng, count=45):
    pool = []
    for _ in range(count):
        p = rng.choice([10, 15, 20, 25, 30, 40, 50, 60, 75, 80])
        n = rng.choice([40, 60, 80, 100, 120, 150, 200, 250, 300, 400, 500])
        c = n * p // 100
        wrongs = wrong_numbers(rng, c, [c + 1, c - 1, c + rng.randint(2, 9),
                                        c - rng.randint(2, 9)])
        pool.append(Q('What is {}% of {}?'.format(p, n), str(c), *wrongs))
    return pool


def square_pool(rng, count=35):
    pool = []
    for _ in range(count):
        n = rng.randint(6, 30)
        c = n * n
        wrongs = wrong_numbers(rng, c, [(n + 1) ** 2, (n - 1) ** 2, n * (n + 2),
                                        c + rng.randint(2, 9)])
        pool.append(Q('What is the square of {}?'.format(n), str(c), *wrongs))
    return pool


def sequence_pool(rng, count=35):
    pool = []
    for _ in range(count):
        d = rng.randint(2, 9)
        start = rng.randint(1, 20)
        length = rng.randint(4, 6)
        seq = [start + i * d for i in range(length)]
        nxt = seq[-1] + d
        t = 'What is the next number in the sequence: {}?'.format(', '.join(map(str, seq)))
        wrongs = wrong_numbers(rng, nxt, [nxt + d, nxt - d, nxt + rng.randint(1, 4),
                                          nxt + d + 1])
        pool.append(Q(t, str(nxt), *wrongs))
    return pool


def binary_pool(rng, count=30):
    pool = []
    for _ in range(count):
        n = rng.randint(4, 200)
        b = bin(n)[2:]
        candidates = {bin(n + i)[2:] for i in (1, 2, 3, 4, 5)} | {b[::-1]}
        candidates = [c for c in candidates if c != b]
        wrongs = rng.sample(candidates, min(3, len(candidates)))
        pool.append(Q('What is the binary representation of {}?'.format(n), b, *wrongs))
    return pool


def code_output_pool():
    items = [
        ('print(2 ** 3)', '8', ['6', '9', '16']),
        ('print(10 % 3)', '1', ['3', '0', '2']),
        ('print(7 // 2)', '3', ['3.5', '2', '4']),
        ('print(len("hello"))', '5', ['4', '6', '10']),
        ('print("ab" * 3)', 'ababab', ['abab', 'abababab', 'aabbcc']),
        ('print(5 + 5 * 2)', '15', ['20', '30', '10']),
        ('print(bool(""))', 'False', ['True', 'None', '0']),
        ('print(3 == 3.0)', 'True', ['False', 'Error', 'None']),
        ('print("a" in "banana")', 'True', ['False', 'None', 'Error']),
        ('print(int("7") + 2)', '9', ['72', '7', 'Error']),
        ('print(round(3.7))', '4', ['3', '3.5', '5']),
        ('print(max(4, 9, 2))', '9', ['4', '2', '7']),
        ('print("hello".upper())', 'HELLO', ['hello', 'Hello', 'hi']),
        ('print(10 / 4)', '2.5', ['2', '2.4', '0.4']),
        ('print(2 + 3 * 4)', '14', ['20', '24', '11']),
        ('print([1, 2, 3][1])', '2', ['1', '3', '0']),
        ('print(len([1, 2, 3, 4]))', '4', ['3', '5', '2']),
        ('print(9 // 2)', '4', ['4.5', '3', '5']),
        ('print(min(8, 3, 5))', '3', ['5', '8', '1']),
        ('print(100 // 9)', '11', ['11.1', '10', '12']),
        ('print("abc"[::-1])', 'cba', ['abc', 'ab', 'xyz']),
        ('print(4 ** 0)', '1', ['0', '4', 'Error']),
        ('print(3 > 5)', 'False', ['True', 'None', 'Error']),
        ('print("".join(["a", "b"]))', 'ab', ['a,b', 'ab,', '["a","b"]']),
        ('print(7 % 5)', '2', ['1', '5', '0']),
        ('print(len("python"))', '6', ['5', '7', '4']),
        ('print(str(123) + "4")', '1234', ['127', '12347', 'Error']),
        ('print(5 ** 0.5 > 2)', 'True', ['False', 'Error', 'None']),
    ]
    return [Q('In Python, what is the output of {}?'.format(code), ans, *wrongs)
            for code, ans, wrongs in items]


def ratio_pool(rng, count=30):
    pool = []
    for _ in range(count):
        a = rng.randint(2, 15)
        b = rng.randint(2, 15)
        scale = rng.randint(2, 9)
        total = (a + b) * scale
        t = 'If a sum of {} is divided between two people in the ratio {}:{} , what is the larger share?'.format(total, a, b)
        larger = max(a, b) * scale
        smaller = min(a, b) * scale
        wrongs = wrong_numbers(rng, larger, [larger + a, larger - a, larger + b, smaller,
                                             total - smaller + 1])
        pool.append(Q(t, str(larger), *wrongs))
    return pool


def age_pool(rng, count=20):
    pool = []
    for _ in range(count):
        age = rng.randint(20, 50)
        years = rng.randint(2, 12)
        product = age * years
        t = 'If a person is {} years old, how old will they be in {} years?'.format(age, years)
        c = age + years
        wrongs = wrong_numbers(rng, c, [c + 1, c - 1, product, age - years, c + 2])
        pool.append(Q(t, str(c), *wrongs))
    return pool


# =====================================================================
# Curated fact lists
# =====================================================================

GK_CAPITALS = [
    ('Afghanistan', 'Kabul'), ('Argentina', 'Buenos Aires'), ('Australia', 'Canberra'),
    ('Austria', 'Vienna'), ('Bangladesh', 'Dhaka'), ('Belgium', 'Brussels'),
    ('Brazil', 'Brasilia'), ('Canada', 'Ottawa'), ('Chile', 'Santiago'),
    ('China', 'Beijing'), ('Colombia', 'Bogota'), ('Cuba', 'Havana'),
    ('Czech Republic', 'Prague'), ('Denmark', 'Copenhagen'), ('Egypt', 'Cairo'),
    ('Ethiopia', 'Addis Ababa'), ('Finland', 'Helsinki'), ('France', 'Paris'),
    ('Germany', 'Berlin'), ('Greece', 'Athens'), ('Hungary', 'Budapest'),
    ('Iceland', 'Reykjavik'), ('India', 'New Delhi'), ('Indonesia', 'Jakarta'),
    ('Iran', 'Tehran'), ('Iraq', 'Baghdad'), ('Ireland', 'Dublin'),
    ('Israel', 'Jerusalem'), ('Italy', 'Rome'), ('Japan', 'Tokyo'),
    ('Kenya', 'Nairobi'), ('Malaysia', 'Kuala Lumpur'), ('Mexico', 'Mexico City'),
    ('Morocco', 'Rabat'), ('Nepal', 'Kathmandu'), ('Netherlands', 'Amsterdam'),
    ('New Zealand', 'Wellington'), ('Nigeria', 'Abuja'), ('Norway', 'Oslo'),
    ('Pakistan', 'Islamabad'), ('Peru', 'Lima'), ('Philippines', 'Manila'),
    ('Poland', 'Warsaw'), ('Portugal', 'Lisbon'), ('Romania', 'Bucharest'),
    ('Russia', 'Moscow'), ('Saudi Arabia', 'Riyadh'), ('South Africa', 'Pretoria'),
    ('South Korea', 'Seoul'), ('Spain', 'Madrid'), ('Sri Lanka', 'Sri Jayawardenepura Kotte'),
    ('Sweden', 'Stockholm'), ('Switzerland', 'Bern'), ('Thailand', 'Bangkok'),
    ('Turkey', 'Ankara'), ('Ukraine', 'Kyiv'), ('United Arab Emirates', 'Abu Dhabi'),
    ('United Kingdom', 'London'), ('United States', 'Washington D.C.'),
    ('Vietnam', 'Hanoi'),
]

GK_CURRENCIES = [
    ('United States', 'US Dollar'), ('United Kingdom', 'British Pound'),
    ('Japan', 'Japanese Yen'), ('India', 'Indian Rupee'), ('China', 'Chinese Yuan'),
    ('Eurozone', 'Euro'), ('Canada', 'Canadian Dollar'), ('Australia', 'Australian Dollar'),
    ('Switzerland', 'Swiss Franc'), ('Russia', 'Russian Ruble'), ('Brazil', 'Brazilian Real'),
    ('Mexico', 'Mexican Peso'), ('South Africa', 'South African Rand'),
    ('Saudi Arabia', 'Saudi Riyal'), ('Turkey', 'Turkish Lira'), ('Nigeria', 'Nigerian Naira'),
    ('Egypt', 'Egyptian Pound'), ('Pakistan', 'Pakistani Rupee'),
    ('Bangladesh', 'Bangladeshi Taka'), ('Indonesia', 'Indonesian Rupiah'),
    ('South Korea', 'South Korean Won'), ('Sweden', 'Swedish Krona'),
    ('Norway', 'Norwegian Krone'), ('Denmark', 'Danish Krone'), ('Poland', 'Polish Zloty'),
    ('Thailand', 'Thai Baht'), ('Vietnam', 'Vietnamese Dong'),
    ('Philippines', 'Philippine Peso'), ('Malaysia', 'Malaysian Ringgit'),
    ('Singapore', 'Singapore Dollar'), ('New Zealand', 'New Zealand Dollar'),
    ('Argentina', 'Argentine Peso'), ('Chile', 'Chilean Peso'),
    ('Colombia', 'Colombian Peso'), ('Kenya', 'Kenyan Shilling'),
    ('Israel', 'Israeli New Shekel'),
]

GK_LANDMARKS = [
    ('Eiffel Tower', 'France'), ('Statue of Liberty', 'United States'),
    ('Taj Mahal', 'India'), ('Great Wall of China', 'China'), ('Colosseum', 'Italy'),
    ('Machu Picchu', 'Peru'), ('Pyramids of Giza', 'Egypt'), ('Stonehenge', 'United Kingdom'),
    ('Big Ben', 'United Kingdom'), ('Sagrada Familia', 'Spain'),
    ('Sydney Opera House', 'Australia'), ('Christ the Redeemer', 'Brazil'),
    ('Petra', 'Jordan'), ('Chichen Itza', 'Mexico'), ('Acropolis', 'Greece'),
    ('Leaning Tower of Pisa', 'Italy'), ('Mount Fuji', 'Japan'),
    ('Angkor Wat', 'Cambodia'), ('Golden Gate Bridge', 'United States'),
    ('Burj Khalifa', 'United Arab Emirates'), ('Table Mountain', 'South Africa'),
    ('Moai Statues', 'Chile'), ('Kremlin', 'Russia'), ('Hagia Sophia', 'Turkey'),
    ('Mount Rushmore', 'United States'), ('Neuschwanstein Castle', 'Germany'),
    ('Lotus Temple', 'India'), ('Saint Basil Cathedral', 'Russia'),
]

GK_INVENTORS = [
    ('the telephone', 'Alexander Graham Bell'), ('the incandescent light bulb', 'Thomas Edison'),
    ('the airplane', 'the Wright Brothers'), ('the printing press', 'Johannes Gutenberg'),
    ('the radio', 'Guglielmo Marconi'), ('the television', 'John Logie Baird'),
    ('the World Wide Web', 'Tim Berners-Lee'), ('dynamite', 'Alfred Nobel'),
    ('the steam engine', 'James Watt'), ('the electric battery', 'Alessandro Volta'),
    ('the X-ray machine', 'Wilhelm Rontgen'), ('the polio vaccine', 'Jonas Salk'),
    ('the periodic table', 'Dmitri Mendeleev'), ('the telegraph', 'Samuel Morse'),
    ('the first mechanical computer', 'Charles Babbage'), ('the phonograph', 'Thomas Edison'),
    ('the lightning rod', 'Benjamin Franklin'), ('the sewing machine', 'Elias Howe'),
    ('the typewriter', 'Christopher Sholes'), ('the telephone exchange', 'Tivadar Puskas'),
    ('the zipper', 'Gideon Sundback'), ('the safety razor', 'King Camp Gillette'),
    ('the microscope', 'Zacharias Janssen'), ('the first airplane engine', 'Charles Taylor'),
]

GK_SCIENTISTS = [
    ('Albert Einstein', 'the theory of relativity'), ('Isaac Newton', 'the laws of motion'),
    ('Charles Darwin', 'the theory of evolution'), ('Marie Curie', 'radioactivity research'),
    ('Louis Pasteur', 'pasteurization'), ('Nikola Tesla', 'alternating current'),
    ('Niels Bohr', 'atomic structure'), ('Michael Faraday', 'electromagnetism'),
    ('Galileo Galilei', 'modern astronomy'), ('Stephen Hawking', 'black hole theory'),
    ('Gregor Mendel', 'genetics'), ('Alan Turing', 'computer science'),
    ('Ada Lovelace', 'programming'), ('Srinivasa Ramanujan', 'number theory'),
    ('Richard Feynman', 'quantum mechanics'), ('Edwin Hubble', 'expanding universe'),
    ('James Watson', 'DNA structure'), ('Enrico Fermi', 'nuclear physics'),
    ('Heinrich Hertz', 'electromagnetic waves'), ('Alexander Fleming', 'penicillin'),
    ('Linus Pauling', 'quantum chemistry'), ('James Clerk Maxwell', 'electromagnetic theory'),
]

GK_CURATED = [
    Q('How many continents are there?', '7', '5', '6', '8'),
    Q('How many planets are in our solar system?', '8', '7', '9', '10'),
    Q('Which planet is closest to the Sun?', 'Mercury', 'Venus', 'Mars', 'Earth'),
    Q('What is the largest ocean on Earth?', 'Pacific Ocean', 'Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean'),
    Q('What is the longest bone in the human body?', 'Femur', 'Tibia', 'Humerus', 'Fibula'),
    Q('How many colours are in a rainbow?', '7', '6', '8', '5'),
    Q('What is the smallest country in the world?', 'Vatican City', 'Monaco', 'Malta', 'San Marino'),
    Q('Which planet is known as the Morning Star?', 'Venus', 'Mars', 'Mercury', 'Jupiter'),
    Q('What is the hardest natural substance?', 'Diamond', 'Gold', 'Iron', 'Quartz'),
    Q('How many bones are in the adult human body?', '206', '201', '208', '210'),
    Q('Which is the largest desert in the world?', 'Antarctica', 'Sahara', 'Gobi', 'Arabian'),
    Q('How many strings does a standard acoustic guitar have?', '6', '5', '7', '4'),
    Q('Which language has the most native speakers?', 'Mandarin Chinese', 'English', 'Spanish', 'Hindi'),
    Q('What is the largest mammal in the world?', 'Blue Whale', 'African Elephant', 'Giraffe', 'Hippopotamus'),
    Q('What is the fastest land animal?', 'Cheetah', 'Lion', 'Leopard', 'Horse'),
    Q('Which gas do plants absorb from the atmosphere?', 'Carbon dioxide', 'Oxygen', 'Nitrogen', 'Hydrogen'),
    Q('What is the freezing point of water in degrees Celsius?', '0', '32', '100', '-1'),
    Q('Which is the largest country by land area?', 'Russia', 'Canada', 'China', 'United States'),
    Q('What is the tallest mountain on Earth?', 'Mount Everest', 'K2', 'Kangchenjunga', 'Lhotse'),
    Q('Which element has the chemical symbol O?', 'Oxygen', 'Osmium', 'Gold', 'Oganesson'),
    Q('How many days are in a leap year?', '366', '365', '364', '360'),
    Q('What is the smallest prime number?', '2', '1', '3', '0'),
    Q('What is the approximate speed of light?', '300,000 km/s', '150,000 km/s', '500,000 km/s', '100,000 km/s'),
    Q('Which organ pumps blood around the body?', 'Heart', 'Lungs', 'Liver', 'Brain'),
    Q('What is the largest organ of the human body?', 'Skin', 'Liver', 'Lungs', 'Heart'),
    Q('How many teeth does a healthy adult human have?', '32', '28', '30', '34'),
    Q('What is the largest island on Earth?', 'Greenland', 'Australia', 'Borneo', 'Madagascar'),
    Q('What is the study of stars and celestial bodies called?', 'Astronomy', 'Astrology', 'Geology', 'Meteorology'),
    Q('Which animal is the tallest in the world?', 'Giraffe', 'Elephant', 'Ostrich', 'Camel'),
    Q('What is the most abundant gas in Earth atmosphere?', 'Nitrogen', 'Oxygen', 'Carbon dioxide', 'Argon'),
    Q('Which is the deepest ocean trench?', 'Mariana Trench', 'Java Trench', 'Tonga Trench', 'Puerto Rico Trench'),
    Q('How many hearts does an octopus have?', '3', '1', '2', '4'),
    Q('What is the largest land animal?', 'African Elephant', 'White Rhinoceros', 'Hippopotamus', 'Giraffe'),
    Q('What is the chemical symbol for gold?', 'Au', 'Ag', 'Fe', 'Pb'),
    Q('Which planet rotates on its side?', 'Uranus', 'Saturn', 'Neptune', 'Venus'),
    Q('Which festival is known as the festival of lights in India?', 'Diwali', 'Holi', 'Eid', 'Christmas'),
    Q('What is the tallest waterfall in the world?', 'Angel Falls', 'Victoria Falls', 'Niagara Falls', 'Iguazu Falls'),
    Q('How many sides does a hexagon have?', '6', '5', '7', '8'),
    Q('Which country is famous for growing tulips?', 'Netherlands', 'France', 'Italy', 'Belgium'),
    Q('Who was the first person to walk on the Moon?', 'Neil Armstrong', 'Buzz Aldrin', 'Yuri Gagarin', 'Michael Collins'),
    Q('Which planet has the most confirmed moons?', 'Saturn', 'Jupiter', 'Mars', 'Neptune'),
    Q('What is the currency of Japan?', 'Yen', 'Won', 'Yuan', 'Ringgit'),
    Q('How many players are in a cricket team?', '11', '9', '10', '12'),
    Q('Which country invented paper?', 'China', 'Egypt', 'India', 'Greece'),
    Q('What is the hottest planet in the solar system?', 'Venus', 'Mercury', 'Mars', 'Jupiter'),
    Q('Which is the largest freshwater lake by volume?', 'Lake Baikal', 'Lake Superior', 'Lake Victoria', 'Caspian Sea'),
    Q('What is the study of weather called?', 'Meteorology', 'Geology', 'Astronomy', 'Oceanography'),
    Q('Which bird is known for mimicking sounds?', 'Parrot', 'Sparrow', 'Eagle', 'Pigeon'),
    Q('How many time zones does the world have?', '24', '12', '36', '48'),
    Q('Which metal is liquid at room temperature?', 'Mercury', 'Iron', 'Aluminium', 'Copper'),
]


def build_gk(rng):
    return (lookup_pool(rng, GK_CAPITALS, 'What is the capital of {}?')
            + lookup_pool(rng, GK_CURRENCIES, 'What is the currency of {}?')
            + lookup_pool(rng, GK_LANDMARKS, 'In which country is the {} located?')
            + lookup_pool(rng, GK_INVENTORS, 'Who invented {}?')
            + lookup_pool(rng, GK_SCIENTISTS, 'Who is known for {}?')
            + list(GK_CURATED))


# =====================================================================
# Computer Science
# =====================================================================

CS_CURATED = [
    Q('What does CPU stand for?', 'Central Processing Unit', 'Computer Personal Unit', 'Central Program Utility', 'Control Processing Unit'),
    Q('What does RAM stand for?', 'Random Access Memory', 'Read Access Memory', 'Rapid Access Module', 'Random Alloc Memory'),
    Q('What is the main memory of a computer that stores data temporarily?', 'RAM', 'ROM', 'Cache', 'SSD'),
    Q('Which memory is non-volatile and used for boot instructions?', 'ROM', 'RAM', 'Cache', 'Register'),
    Q('Which component is considered the brain of the computer?', 'CPU', 'GPU', 'RAM', 'Hard disk'),
    Q('What is the binary number system base?', '2', '8', '10', '16'),
    Q('What is the decimal value of the binary number 1010?', '10', '8', '12', '5'),
    Q('How many bits are in one byte?', '8', '4', '16', '32'),
    Q('Which of these is a type of volatile memory?', 'RAM', 'ROM', 'Flash', 'Hard disk'),
    Q('What does GPU stand for?', 'Graphics Processing Unit', 'General Processing Unit', 'Graphical Program Utility', 'Global Processing Unit'),
    Q('Which bus connects the CPU to the main memory?', 'System bus', 'USB bus', 'Serial bus', 'PCI bus'),
    Q('What is the smallest unit of data in computing?', 'Bit', 'Byte', 'Nibble', 'Word'),
    Q('How many bits are in a nibble?', '4', '8', '2', '16'),
    Q('What does the term 32-bit processor refer to?', 'Register width', 'Clock speed', 'Cache size', 'RAM size'),
    Q('Which company makes the x86 processor architecture?', 'Intel', 'AMD', 'ARM', 'Apple'),
    Q('What does SSD stand for?', 'Solid State Drive', 'System Storage Disk', 'Super Speed Drive', 'Serial Storage Device'),
    Q('Which cache level is closest to the CPU core?', 'L1', 'L2', 'L3', 'RAM'),
    Q('What is the process of converting source code into machine code called?', 'Compilation', 'Interpretation', 'Translation', 'Execution'),
    Q('What is an interpreter used for?', 'Executing code line by line', 'Compiling code', 'Debugging hardware', 'Managing memory'),
    Q('Which of the following is a low-level programming language?', 'Assembly', 'Python', 'Java', 'JavaScript'),
    Q('What does the SDLC stand for?', 'Software Development Life Cycle', 'System Data Load Cycle', 'Software Design Logic Center', 'System Development Language Core'),
    Q('Which phase comes first in the SDLC?', 'Requirement analysis', 'Testing', 'Deployment', 'Maintenance'),
    Q('What is unit testing?', 'Testing individual components', 'Testing the whole system', 'Testing user interface', 'Testing performance'),
    Q('What does QA stand for in software development?', 'Quality Assurance', 'Quick Access', 'Quality Audit', 'Query Analysis'),
    Q('Which model describes software development in linear phases?', 'Waterfall', 'Agile', 'Spiral', 'V-Model'),
    Q('What does the agile methodology emphasize?', 'Incremental delivery', 'Linear phases', 'Documentation only', 'Waterfall planning'),
    Q('Which language is known for its garbage collection and runs on the JVM?', 'Java', 'C', 'C++', 'Assembly'),
    Q('What is a compiler frontend responsible for?', 'Lexical and syntax analysis', 'Code optimization', 'Register allocation', 'Machine code generation'),
    Q('Which phase of a compiler removes dead code?', 'Optimization', 'Lexical analysis', 'Parsing', 'Linking'),
    Q('What is a token in compiler design?', 'A sequence of characters with a meaning', 'A memory address', 'A hardware device', 'A register'),
    Q('Which is the first phase of a compiler?', 'Lexical analysis', 'Semantic analysis', 'Code generation', 'Optimization'),
    Q('What is a finite automaton?', 'A mathematical model with a finite set of states', 'A type of Turing machine', 'A data structure', 'A compiler'),
    Q('Which machine has unlimited memory and is the basis of computation?', 'Turing Machine', 'Finite Automaton', 'Pushdown Automaton', 'Mealy Machine'),
    Q('Which grammar type is used to describe programming language syntax?', 'Context-free grammar', 'Regular grammar', 'Context-sensitive grammar', 'Unrestricted grammar'),
    Q('What is a pushdown automaton equivalent to?', 'Context-free grammar', 'Regular grammar', 'Turing machine', 'Finite automaton'),
    Q('Which of the following is a regular expression operator?', 'Kleene star', 'Lambda', 'Gamma', 'Delta'),
    Q('What does the Halting Problem demonstrate?', 'Some problems are undecidable', 'All problems are solvable', 'Computers are infinite', 'NP equals P'),
    Q('What is the Church-Turing thesis about?', 'The nature of computable functions', 'The speed of computers', 'Memory capacity', 'Compiler design'),
    Q('Which data structure uses FIFO ordering?', 'Queue', 'Stack', 'Tree', 'Graph'),
    Q('Which data structure uses LIFO ordering?', 'Stack', 'Queue', 'Array', 'Heap'),
    Q('What is the time complexity of binary search?', 'O(log n)', 'O(n)', 'O(n log n)', 'O(1)'),
    Q('What does DBMS stand for?', 'Database Management System', 'Data Backup Management System', 'Digital Binary Memory System', 'Dynamic Buffer Management System'),
    Q('What is a primary key in a database?', 'A unique identifier for a record', 'A foreign reference', 'An index', 'A table name'),
    Q('Which SQL command is used to retrieve data?', 'SELECT', 'GET', 'FETCH', 'PULL'),
    Q('What does SQL stand for?', 'Structured Query Language', 'Simple Query Language', 'System Query Logic', 'Standard Query Language'),
    Q('Which sorting algorithm has the best average case of O(n log n)?', 'Merge sort', 'Bubble sort', 'Selection sort', 'Insertion sort'),
    Q('What is the worst-case time complexity of bubble sort?', 'O(n^2)', 'O(n)', 'O(n log n)', 'O(log n)'),
    Q('Which algorithm is used to find the shortest path in a graph?', "Dijkstra's algorithm", "Prim's algorithm", 'Binary search', 'Linear search'),
    Q('What does HTTP stand for?', 'HyperText Transfer Protocol', 'High Transfer Text Protocol', 'Hyper Text Terminal Protocol', 'Host Transfer Protocol'),
    Q('Which protocol provides a secure HTTP connection?', 'HTTPS', 'FTP', 'SMTP', 'DNS'),
    Q('What is an IP address?', 'A unique address of a device on a network', 'A web address', 'An email address', 'A file name'),
    Q('Which device connects multiple networks?', 'Router', 'Switch', 'Hub', 'Modem'),
    Q('What does OS stand for?', 'Operating System', 'Open Source', 'Output System', 'Online Server'),
    Q('Which OS kernel manages processes and memory?', 'Linux kernel', 'BIOS', 'Bootloader', 'Shell'),
    Q('What is deadlock in operating systems?', 'Two or more processes waiting for each other', 'A process crash', 'Memory leak', 'CPU overheating'),
    Q('Which scheduling algorithm uses the shortest job first?', 'SJF', 'FCFS', 'Round robin', 'Priority'),
    Q('What is paging in memory management?', 'Dividing memory into fixed-size pages', 'Compressing files', 'Encrypting data', 'Clearing cache'),
    Q('What is virtual memory?', 'Using disk space as an extension of RAM', 'A type of ROM', 'Cache memory', 'Register memory'),
    Q('What does BIOS stand for?', 'Basic Input Output System', 'Binary Input Output System', 'Basic Integrated Operating System', 'Boot Input Output Setup'),
    Q('Which of the following is an operating system?', 'Ubuntu', 'Chrome', 'Firefox', 'Photoshop'),
    Q('What is the file system used by Linux by default?', 'ext4', 'NTFS', 'FAT32', 'HFS+'),
    Q('What is a process in an operating system?', 'A program in execution', 'A file', 'A hardware device', 'A user'),
    Q('Which component manages input and output devices?', 'Device drivers', 'Applications', 'Browsers', 'Shells'),
    Q('What is the kernel?', 'The core of the operating system', 'A hardware chip', 'A file type', 'A user interface'),
    Q('What is multiprogramming?', 'Running multiple programs concurrently', 'Running one program', 'Duplicating files', 'Restarting the system'),
    Q('What does 1 KB equal?', '1024 bytes', '1000 bytes', '8 bytes', '1024 bits'),
    Q('Which of these is a cloud computing service model?', 'IaaS', 'DDoS', 'TCP', 'HTML'),
    Q('What does SaaS stand for?', 'Software as a Service', 'System as a Service', 'Software and Security', 'Storage as a Service'),
    Q('What is Big Data characterized by?', 'Volume, velocity and variety', 'Speed only', 'Small files', 'Offline storage'),
    Q('What is the Internet of Things (IoT)?', 'Networked physical devices', 'A web browser', 'A programming language', 'An email service'),
    Q('What does AI stand for?', 'Artificial Intelligence', 'Automated Input', 'Advanced Internet', 'Analog Integration'),
    Q('Which is a supervised learning algorithm?', 'Linear regression', 'K-means', 'Apriori', 'DBSCAN'),
    Q('What is a neural network?', 'A model inspired by the brain', 'A type of virus', 'A network cable', 'A database'),
    Q('What does API stand for?', 'Application Programming Interface', 'Advanced Program Instruction', 'Application Process Integration', 'Automated Protocol Interface'),
    Q('What is a framework?', 'A reusable structure for building software', 'A hardware component', 'A database', 'An operating system'),
    Q('Which of the following is a version control system?', 'Git', 'Docker', 'Kubernetes', 'Nginx'),
    Q('What is refactoring?', 'Restructuring code without changing behavior', 'Deleting code', 'Adding features', 'Optimizing hardware'),
    Q('What is a bug?', 'An error in a program', 'A hardware fault', 'A network issue', 'A data type'),
    Q('What does debugging mean?', 'Finding and fixing errors', 'Compiling code', 'Running tests', 'Deploying code'),
    Q('What is a high-level language?', 'A language close to human language', 'A language close to machine code', 'A binary language', 'An assembly language'),
    Q('Which language is compiled to bytecode and runs on JVM?', 'Java', 'Python', 'Ruby', 'PHP'),
    Q('What is the time complexity of accessing an array element by index?', 'O(1)', 'O(n)', 'O(log n)', 'O(n^2)'),
    Q('Which structure is used for function calls in most languages?', 'Call stack', 'Queue', 'Heap', 'Tree'),
    Q('What is a linked list?', 'A sequence of nodes connected by pointers', 'An array', 'A hash map', 'A binary tree'),
    Q('What is the advantage of a hash table?', 'Fast average O(1) lookups', 'Sorted data', 'Fixed size', 'Slow inserts'),
    Q('Which of the following is a NoSQL database?', 'MongoDB', 'MySQL', 'PostgreSQL', 'Oracle'),
    Q('What is ACID in databases?', 'Atomicity, Consistency, Isolation, Durability', 'Access, Control, Index, Data', 'All, Clear, Insert, Delete', 'Auto, Check, Input, Delete'),
    Q('What is a transaction in a database?', 'A unit of work with multiple operations', 'A query', 'A table', 'A backup'),
    Q('What does CRUD stand for?', 'Create, Read, Update, Delete', 'Copy, Run, Undo, Delete', 'Create, Restore, Update, Drop', 'Call, Read, Use, Delete'),
    Q('What is normalisation in databases?', 'Reducing data redundancy', 'Encrypting data', 'Sharding tables', 'Indexing data'),
    Q('What is an index in a database?', 'A structure to speed up queries', 'A table copy', 'A stored procedure', 'A foreign key'),
    Q('Which of these is a primary key property?', 'It must be unique', 'It can be null', 'It can be duplicated', 'It is optional'),
    Q('What is a foreign key?', 'A key that references another table', 'A duplicate key', 'A primary key', 'An index key'),
    Q('What is latency?', 'The delay before data transfer begins', 'The data size', 'The bandwidth', 'The error rate'),
    Q('What is bandwidth?', 'The maximum data transfer rate', 'The delay', 'The packet size', 'The IP address'),
    Q('Which protocol is used for email transfer?', 'SMTP', 'FTP', 'HTTP', 'SNMP'),
    Q('What does DNS do?', 'Translates domain names to IP addresses', 'Encrypts data', 'Routes packets', 'Compresses files'),
    Q('What is a firewall used for?', 'Filtering network traffic', 'Increasing speed', 'Storing data', 'Compiling code'),
    Q('What does Wi-Fi stand for?', 'Wireless Fidelity', 'Wireless Frequency', 'Wide Frequency', 'Wireless File'),
    Q('Which encryption standard is commonly used on the web?', 'TLS', 'MD5', 'Base64', 'SHA-1'),
    Q('What is a data packet?', 'A unit of data transmitted over a network', 'A database record', 'A file folder', 'A memory cell'),
    Q('What is recursion?', 'A function calling itself', 'A loop', 'A data type', 'A variable'),
    Q('What is the base case in recursion?', 'The condition that stops recursion', 'The first call', 'The return value', 'The function name'),
    Q('Which loop repeats a fixed number of times?', 'For loop', 'While loop', 'Do-while loop', 'Infinite loop'),
    Q('What is a variable?', 'A named storage location in memory', 'A constant', 'A function', 'A class'),
    Q('What is a data type?', 'A classification of data values', 'A variable name', 'An operator', 'A statement'),
    Q('Which of the following is a boolean value?', 'True', '1.5', '"Hello"', 'None'),
    Q('What is an algorithm?', 'A step-by-step procedure to solve a problem', 'A programming language', 'A data structure', 'A bug'),
    Q('What is pseudocode?', 'An informal way of describing an algorithm', 'Compiled code', 'Machine code', 'A markup language'),
    Q('Which notation describes algorithm efficiency?', 'Big O notation', 'Binary notation', 'Octal notation', 'Decimal notation'),
    Q('What does FIFO stand for?', 'First In, First Out', 'Fast Input, Fast Output', 'First Input, Final Output', 'File Input Output'),
    Q('What is a stack overflow?', 'Recursion without a base case', 'A full hard disk', 'Too many files', 'High CPU usage'),
]


def build_cs(rng):
    return list(CS_CURATED) + binary_pool(rng)


# =====================================================================
# Programming
# =====================================================================

PROG_CURATED = [
    Q('Which keyword is used to define a function in Python?', 'def', 'func', 'function', 'lambda'),
    Q('How do you create a list in Python?', '[]', '{}', '()', '<>'),
    Q('Which of the following is a Python tuple?', '(1, 2, 3)', '[1, 2, 3]', '{1, 2, 3}', '{1: 2}'),
    Q('What is the output of type(3.14) in Python?', 'float', 'int', 'double', 'decimal'),
    Q('Which statement is used to handle exceptions in Python?', 'try/except', 'catch/throw', 'if/else', 'switch/case'),
    Q('What is the keyword for a class in Python?', 'class', 'object', 'struct', 'def'),
    Q('Which method is called when an object is created in Python?', '__init__', '__new__', '__main__', '__call__'),
    Q('How do you import a module in Python?', 'import', 'include', 'require', 'using'),
    Q('What is the result of 2 == "2" in Python?', 'False', 'True', 'Error', 'None'),
    Q('Which data structure in Python is a collection of key-value pairs?', 'Dictionary', 'List', 'Tuple', 'Set'),
    Q('What is the output of list(range(3))?', '[0, 1, 2]', '[1, 2, 3]', '[0, 1, 2, 3]', '[1, 2]'),
    Q('Which keyword is used to return a value in Python?', 'return', 'yield', 'break', 'continue'),
    Q('What is the default index of the first element of a list?', '0', '1', '-1', 'None'),
    Q('Which Python library is used for data analysis?', 'pandas', 'flask', 'django', 'requests'),
    Q('Which library is used for numerical computations in Python?', 'NumPy', 'SciPy', 'Matplotlib', 'Pillow'),
    Q('Which library is used for machine learning in Python?', 'scikit-learn', 'requests', 'tkinter', 'sqlite3'),
    Q('What is the keyword to create a virtual environment in Python?', 'venv', 'env', 'virtual', 'ven'),
    Q('How do you run a Python script named app.py?', 'python app.py', 'run app.py', 'exec app.py', 'start app.py'),
    Q('What is pip used for in Python?', 'Installing packages', 'Running code', 'Debugging', 'Compiling'),
    Q('Which symbol denotes a comment in Python?', '#', '//', '/*', '--'),
    Q('What is the output of len("hello world")?', '11', '10', '12', '5'),
    Q('What is the keyword for anonymous functions in Python?', 'lambda', 'def', 'anon', 'func'),
    Q('What is the correct way to open a file for reading in Python?', 'open("file", "r")', 'read("file")', 'file.open("r")', 'open("file", "w")'),
    Q('Which statement ends a loop iteration in Python?', 'continue', 'break', 'pass', 'stop'),
    Q('What is the default port for a Django development server?', '8000', '8080', '3000', '5000'),
    Q('Which command creates a new Django project?', 'django-admin startproject', 'django startproject', 'python createproject', 'django-admin new'),
    Q('Which file contains the URL configuration of a Django app?', 'urls.py', 'views.py', 'models.py', 'settings.py'),
    Q('What is a Django model?', 'A Python class that maps to a database table', 'A view function', 'A URL pattern', 'A template file'),
    Q('Which command applies database migrations in Django?', 'python manage.py migrate', 'python manage.py runserver', 'python manage.py makemigrations', 'python manage.py collectstatic'),
    Q('Which template language does Django use by default?', 'Django template language', 'Jinja2', 'EJS', 'Handlebars'),
    Q('What is the ORM in Django?', 'Object-Relational Mapper', 'Object Request Model', 'Ordered Relational Module', 'Online Resource Manager'),
    Q('Which decorator requires login in Django?', '@login_required', '@require_login', '@authenticate', '@secure'),
    Q('What is a view in Django?', 'A function that returns a response', 'A database table', 'A template', 'A URL'),
    Q('Which Django function is used to query all records?', 'Model.objects.all()', 'Model.query()', 'Model.fetch()', 'Model.get_all()'),
    Q('What does the Django admin provide?', 'A built-in admin interface', 'A web server', 'A database', 'A compiler'),
    Q('Which Django middleware handles CSRF by default?', 'CsrfViewMiddleware', 'AuthMiddleware', 'SecurityMiddleware', 'SessionMiddleware'),
    Q('What does REST stand for?', 'Representational State Transfer', 'Remote State Transfer', 'Rapid Event State Testing', 'Reliable System Transfer'),
    Q('Which HTTP method is used to create a resource?', 'POST', 'GET', 'PUT', 'DELETE'),
    Q('Which HTTP method is used to update a resource completely?', 'PUT', 'POST', 'GET', 'PATCH'),
    Q('Which HTTP status code means success?', '200', '404', '500', '302'),
    Q('Which HTTP status code means not found?', '404', '200', '500', '301'),
    Q('What is JSON?', 'A lightweight data interchange format', 'A programming language', 'A database', 'An API'),
    Q('Which of the following is valid JSON?', '{"name": "John"}', '{name: "John"}', '{"name": John}', '<name>John</name>'),
    Q('What is the main entry point of a Java program?', 'main method', 'start method', 'init method', 'run method'),
    Q('Which keyword is used to create an object in Java?', 'new', 'create', 'object', 'make'),
    Q('What is inheritance in Java?', 'A class acquiring properties of another', 'A loop', 'A data type', 'A variable'),
    Q('Which keyword is used to inherit a class in Java?', 'extends', 'implements', 'inherits', 'super'),
    Q('Which keyword is used to implement an interface in Java?', 'implements', 'extends', 'inherits', 'uses'),
    Q('What is polymorphism in OOP?', 'The ability of objects to take many forms', 'A data structure', 'A loop', 'An exception'),
    Q('Which concept hides internal details of an object?', 'Encapsulation', 'Inheritance', 'Polymorphism', 'Abstraction'),
    Q('Which Java keyword prevents inheritance of a class?', 'final', 'static', 'private', 'abstract'),
    Q('What is a constructor in Java?', 'A method called when an object is created', 'A method to destroy objects', 'A static method', 'An interface'),
    Q('Which Java collection stores unique elements?', 'Set', 'List', 'Map', 'Queue'),
    Q('Which Java collection stores key-value pairs?', 'Map', 'List', 'Set', 'Array'),
    Q('What is an exception in Java?', 'An event that disrupts normal flow', 'A data type', 'A loop', 'A variable'),
    Q('Which keyword is used to catch an exception in Java?', 'catch', 'except', 'handle', 'grab'),
    Q('What is the base class of all Java classes?', 'Object', 'Class', 'System', 'Main'),
    Q('Which operator is used for string concatenation in Java?', '+', '&', '||', '++'),
    Q('What is a generic in Java?', 'A type that operates on other types', 'A class', 'A method', 'A variable'),
    Q('Which data type in Java stores a single character?', 'char', 'string', 'int', 'byte'),
    Q('Which of these is a wrapper class in Java?', 'Integer', 'int', 'char', 'long'),
    Q('What does the static keyword mean in Java?', 'Belongs to the class, not instances', 'Creates an object', 'Declares a constant', 'Marks a method private'),
    Q('Which Java feature allows multiple methods with the same name?', 'Overloading', 'Overriding', 'Inheritance', 'Abstraction'),
    Q('What is the size of an int in Java?', '4 bytes', '2 bytes', '8 bytes', '1 byte'),
    Q('Which keyword declares an interface in Java?', 'interface', 'contract', 'abstract', 'protocol'),
    Q('What is a lambda expression in Java?', 'An anonymous function', 'A loop', 'A class', 'A variable'),
    Q('Which C++ feature allocates memory dynamically?', 'new', 'malloc only', 'alloc', 'create'),
    Q('Which operator is used to access the value at a pointer in C++?', '*', '&', '->', '.'),
    Q('What is the STL in C++?', 'Standard Template Library', 'Standard Type Library', 'System Template Language', 'Simple Template List'),
    Q('Which STL container stores elements in sorted order?', 'set', 'vector', 'list', 'queue'),
    Q('Which C++ keyword handles runtime errors?', 'try', 'catch', 'throw', 'except'),
    Q('What is the difference between struct and class in C++?', 'Default access is public vs private', 'None', 'Struct is bigger', 'Class is faster'),
    Q('Which C++ keyword is used to inherit a class?', ':', 'extends', 'inherits', 'of'),
    Q('What is a smart pointer in C++?', 'A pointer with automatic memory management', 'A faster pointer', 'A const pointer', 'A void pointer'),
    Q('Which C++ standard introduced auto keyword?', 'C++11', 'C++98', 'C++03', 'C++14'),
    Q('What is the size of a bool in C++?', '1 byte', '4 bytes', '2 bytes', '8 bytes'),
    Q('Which C++ container is a dynamic array?', 'vector', 'set', 'map', 'stack'),
    Q('Which keyword in C++ is used to define a constant?', 'const', 'static', 'final', 'readonly'),
    Q('What is a namespace in C++?', 'A scope for identifiers', 'A class', 'A function', 'A variable'),
    Q('Which header is used for input/output in C++?', 'iostream', 'stdio.h', 'stdlib.h', 'string.h'),
    Q('What does the #include preprocessor directive do?', 'Includes a header file', 'Defines a macro', 'Declares a class', 'Starts a loop'),
    Q('Which JavaScript keyword declares a variable?', 'let', 'def', 'varible', 'int'),
    Q('Which keyword declares a constant in JavaScript?', 'const', 'static', 'final', 'let'),
    Q('What is the output of typeof null in JavaScript?', 'object', 'null', 'undefined', 'string'),
    Q('Which method converts JSON to an object in JavaScript?', 'JSON.parse()', 'JSON.stringify()', 'JSON.toObject()', 'JSON.decode()'),
    Q('Which method converts an object to JSON in JavaScript?', 'JSON.stringify()', 'JSON.parse()', 'JSON.encode()', 'JSON.serialize()'),
    Q('Which array method adds elements to the end?', 'push()', 'pop()', 'shift()', 'unshift()'),
    Q('Which array method removes the last element?', 'pop()', 'push()', 'shift()', 'splice()'),
    Q('Which method joins array elements into a string?', 'join()', 'concat()', 'merge()', 'append()'),
    Q('What is the result of 0.1 + 0.2 === 0.3 in JavaScript?', 'false', 'true', 'undefined', 'NaN'),
    Q('Which keyword defines a function in JavaScript?', 'function', 'def', 'func', 'method'),
    Q('Which operator performs strict equality in JavaScript?', '===', '==', '=', '!='),
    Q('What is the event used when a button is clicked in JavaScript?', 'click', 'mouseover', 'load', 'change'),
    Q('Which method selects an element by id in JavaScript?', 'getElementById()', 'queryByID()', 'selectId()', 'getByClass()'),
    Q('What does document.querySelector return?', 'The first matching element', 'All matching elements', 'An array of classes', 'A string'),
    Q('Which JavaScript object represents the browser window?', 'window', 'document', 'screen', 'navigator'),
    Q('What is the DOM?', 'Document Object Model', 'Data Object Model', 'Document Oriented Module', 'Dynamic Object Mapping'),
    Q('Which method adds an event listener?', 'addEventListener()', 'attachEvent()', 'listenEvent()', 'onEvent()'),
    Q('What is the result of "5" + 3 in JavaScript?', '"53"', '8', '53', 'undefined'),
    Q('What is the output of console.log(2 + "2")?', '22', '4', 'NaN', 'Error'),
    Q('Which statement is used to write to the console?', 'console.log()', 'print()', 'echo()', 'write()'),
    Q('What is a callback in JavaScript?', 'A function passed to another function', 'A loop', 'A variable', 'An error'),
    Q('What does the map() array method do?', 'Creates a new array from each element', 'Filters elements', 'Sorts elements', 'Removes duplicates'),
    Q('What is a Promise in JavaScript?', 'An object representing async completion', 'A data type', 'A loop', 'A function'),
    Q('Which SQL statement inserts data into a table?', 'INSERT INTO', 'ADD', 'CREATE', 'PUT'),
    Q('Which SQL statement updates existing data?', 'UPDATE', 'MODIFY', 'CHANGE', 'SET'),
    Q('Which SQL statement deletes records?', 'DELETE FROM', 'REMOVE', 'DROP ROW', 'TRUNCATE'),
    Q('Which SQL clause filters records?', 'WHERE', 'HAVING only', 'FILTER', 'GROUP BY'),
    Q('Which SQL keyword returns only distinct values?', 'DISTINCT', 'UNIQUE', 'ONLY', 'DIFFERENT'),
    Q('What does the SQL ORDER BY clause do?', 'Sorts results', 'Filters results', 'Groups results', 'Limits results'),
    Q('Which SQL aggregate function returns the average?', 'AVG()', 'SUM()', 'COUNT()', 'MEAN()'),
    Q('Which SQL function counts rows?', 'COUNT()', 'TOTAL()', 'ROWS()', 'SUM()'),
    Q('What is a primary key in SQL?', 'A unique identifier for each row', 'The first column', 'An index', 'A foreign key'),
    Q('Which SQL keyword joins two tables?', 'JOIN', 'MERGE', 'LINK', 'COMBINE'),
    Q('What does LEFT JOIN return?', 'All rows from left table and matches from right', 'Only matching rows', 'All rows from both', 'Nothing'),
    Q('Which SQL statement creates a new table?', 'CREATE TABLE', 'MAKE TABLE', 'NEW TABLE', 'ADD TABLE'),
    Q('What does the GROUP BY clause do?', 'Groups rows with the same values', 'Sorts rows', 'Filters rows', 'Joins tables'),
    Q('Which operator checks for null in SQL?', 'IS NULL', '= NULL', 'NULL()', 'IS EMPTY'),
    Q('What is SQL injection?', 'An attack that inserts malicious SQL', 'A database backup', 'A query optimization', 'A table index'),
]


def build_prog(rng):
    return list(PROG_CURATED) + code_output_pool()


# =====================================================================
# Mathematics
# =====================================================================

MATH_CURATED = [
    Q('What is the value of pi (approximately)?', '3.14159', '3.14159', '3.15159', '3.13159'),
    Q('What is the value of the mathematical constant e?', '2.71828', '3.14159', '2.154', '1.618'),
    Q('What is the square root of 144?', '12', '14', '11', '13'),
    Q('What is 15% of 200?', '30', '25', '35', '40'),
    Q('What is the sum of the angles of a triangle?', '180 degrees', '90 degrees', '360 degrees', '270 degrees'),
    Q('What is the area of a rectangle with length 5 and width 3?', '15', '8', '16', '12'),
    Q('What is the perimeter of a square with side 6?', '24', '36', '12', '30'),
    Q('What is the circumference of a circle with radius 7?', '43.98', '14', '21.99', '49'),
    Q('Which number is prime?', '17', '15', '21', '27'),
    Q('What is the highest common factor of 12 and 18?', '6', '3', '9', '2'),
    Q('What is the least common multiple of 4 and 6?', '12', '24', '6', '18'),
    Q('What is 2 to the power of 10?', '1024', '512', '2048', '1000'),
    Q('What is the value of 3 factorial (3!)?', '6', '3', '9', '12'),
    Q('What is 5 factorial (5!)?', '120', '100', '60', '24'),
    Q('What is 25% expressed as a decimal?', '0.25', '0.50', '2.5', '0.025'),
    Q('What is 3/4 expressed as a decimal?', '0.75', '0.50', '0.70', '0.34'),
    Q('What is the average of 4, 8 and 12?', '8', '10', '6', '12'),
    Q('What is the mode of the numbers 2, 3, 3, 5, 5, 5?', '5', '3', '2', '4'),
    Q('What is the median of 1, 3, 5, 7, 9?', '5', '3', '7', '4'),
    Q('What is the sum of the interior angles of a quadrilateral?', '360 degrees', '180 degrees', '270 degrees', '540 degrees'),
    Q('What is the value of x in the equation 2x + 4 = 10?', '3', '2', '4', '5'),
    Q('What is the slope of the line y = 3x + 2?', '3', '2', '1', '-3'),
    Q('What is the y-intercept of the line y = 2x - 5?', '-5', '2', '5', '-2'),
    Q('What is the product of 7 and 8?', '56', '54', '64', '48'),
    Q('What is 100 - 37?', '63', '73', '67', '60'),
    Q('What is the next prime number after 7?', '11', '9', '13', '10'),
    Q('What is 2 cubed (2^3)?', '8', '6', '9', '4'),
    Q('What is the value of 0 divided by 5?', '0', '5', 'Undefined', '1'),
    Q('What is the value of 5 divided by 0?', 'Undefined', '0', '5', '1'),
    Q('What is the area of a triangle with base 8 and height 5?', '20', '40', '13', '26'),
    Q('What is the formula for the area of a circle?', 'pi * r^2', 'pi * r', '2 * pi * r', 'r^2'),
    Q('What is the volume of a cube with side 3?', '27', '9', '18', '36'),
    Q('What is the square of 13?', '169', '156', '186', '139'),
    Q('What is the cube root of 27?', '3', '9', '6', '2'),
    Q('What is 99 rounded to the nearest ten?', '100', '90', '95', '99'),
    Q('What is 10% of 500?', '50', '100', '25', '5'),
    Q('What is the value of 7^2?', '49', '14', '42', '54'),
    Q('What is the reciprocal of 5?', '1/5', '5', '1/2', '0.5'),
    Q('What is the positive square root of 81?', '9', '8', '7', '11'),
    Q('What is the value of 6 + 4 * 2?', '14', '20', '16', '12'),
    Q('What is the value of (6 + 4) * 2?', '20', '14', '16', '18'),
    Q('Which of the following is an even prime number?', '2', '3', '5', '7'),
    Q('What is the sum of the first five natural numbers?', '15', '10', '20', '14'),
    Q('What is the next number in 2, 6, 12, 20?', '30', '24', '28', '26'),
    Q('What is the Fibonacci number that follows 21?', '34', '33', '42', '25'),
    Q('How many degrees are in a right angle?', '90', '180', '45', '360'),
    Q('What is 1/2 + 1/4?', '3/4', '1/3', '2/6', '1/8'),
    Q('What is the decimal expansion of 1/8?', '0.125', '0.15', '0.18', '0.20'),
    Q('What is 40% of 150?', '60', '50', '70', '75'),
    Q('What is the value of the digit 7 in the number 3721?', '700', '70', '7', '7000'),
]


def build_math(rng):
    return (list(MATH_CURATED) + arithmetic_pool(rng)
            + percent_pool(rng) + square_pool(rng) + sequence_pool(rng))


# =====================================================================
# Science
# =====================================================================

SCIENCE_CURATED = [
    Q('What is the chemical symbol for water?', 'H2O', 'HO2', 'H2', 'O2'),
    Q('What is the chemical symbol for sodium chloride?', 'NaCl', 'KCl', 'NaOH', 'HCl'),
    Q('What is the chemical symbol for carbon dioxide?', 'CO2', 'CO', 'C2O', 'CaO'),
    Q('What is the chemical symbol for gold?', 'Au', 'Ag', 'Fe', 'Go'),
    Q('What is the chemical symbol for silver?', 'Ag', 'Au', 'Si', 'Fe'),
    Q('What is the chemical symbol for iron?', 'Fe', 'Ir', 'In', 'Fr'),
    Q('What is the chemical symbol for oxygen?', 'O', 'Ox', 'Oy', 'O2'),
    Q('What is the chemical symbol for hydrogen?', 'H', 'Hy', 'Hd', 'He'),
    Q('What is the chemical symbol for helium?', 'He', 'H', 'Hm', 'He2'),
    Q('What is the chemical symbol for nitrogen?', 'N', 'Ni', 'Ng', 'Nz'),
    Q('What is the chemical symbol for calcium?', 'Ca', 'C', 'Cl', 'Cy'),
    Q('What is the chemical symbol for potassium?', 'K', 'P', 'Pt', 'Po'),
    Q('What is the pH of a neutral solution?', '7', '0', '5', '10'),
    Q('What is the atomic number of carbon?', '6', '12', '8', '4'),
    Q('What is the atomic number of oxygen?', '8', '6', '16', '2'),
    Q('What is the atomic number of hydrogen?', '1', '2', '0', '8'),
    Q('What is the atomic number of gold?', '79', '47', '29', '92'),
    Q('Which gas do humans breathe in for respiration?', 'Oxygen', 'Carbon dioxide', 'Nitrogen', 'Hydrogen'),
    Q('Which gas is exhaled by humans?', 'Carbon dioxide', 'Oxygen', 'Nitrogen', 'Helium'),
    Q('What is the powerhouse of the cell?', 'Mitochondria', 'Nucleus', 'Ribosome', 'Golgi apparatus'),
    Q('Which organelle contains the cell genetic material?', 'Nucleus', 'Mitochondria', 'Chloroplast', 'Lysosome'),
    Q('Which process do plants use to make food?', 'Photosynthesis', 'Respiration', 'Digestion', 'Fermentation'),
    Q('Which gas is released during photosynthesis?', 'Oxygen', 'Carbon dioxide', 'Nitrogen', 'Methane'),
    Q('What is the basic unit of life?', 'Cell', 'Atom', 'Tissue', 'Organ'),
    Q('How many chromosomes do humans have?', '46', '48', '44', '23'),
    Q('What is DNA made of?', 'Nucleotides', 'Amino acids', 'Fatty acids', 'Monosaccharides'),
    Q('Which blood cells fight infections?', 'White blood cells', 'Red blood cells', 'Platelets', 'Plasma'),
    Q('Which blood cells carry oxygen?', 'Red blood cells', 'White blood cells', 'Platelets', 'Neurons'),
    Q('What is the largest internal organ in the human body?', 'Liver', 'Kidney', 'Lungs', 'Heart'),
    Q('What is the normal human body temperature?', '37 degrees C', '35 degrees C', '40 degrees C', '33 degrees C'),
    Q('Which vitamin is produced by sunlight on skin?', 'Vitamin D', 'Vitamin A', 'Vitamin C', 'Vitamin B12'),
    Q('Which vitamin is found in citrus fruits?', 'Vitamin C', 'Vitamin D', 'Vitamin K', 'Vitamin B12'),
    Q('What is the unit of force?', 'Newton', 'Joule', 'Watt', 'Pascal'),
    Q('What is the unit of energy?', 'Joule', 'Newton', 'Watt', 'Pascal'),
    Q('What is the unit of power?', 'Watt', 'Joule', 'Newton', 'Ohm'),
    Q('What is the unit of electric current?', 'Ampere', 'Volt', 'Ohm', 'Watt'),
    Q('What is the unit of electric potential difference?', 'Volt', 'Ampere', 'Ohm', 'Coulomb'),
    Q('What is the unit of electrical resistance?', 'Ohm', 'Volt', 'Ampere', 'Watt'),
    Q('What is the speed of sound in air approximately?', '343 m/s', '150 m/s', '600 m/s', '1000 m/s'),
    Q('Which force pulls objects towards the Earth?', 'Gravity', 'Magnetism', 'Friction', 'Tension'),
    Q('What is Newtons third law of motion?', 'For every action there is an equal and opposite reaction', 'Objects in motion stay in motion', 'F = ma', 'Energy cannot be created'),
    Q('What is the formula for Newtons second law?', 'F = ma', 'E = mc^2', 'V = IR', 'W = Fd'),
    Q('What is the SI unit of mass?', 'Kilogram', 'Gram', 'Newton', 'Pound'),
    Q('What is the SI unit of length?', 'Metre', 'Centimetre', 'Kilometre', 'Foot'),
    Q('What is the SI unit of time?', 'Second', 'Minute', 'Hour', 'Millisecond'),
    Q('What is the SI unit of temperature?', 'Kelvin', 'Celsius', 'Fahrenheit', 'Rankine'),
    Q('Which particle has a negative charge?', 'Electron', 'Proton', 'Neutron', 'Photon'),
    Q('Which particle has a positive charge?', 'Proton', 'Electron', 'Neutron', 'Muon'),
    Q('Which particle is neutral?', 'Neutron', 'Proton', 'Electron', 'Positron'),
    Q('What does a catalyst do?', 'Speeds up a reaction', 'Slows a reaction', 'Stops a reaction', 'Absorbs heat'),
    Q('What is the most common element in the universe?', 'Hydrogen', 'Oxygen', 'Helium', 'Carbon'),
    Q('What is the most common element in the Earth crust?', 'Oxygen', 'Silicon', 'Iron', 'Aluminium'),
    Q('Which metal is used in batteries?', 'Lithium', 'Gold', 'Silver', 'Tungsten'),
    Q('What is rust?', 'Iron oxide', 'Copper sulphate', 'Aluminium oxide', 'Zinc carbonate'),
    Q('What is the process of a solid turning into a gas called?', 'Sublimation', 'Evaporation', 'Condensation', 'Melting'),
    Q('What is the process of a gas turning into a liquid called?', 'Condensation', 'Evaporation', 'Sublimation', 'Freezing'),
    Q('What is the process of a liquid turning into a gas called?', 'Evaporation', 'Condensation', 'Freezing', 'Sublimation'),
    Q('At what temperature does water boil at sea level?', '100 degrees C', '90 degrees C', '110 degrees C', '120 degrees C'),
    Q('Which organ pumps deoxygenated blood to the lungs?', 'Right ventricle', 'Left ventricle', 'Right atrium', 'Aorta'),
    Q('What is the main function of the kidneys?', 'Filtering blood', 'Pumping blood', 'Digesting food', 'Producing hormones only'),
    Q('Which acid is found in the stomach?', 'Hydrochloric acid', 'Sulphuric acid', 'Nitric acid', 'Acetic acid'),
    Q('Which of these is a fossil fuel?', 'Coal', 'Sunlight', 'Wind', 'Water'),
    Q('Which renewable energy source uses the sun?', 'Solar power', 'Coal power', 'Gas power', 'Nuclear fission'),
    Q('What is the chemical formula of methane?', 'CH4', 'CO2', 'C2H6', 'NH3'),
    Q('What is the chemical formula of ammonia?', 'NH3', 'NO2', 'CH4', 'H2O'),
    Q('What is the chemical formula of common salt?', 'NaCl', 'KCl', 'CaCl2', 'NaOH'),
    Q('Which of the following is an acid?', 'Vinegar', 'Baking soda', 'Soap', 'Detergent'),
    Q('Which of the following is a base?', 'Baking soda', 'Lemon juice', 'Vinegar', 'Cola'),
    Q('What is the main component of natural gas?', 'Methane', 'Ethane', 'Propane', 'Butane'),
    Q('Which planet has a ring system?', 'Saturn', 'Mercury', 'Venus', 'Mars'),
    Q('Which star is closest to Earth?', 'The Sun', 'Proxima Centauri', 'Sirius', 'Alpha Centauri'),
    Q('What causes day and night?', 'Rotation of the Earth', 'Revolution of the Earth', 'Tilt of the Earth', 'Moon gravity'),
    Q('What causes seasons?', 'The tilt of the Earth axis', 'Distance from the Sun', 'Earth rotation', 'Moon phases'),
    Q('How long does Earth take to orbit the Sun?', '365.25 days', '365 days', '360 days', '400 days'),
    Q('What is the phenomenon of light bending called?', 'Refraction', 'Reflection', 'Diffusion', 'Absorption'),
    Q('What is a rainbow caused by?', 'Refraction and reflection of light', 'Diffraction only', 'Absorption', 'Polarization'),
    Q('Which colour has the longest wavelength?', 'Red', 'Blue', 'Green', 'Violet'),
    Q('Which colour has the shortest wavelength?', 'Violet', 'Red', 'Orange', 'Yellow'),
    Q('What is the study of living organisms called?', 'Biology', 'Chemistry', 'Physics', 'Geology'),
    Q('What is the study of matter and its reactions called?', 'Chemistry', 'Biology', 'Physics', 'Astronomy'),
    Q('What is the study of motion and energy called?', 'Physics', 'Chemistry', 'Biology', 'Geography'),
    Q('Which scientist proposed the theory of evolution?', 'Charles Darwin', 'Isaac Newton', 'Galileo Galilei', 'Albert Einstein'),
    Q('What is the largest organ in the human body?', 'Skin', 'Liver', 'Brain', 'Lungs'),
    Q('How many chambers does the human heart have?', '4', '2', '3', '5'),
    Q('What is the function of red blood cells?', 'Carry oxygen', 'Clot blood', 'Fight infection', 'Produce insulin'),
    Q('Which gland regulates metabolism?', 'Thyroid', 'Pituitary', 'Adrenal', 'Pancreas'),
    Q('What is the main sugar in blood?', 'Glucose', 'Fructose', 'Sucrose', 'Lactose'),
    Q('What is the formula for gravitational potential energy?', 'mgh', '1/2 mv^2', 'F = ma', 'E = mc^2'),
    Q('What is the formula for kinetic energy?', '1/2 mv^2', 'mgh', 'mv', 'mg/h'),
    Q('What is the acceleration due to gravity on Earth?', '9.8 m/s^2', '8.9 m/s^2', '10.8 m/s^2', '6.7 m/s^2'),
    Q('Which law states that energy cannot be created or destroyed?', 'First law of thermodynamics', 'Second law of thermodynamics', 'Newtons first law', 'Ohms law'),
    Q('What is an isotope?', 'Atoms with the same protons but different neutrons', 'Atoms with different protons', 'A type of molecule', 'A charged atom'),
    Q('What is an ion?', 'A charged atom', 'A neutral atom', 'A molecule', 'A neutron'),
    Q('What is the atomic mass of carbon?', '12', '6', '8', '14'),
    Q('Which noble gas is used in balloons?', 'Helium', 'Neon', 'Argon', 'Xenon'),
    Q('Which gas makes up about 78% of the atmosphere?', 'Nitrogen', 'Oxygen', 'Carbon dioxide', 'Argon'),
    Q('Which gas makes up about 21% of the atmosphere?', 'Oxygen', 'Nitrogen', 'Carbon dioxide', 'Hydrogen'),
    Q('What is the greenhouse effect primarily caused by?', 'Greenhouse gases', 'Oxygen', 'Nitrogen', 'Helium'),
    Q('Which of the following is a greenhouse gas?', 'Carbon dioxide', 'Oxygen', 'Nitrogen', 'Argon'),
    Q('What is the main cause of global warming?', 'Increase in greenhouse gases', 'Solar flares', 'Moon phases', 'Earth tilt'),
    Q('What is acid rain caused by?', 'Pollutants like sulfur and nitrogen oxides', 'Rainfall only', 'Wind', 'Temperature'),
    Q('What is the ozone layer?', 'A layer that absorbs UV radiation', 'A layer of clouds', 'The ocean surface', 'A layer of ice'),
    Q('Which particle is found in the nucleus of an atom?', 'Proton', 'Electron', 'Photon', 'Graviton'),
    Q('What are the three states of matter?', 'Solid, liquid, gas', 'Solid, soft, hard', 'Wet, dry, damp', 'Hot, cold, warm'),
    Q('What is the process of water turning into ice called?', 'Freezing', 'Melting', 'Condensation', 'Sublimation'),
    Q('What is the process of ice turning into water called?', 'Melting', 'Freezing', 'Evaporation', 'Condensation'),
    Q('What is a compound?', 'A substance made of two or more elements', 'A single element', 'A mixture only', 'An isotope'),
    Q('What is a pure substance made of only one type of atom?', 'Element', 'Compound', 'Mixture', 'Solution'),
    Q('What is the boiling point of water in Fahrenheit?', '212', '100', '180', '250'),
    Q('What is the freezing point of water in Fahrenheit?', '32', '0', '100', '212'),
    Q('What is the chemical symbol of lead?', 'Pb', 'Ld', 'Le', 'Pl'),
    Q('What is the chemical symbol of copper?', 'Cu', 'Co', 'Cp', 'Ce'),
    Q('What is the chemical symbol of zinc?', 'Zn', 'Zi', 'Ze', 'Zc'),
    Q('What is the chemical symbol of potassium?', 'K', 'P', 'Po', 'Ka'),
    Q('What is the chemical symbol of aluminium?', 'Al', 'Am', 'Au', 'Ar'),
    Q('Which is the lightest element?', 'Hydrogen', 'Helium', 'Lithium', 'Oxygen'),
    Q('What is the hardest known mineral?', 'Diamond', 'Quartz', 'Topaz', 'Corundum'),
    Q('Which metal is a liquid at room temperature?', 'Mercury', 'Lead', 'Zinc', 'Aluminium'),
    Q('What is the study of earthquakes called?', 'Seismology', 'Geology', 'Meteorology', 'Hydrology'),
    Q('What is the outer layer of the Earth called?', 'Crust', 'Mantle', 'Core', 'Magma'),
    Q('Which layer of the Earth is liquid?', 'Outer core', 'Crust', 'Mantle', 'Inner core'),
]


def build_science(rng):
    return list(SCIENCE_CURATED)


# =====================================================================
# History
# =====================================================================

HISTORY_CURATED = [
    Q('The Great Pyramid of Giza was built for which pharaoh?', 'Khufu', 'Tutankhamun', 'Ramses II', 'Akhenaten'),
    Q('Which ancient civilization built Machu Picchu?', 'Inca', 'Aztec', 'Maya', 'Olmec'),
    Q('The Roman Colosseum was primarily used for what?', 'Gladiatorial contests', 'Religious ceremonies', 'Government meetings', 'Public libraries'),
    Q('Which empire built the Great Wall of China?', 'Ming Dynasty', 'Mongol Empire', 'Han Dynasty', 'Tang Dynasty'),
    Q('Socrates, Plato and Aristotle were philosophers from which country?', 'Greece', 'Rome', 'Egypt', 'Persia'),
    Q('Who was the first Emperor of Rome?', 'Augustus', 'Julius Caesar', 'Nero', 'Constantine'),
    Q('In which year did World War II begin?', '1939', '1914', '1945', '1941'),
    Q('In which year did World War II end?', '1945', '1939', '1944', '1918'),
    Q('Which country was led by Adolf Hitler during World War II?', 'Germany', 'Italy', 'Japan', 'Austria'),
    Q('What was the name of the Allied invasion of Normandy in 1944?', 'D-Day', 'Operation Barbarossa', 'Battle of Britain', 'Pearl Harbor'),
    Q('Which battle is considered a turning point in the Pacific during WWII?', 'Midway', 'Stalingrad', 'Normandy', 'El Alamein'),
    Q('Which event triggered the start of World War I?', 'Assassination of Archduke Franz Ferdinand', 'Invasion of Poland', 'Sinking of Lusitania', 'Russian Revolution'),
    Q('The Treaty of Versailles ended which war?', 'World War I', 'World War II', 'Franco-Prussian War', 'Crimean War'),
    Q('Who was the leader of the Soviet Union during most of World War II?', 'Joseph Stalin', 'Vladimir Lenin', 'Leon Trotsky', 'Nikita Khrushchev'),
    Q('Which city was bombed with the first atomic bomb?', 'Hiroshima', 'Nagasaki', 'Tokyo', 'Kyoto'),
    Q('The Mughal Empire was founded by whom?', 'Babur', 'Akbar', 'Shah Jahan', 'Aurangzeb'),
    Q('Who built the Taj Mahal?', 'Shah Jahan', 'Akbar', 'Babur', 'Jahangir'),
    Q('Which Mughal emperor is known for religious tolerance?', 'Akbar', 'Aurangzeb', 'Shah Jahan', 'Babur'),
    Q('The Mughal Empire was centered in which modern country?', 'India', 'Pakistan only', 'Afghanistan', 'Iran'),
    Q('Which Mughal emperor built the city of Fatehpur Sikri?', 'Akbar', 'Babur', 'Humayun', 'Aurangzeb'),
    Q('Which Mughal emperor built the Red Fort in Delhi?', 'Shah Jahan', 'Akbar', 'Babur', 'Aurangzeb'),
    Q('The French Revolution began in which year?', '1789', '1776', '1804', '1815'),
    Q('What was the Bastille?', 'A prison in Paris', 'A royal palace', 'A cathedral', 'A fortress gate'),
    Q('Who was the leader of France during the Revolution who later became Emperor?', 'Napoleon Bonaparte', 'Louis XVI', 'Robespierre', 'Danton'),
    Q('Which document declared the rights of citizens during the French Revolution?', 'Declaration of the Rights of Man', 'Magna Carta', 'Bill of Rights', 'US Constitution'),
    Q('Who was the king of France during the French Revolution?', 'Louis XVI', 'Louis XIV', 'Charles IX', 'Henry IV'),
    Q('The French Revolution was inspired by which earlier revolution?', 'American Revolution', 'Industrial Revolution', 'Russian Revolution', 'Glorious Revolution'),
    Q('What was the Reign of Terror in France associated with?', 'Maximilien Robespierre', 'Napoleon Bonaparte', 'Louis XVI', 'Charlotte Corday'),
    Q('Who was the Egyptian queen who allied with Julius Caesar?', 'Cleopatra', 'Nefertiti', 'Hatshepsut', 'Isis'),
    Q('Which civilization is known for hieroglyphics?', 'Ancient Egypt', 'Ancient Greece', 'Ancient Rome', 'Maya'),
    Q('Which civilization invented the wheel?', 'Sumerians', 'Romans', 'Greeks', 'Egyptians'),
    Q('The city of Rome was founded according to legend by whom?', 'Romulus and Remus', 'Julius Caesar', 'Aeneas', 'Augustus'),
    Q('Which Roman general crossed the Rubicon?', 'Julius Caesar', 'Pompey', 'Hannibal', 'Augustus'),
    Q('Which civilization built the city of Tenochtitlan?', 'Aztec', 'Inca', 'Maya', 'Toltec'),
    Q('Which explorer reached the Americas in 1492?', 'Christopher Columbus', 'Vasco da Gama', 'Ferdinand Magellan', 'Amerigo Vespucci'),
    Q('Who was the first European to sail around the world (expedition)?', 'Ferdinand Magellan', 'Christopher Columbus', 'James Cook', 'Marco Polo'),
    Q('The Renaissance began in which country?', 'Italy', 'France', 'England', 'Spain'),
    Q('Who painted the Mona Lisa?', 'Leonardo da Vinci', 'Michelangelo', 'Raphael', 'Donatello'),
    Q('Who sculpted the statue of David?', 'Michelangelo', 'Leonardo da Vinci', 'Raphael', 'Botticelli'),
    Q('The Industrial Revolution began in which country?', 'Great Britain', 'France', 'Germany', 'United States'),
    Q('Who invented the steam engine that powered the Industrial Revolution?', 'James Watt', 'Thomas Newcomen', 'James Hargreaves', 'Richard Arkwright'),
    Q('Which scientist developed the theory of gravity?', 'Isaac Newton', 'Albert Einstein', 'Galileo Galilei', 'Charles Darwin'),
    Q('Who developed the heliocentric model of the solar system?', 'Nicolaus Copernicus', 'Ptolemy', 'Tycho Brahe', 'Johannes Kepler'),
    Q('Which war is known as the war between the North and South in the US?', 'American Civil War', 'Revolutionary War', 'War of 1812', 'Spanish-American War'),
    Q('Who was the US president during the American Civil War?', 'Abraham Lincoln', 'George Washington', 'Thomas Jefferson', 'Andrew Jackson'),
    Q('In which year did the American Revolution begin?', '1775', '1776', '1783', '1765'),
    Q('What was the Boston Tea Party a protest against?', 'Taxation', 'Slavery', 'Suffrage', 'Conscription'),
    Q('Which empire was ruled by Genghis Khan?', 'Mongol Empire', 'Ottoman Empire', 'Roman Empire', 'Persian Empire'),
    Q('The Silk Road connected which two regions?', 'China and the Mediterranean', 'India and Africa', 'Rome and Egypt', 'Europe and the Americas'),
    Q('Which ancient wonder stood in the city of Babylon?', 'Hanging Gardens', 'Colossus of Rhodes', 'Temple of Artemis', 'Lighthouse of Alexandria'),
    Q('The Parthenon is located in which city?', 'Athens', 'Rome', 'Sparta', 'Corinth'),
    Q('Who was Alexander the Greats teacher?', 'Aristotle', 'Plato', 'Socrates', 'Homer'),
    Q('Alexander the Great was king of which ancient kingdom?', 'Macedon', 'Persia', 'Egypt', 'Greece'),
    Q('The Roman Empire fell in which year (Western)?', '476 AD', '410 AD', '500 AD', '1453 AD'),
    Q('The Byzantine Empire had its capital in which city?', 'Constantinople', 'Rome', 'Athens', 'Antioch'),
    Q('Which empire built the Suez Canal?', 'British and French', 'Ottoman', 'Persian', 'Egyptian only'),
    Q('Who was known as the Father of History?', 'Herodotus', 'Thucydides', 'Plutarch', 'Livy'),
    Q('The Magna Carta was signed in which country?', 'England', 'France', 'Spain', 'Germany'),
    Q('In which year was the Magna Carta signed?', '1215', '1066', '1492', '1776'),
    Q('The Norman Conquest of England happened in which year?', '1066', '1215', '1485', '1060'),
    Q('Who led the Norman Conquest of England?', 'William the Conqueror', 'Harold Godwinson', 'Henry II', 'Richard I'),
    Q('The Hundred Years War was between which two countries?', 'England and France', 'England and Spain', 'France and Germany', 'Spain and Portugal'),
    Q('Who was Joan of Arc?', 'A French heroine of the Hundred Years War', 'An English queen', 'A Roman empress', 'A Norse warrior'),
    Q('The Spanish Armada was defeated by which country?', 'England', 'France', 'Portugal', 'Netherlands'),
    Q('In which year was the Spanish Armada defeated?', '1588', '1492', '1600', '1550'),
    Q('Which country first colonized India for trade?', 'Portugal', 'England', 'France', 'Netherlands'),
    Q('Who was the last Mughal emperor?', 'Bahadur Shah II', 'Aurangzeb', 'Shah Jahan', 'Jahangir'),
    Q('The Indian Rebellion of 1857 was against whom?', 'British East India Company', 'Mughal Empire', 'Portuguese', 'French'),
    Q('Who founded the Maurya Empire?', 'Chandragupta Maurya', 'Ashoka', 'Bindusara', 'Harsha'),
    Q('Which emperor converted to Buddhism after a great war?', 'Ashoka', 'Chandragupta', 'Harsha', 'Samudragupta'),
    Q('The Renaissance artist Leonardo da Vinci was from which city?', 'Florence', 'Venice', 'Milan', 'Naples'),
    Q('The ancient city of Pompeii was destroyed by which volcano?', 'Mount Vesuvius', 'Mount Etna', 'Mount Fuji', 'Mount St Helens'),
    Q('Which empire was known for its roads and Latin language?', 'Roman Empire', 'Greek Empire', 'Egyptian Empire', 'Persian Empire'),
    Q('Who was the first Roman Emperor?', 'Augustus', 'Julius Caesar', 'Nero', 'Trajan'),
    Q('The Cold War was primarily between which two superpowers?', 'USA and USSR', 'USA and China', 'UK and France', 'USSR and China'),
    Q('In which year did the Berlin Wall fall?', '1989', '1991', '1985', '1990'),
    Q('The Soviet Union dissolved in which year?', '1991', '1989', '1990', '1995'),
    Q('Who was the first man in space?', 'Yuri Gagarin', 'Neil Armstrong', 'John Glenn', 'Alan Shepard'),
    Q('The Apollo 11 mission landed on the Moon in which year?', '1969', '1965', '1972', '1961'),
    Q('Who was the second man to walk on the Moon?', 'Buzz Aldrin', 'Michael Collins', 'Pete Conrad', 'Alan Bean'),
    Q('Which country was the first to reach the South Pole?', 'Norway', 'United Kingdom', 'United States', 'Russia'),
    Q('Who led the first expedition to the South Pole?', 'Roald Amundsen', 'Robert Scott', 'Ernest Shackleton', 'Edmund Hillary'),
    Q('Who was the first person to climb Mount Everest?', 'Edmund Hillary', 'Tenzing Norgay', 'Reinhold Messner', 'George Mallory'),
    Q('The United Nations was founded in which year?', '1945', '1919', '1939', '1950'),
    Q('Which city hosted the first modern Olympic Games in 1896?', 'Athens', 'Paris', 'London', 'Rome'),
    Q('Who wrote the famous book "The Prince" about political power?', 'Niccolo Machiavelli', 'Thomas Hobbes', 'John Locke', 'Voltaire'),
    Q('The Enlightenment era is associated with which century?', '18th century', '16th century', '20th century', '12th century'),
    Q('Which philosopher wrote "Leviathan"?', 'Thomas Hobbes', 'John Locke', 'Jean-Jacques Rousseau', 'Montesquieu'),
    Q('Who proposed the theory of separation of powers?', 'Montesquieu', 'Rousseau', 'Voltaire', 'Hobbes'),
    Q('The French revolutionary slogan was what?', 'Liberty, Equality, Fraternity', 'Peace, Order, Justice', 'Faith, Hope, Charity', 'Power, Glory, Honor'),
    Q('Which king was executed during the French Revolution?', 'Louis XVI', 'Louis XIV', 'Charles I', 'Napoleon III'),
    Q('Who was the ruler of the Ottoman Empire during its peak?', 'Suleiman the Magnificent', 'Osman I', 'Mehmed II', 'Selim I'),
    Q('The Ottoman Empire was centered in which modern country?', 'Turkey', 'Greece', 'Iran', 'Saudi Arabia'),
    Q('Which battle marked the end of Napoleon reign in 1815?', 'Waterloo', 'Austerlitz', 'Borodino', 'Trafalgar'),
    Q('The British East India Company established which city?', 'Madras', 'Delhi', 'Agra', 'Allahabad'),
    Q('Who was the founder of the Sikh Empire?', 'Ranjit Singh', 'Guru Nanak', 'Banda Singh', 'Hari Singh'),
    Q('The Roman Republic was overthrown by whom?', 'Julius Caesar', 'Augustus', 'Cicero', 'Pompey'),
    Q('Which civilization is credited with democracy?', 'Ancient Greece', 'Ancient Rome', 'Ancient Egypt', 'Babylon'),
    Q('The ancient Olympics were held in honor of which god?', 'Zeus', 'Apollo', 'Poseidon', 'Athena'),
    Q('The Vikings originated from which region?', 'Scandinavia', 'Germany', 'Russia', 'Iceland'),
    Q('Which explorer discovered the sea route to India in 1498?', 'Vasco da Gama', 'Christopher Columbus', 'Ferdinand Magellan', 'Bartolomeu Dias'),
    Q('Who circumnavigated the globe first (as an individual)?', 'Juan Sebastian Elcano', 'Ferdinand Magellan', 'James Cook', 'Francis Drake'),
    Q('The Aztec capital Tenochtitlan is now which modern city?', 'Mexico City', 'Lima', 'Bogota', 'Guatemala City'),
    Q('Which civilization built the city of Cusco?', 'Inca', 'Aztec', 'Maya', 'Chimu'),
    Q('Who was the famous female pharaoh of Egypt?', 'Hatshepsut', 'Cleopatra', 'Nefertiti', 'Isis'),
    Q('The Rosetta Stone helped decipher which script?', 'Egyptian hieroglyphs', 'Cuneiform', 'Linear B', 'Sanskrit'),
    Q('Which dynasty built the Terracotta Army?', 'Qin Dynasty', 'Han Dynasty', 'Ming Dynasty', 'Tang Dynasty'),
    Q('Who was the first emperor of unified China?', 'Qin Shi Huang', 'Liu Bang', 'Kublai Khan', 'Wu Zetian'),
    Q('The ancient trade route across the Sahara was called what?', 'Trans-Saharan trade', 'Silk Road', 'Spice Route', 'Amber Road'),
    Q('Which kingdom was known as the Land of the Rising Sun?', 'Japan', 'China', 'Korea', 'Thailand'),
    Q('The Meiji Restoration modernized which country?', 'Japan', 'China', 'Korea', 'Thailand'),
    Q('Who was the first President of the United States?', 'George Washington', 'John Adams', 'Thomas Jefferson', 'Abraham Lincoln'),
    Q('The Declaration of Independence was signed in which year?', '1776', '1775', '1789', '1800'),
    Q('Which country gifted the Statue of Liberty to the USA?', 'France', 'Spain', 'United Kingdom', 'Netherlands'),
    Q('The Titanic sank in which year?', '1912', '1910', '1915', '1905'),
    Q('The first newspaper was published in which country?', 'Germany', 'England', 'France', 'Italy'),
    Q('Who discovered the New World for Europe in 1492?', 'Christopher Columbus', 'Leif Erikson', 'James Cook', 'Hernan Cortes'),
    Q('Which ruler built the city of Persepolis?', 'Darius the Great', 'Cyrus the Great', 'Xerxes', 'Alexander'),
    Q('The Persian Empire was founded by whom?', 'Cyrus the Great', 'Darius the Great', 'Xerxes', 'Cambyses'),
]


def build_history(rng):
    return list(HISTORY_CURATED)


# =====================================================================
# Geography
# =====================================================================

GEO_CAPITALS = [
    ('France', 'Paris'), ('Germany', 'Berlin'), ('Italy', 'Rome'), ('Spain', 'Madrid'),
    ('Portugal', 'Lisbon'), ('Netherlands', 'Amsterdam'), ('Belgium', 'Brussels'),
    ('Switzerland', 'Bern'), ('Austria', 'Vienna'), ('Sweden', 'Stockholm'),
    ('Norway', 'Oslo'), ('Denmark', 'Copenhagen'), ('Finland', 'Helsinki'),
    ('Iceland', 'Reykjavik'), ('Ireland', 'Dublin'), ('Poland', 'Warsaw'),
    ('Czech Republic', 'Prague'), ('Hungary', 'Budapest'), ('Greece', 'Athens'),
    ('Romania', 'Bucharest'), ('Ukraine', 'Kyiv'), ('Russia', 'Moscow'),
    ('Turkey', 'Ankara'), ('Egypt', 'Cairo'), ('Nigeria', 'Abuja'),
    ('Kenya', 'Nairobi'), ('South Africa', 'Pretoria'), ('Morocco', 'Rabat'),
    ('China', 'Beijing'), ('Japan', 'Tokyo'), ('South Korea', 'Seoul'),
    ('India', 'New Delhi'), ('Pakistan', 'Islamabad'), ('Bangladesh', 'Dhaka'),
    ('Thailand', 'Bangkok'), ('Vietnam', 'Hanoi'), ('Indonesia', 'Jakarta'),
    ('Malaysia', 'Kuala Lumpur'), ('Philippines', 'Manila'),
    ('Saudi Arabia', 'Riyadh'), ('United Arab Emirates', 'Abu Dhabi'),
    ('Iran', 'Tehran'), ('Iraq', 'Baghdad'), ('Israel', 'Jerusalem'),
]

GEO_RIVERS = [
    ('Nile', 'Africa'), ('Amazon', 'South America'), ('Yangtze', 'China'),
    ('Mississippi', 'United States'), ('Ganges', 'India'), ('Danube', 'Europe'),
    ('Volga', 'Russia'), ('Congo', 'Africa'), ('Mekong', 'Southeast Asia'),
    ('Thames', 'England'), ('Seine', 'France'), ('Rhine', 'Europe'),
    ('Indus', 'South Asia'), ('Brahmaputra', 'Asia'), ('Yukon', 'North America'),
    ('Colorado', 'United States'), ('Tigris', 'Iraq'), ('Euphrates', 'Iraq'),
    ('Niger', 'Africa'), ('Zambezi', 'Africa'), ('Lena', 'Russia'),
    ('Ob', 'Russia'), ('Murrumbidgee', 'Australia'), ('Rio Grande', 'North America'),
]

GEO_MOUNTAINS = [
    ('Everest', 'Himalayas'), ('K2', 'Karakoram'), ('Kangchenjunga', 'Himalayas'),
    ('Denali', 'Alaska'), ('Kilimanjaro', 'Africa'), ('Elbrus', 'Europe'),
    ('Mont Blanc', 'Alps'), ('Aconcagua', 'Andes'), ('Fuji', 'Japan'),
    ('Matterhorn', 'Alps'), ('Everest', 'Asia'), ('McKinley', 'North America'),
]

GEO_CURATED = [
    Q('What is the largest continent by area?', 'Asia', 'Africa', 'North America', 'Europe'),
    Q('Which continent is known as the Dark Continent?', 'Africa', 'Asia', 'South America', 'Australia'),
    Q('What is the smallest continent?', 'Australia', 'Europe', 'Antarctica', 'South America'),
    Q('Which ocean is the largest?', 'Pacific Ocean', 'Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean'),
    Q('Which ocean is the deepest?', 'Pacific Ocean', 'Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean'),
    Q('The Sahara Desert is in which continent?', 'Africa', 'Asia', 'Australia', 'South America'),
    Q('Which is the largest desert in Asia?', 'Gobi Desert', 'Thar Desert', 'Arabian Desert', 'Karakum'),
    Q('Which country has the longest coastline?', 'Canada', 'Australia', 'Russia', 'Indonesia'),
    Q('What is the capital of Australia?', 'Canberra', 'Sydney', 'Melbourne', 'Perth'),
    Q('Which is the longest river in the world?', 'Nile', 'Amazon', 'Yangtze', 'Mississippi'),
    Q('Which river flows through Cairo?', 'Nile', 'Amazon', 'Tigris', 'Jordan'),
    Q('Mount Kilimanjaro is located in which country?', 'Tanzania', 'Kenya', 'Uganda', 'Ethiopia'),
    Q('Which country is the largest by population?', 'India', 'China', 'United States', 'Indonesia'),
    Q('Which country is the most populous in Africa?', 'Nigeria', 'Ethiopia', 'Egypt', 'South Africa'),
    Q('The Amazon rainforest is mostly in which country?', 'Brazil', 'Peru', 'Colombia', 'Venezuela'),
    Q('Which is the highest capital city in the world?', 'La Paz', 'Bogota', 'Kathmandu', 'Quito'),
    Q('Which strait separates Asia and North America?', 'Bering Strait', 'Gibraltar', 'Malacca', 'Hormuz'),
    Q('Which canal connects the Mediterranean and Red Sea?', 'Suez Canal', 'Panama Canal', 'Kiel Canal', 'Corinth Canal'),
    Q('Which canal connects the Atlantic and Pacific Oceans?', 'Panama Canal', 'Suez Canal', 'Kiel Canal', 'Suez'),
    Q('Which country is known as the Land of the Rising Sun?', 'Japan', 'China', 'South Korea', 'Thailand'),
    Q('Which country is known as the Land Down Under?', 'Australia', 'New Zealand', 'South Africa', 'Brazil'),
    Q('Which is the largest island country?', 'Indonesia', 'Japan', 'Philippines', 'Madagascar'),
    Q('Which country has the most volcanoes?', 'Indonesia', 'Japan', 'Italy', 'Iceland'),
    Q('The Great Barrier Reef is located off which country?', 'Australia', 'Mexico', 'Belize', 'Philippines'),
    Q('Which is the largest lake in the world?', 'Caspian Sea', 'Lake Superior', 'Lake Victoria', 'Lake Baikal'),
    Q('Which is the deepest freshwater lake?', 'Lake Baikal', 'Lake Superior', 'Lake Tanganyika', 'Caspian Sea'),
    Q('The Himalayas are located in which continent?', 'Asia', 'Europe', 'Africa', 'South America'),
    Q('Which is the highest mountain in Africa?', 'Kilimanjaro', 'Mount Kenya', 'Atlas', 'Rwenzori'),
    Q('Which country contains the Amazon rainforest?', 'Brazil', 'Argentina', 'Chile', 'Uruguay'),
    Q('The Andes mountain range is in which continent?', 'South America', 'North America', 'Asia', 'Europe'),
    Q('Which is the second largest country by area?', 'Canada', 'China', 'United States', 'Australia'),
    Q('Which is the largest country in South America?', 'Brazil', 'Argentina', 'Peru', 'Colombia'),
    Q('Which European country has the most countries bordering it?', 'Germany', 'France', 'Poland', 'Italy'),
    Q('The equator passes through which of these countries?', 'Brazil', 'Mexico', 'China', 'Australia'),
    Q('Which country is the worlds largest producer of coffee?', 'Brazil', 'Colombia', 'Vietnam', 'Ethiopia'),
    Q('Which desert is the driest on Earth?', 'Atacama', 'Sahara', 'Gobi', 'Namib'),
    Q('Which is the largest city in the world by population?', 'Tokyo', 'Delhi', 'Shanghai', 'Mumbai'),
    Q('The Dead Sea borders which two countries?', 'Israel and Jordan', 'Israel and Egypt', 'Jordan and Saudi Arabia', 'Lebanon and Syria'),
    Q('Which is the saltiest ocean?', 'Atlantic Ocean', 'Pacific Ocean', 'Indian Ocean', 'Arctic Ocean'),
    Q('The Mediterranean Sea connects to the Atlantic via which strait?', 'Strait of Gibraltar', 'Bosporus', 'Hormuz', 'Malacca'),
    Q('Which country is home to the volcano Mount Etna?', 'Italy', 'Greece', 'Spain', 'Portugal'),
    Q('Which is the longest mountain range in the world?', 'Andes', 'Rockies', 'Himalayas', 'Alps'),
    Q('Which country has the most time zones?', 'France', 'Russia', 'United States', 'China'),
    Q('The Prime Meridian passes through which city?', 'London', 'Paris', 'Berlin', 'Madrid'),
    Q('Which country is the worlds largest producer of oil?', 'United States', 'Saudi Arabia', 'Russia', 'Iran'),
]


def build_geography(rng):
    return (lookup_pool(rng, GEO_CAPITALS, 'What is the capital of {}?')
            + lookup_pool(rng, GEO_RIVERS, 'The {} river is located on which continent or country?')
            + list(GEO_CURATED))


# =====================================================================
# English
# =====================================================================

EN_SYNONYMS = [
    ('abundant', 'plentiful', 'scarce', 'rare', 'faint'),
    ('begin', 'commence', 'conclude', 'finish', 'cease'),
    ('brave', 'courageous', 'cowardly', 'timid', 'fearful'),
    ('calm', 'tranquil', 'agitated', 'stormy', 'chaotic'),
    ('clever', 'intelligent', 'foolish', 'dull', 'simple'),
    ('cold', 'frigid', 'boiling', 'hot', 'warm'),
    ('complete', 'finish', 'start', 'begin', 'open'),
    ('correct', 'accurate', 'wrong', 'flawed', 'false'),
    ('dangerous', 'hazardous', 'safe', 'secure', 'harmless'),
    ('difficult', 'challenging', 'easy', 'simple', 'trivial'),
    ('eager', 'keen', 'reluctant', 'hesitant', 'unwilling'),
    ('easy', 'simple', 'hard', 'complex', 'tough'),
    ('fast', 'quick', 'slow', 'sluggish', 'leisurely'),
    ('happy', 'joyful', 'sad', 'gloomy', 'miserable'),
    ('honest', 'sincere', 'dishonest', 'deceitful', 'fake'),
    ('hungry', 'ravenous', 'satisfied', 'full', 'stuffed'),
    ('important', 'crucial', 'trivial', 'minor', 'negligible'),
    ('large', 'huge', 'tiny', 'small', 'miniature'),
    ('lonely', 'isolated', 'crowded', 'popular', 'social'),
    ('loud', 'noisy', 'quiet', 'silent', 'hushed'),
    ('mad', 'angry', 'calm', 'peaceful', 'composed'),
    ('neat', 'tidy', 'messy', 'untidy', 'disorderly'),
    ('old', 'ancient', 'modern', 'new', 'fresh'),
    ('poor', 'impoverished', 'wealthy', 'rich', 'affluent'),
    ('quiet', 'silent', 'noisy', 'loud', 'boisterous'),
    ('rich', 'wealthy', 'poor', 'destitute', 'needy'),
    ('scared', 'frightened', 'brave', 'bold', 'fearless'),
    ('smart', 'bright', 'dim', 'dull', 'unintelligent'),
    ('strange', 'odd', 'normal', 'ordinary', 'common'),
    ('strong', 'powerful', 'weak', 'feeble', 'fragile'),
    ('tall', 'lofty', 'short', 'stubby', 'small'),
    ('thin', 'slender', 'thick', 'chubby', 'bulky'),
    ('tired', 'weary', 'energetic', 'fresh', 'refreshed'),
    ('ugly', 'unsightly', 'beautiful', 'pretty', 'attractive'),
    ('beautiful', 'gorgeous', 'ugly', 'plain', 'hideous'),
    ('dark', 'gloomy', 'bright', 'light', 'sunny'),
    ('swift', 'fast', 'slow', 'leisurely', 'sluggish'),
    ('funny', 'humorous', 'serious', 'somber', 'dull'),
    ('content', 'satisfied', 'unhappy', 'dissatisfied', 'restless'),
    ('tough', 'hard', 'soft', 'tender', 'delicate'),
    ('aid', 'help', 'hinder', 'block', 'obstruct'),
    ('occupation', 'job', 'hobby', 'pastime', 'leisure'),
    ('chuckle', 'laugh', 'cry', 'weep', 'sob'),
    ('glance', 'look', 'stare', 'gaze', 'peer'),
    ('relocate', 'move', 'stay', 'remain', 'settle'),
    ('sprint', 'run', 'walk', 'crawl', 'stroll'),
    ('demonstrate', 'show', 'hide', 'conceal', 'mask'),
    ('tiny', 'small', 'large', 'huge', 'enormous'),
    ('cease', 'stop', 'start', 'begin', 'commence'),
    ('contemplate', 'think', 'ignore', 'forget', 'neglect'),
    ('attempt', 'try', 'abandon', 'quit', 'give up'),
    ('desire', 'want', 'dislike', 'hate', 'loathe'),
    ('labor', 'work', 'rest', 'idle', 'laze'),
    ('miserable', 'unhappy', 'joyful', 'content', 'pleased'),
    ('prompt', 'quick', 'slow', 'delayed', 'tardy'),
    ('rescue', 'save', 'abandon', 'endanger', 'jeopardize'),
    ('sorrow', 'grief', 'joy', 'happiness', 'delight'),
    ('tremendous', 'enormous', 'tiny', 'minuscule', 'small'),
    ('valuable', 'precious', 'worthless', 'cheap', 'useless'),
]

EN_ANTONYMS = [
    ('happy', 'sad', 'joyful', 'cheerful', 'glad'),
    ('big', 'small', 'large', 'huge', 'enormous'),
    ('fast', 'slow', 'quick', 'rapid', 'swift'),
    ('hot', 'cold', 'warm', 'boiling', 'scorching'),
    ('tall', 'short', 'high', 'lofty', 'elevated'),
    ('strong', 'weak', 'powerful', 'mighty', 'robust'),
    ('rich', 'poor', 'wealthy', 'affluent', 'prosperous'),
    ('young', 'old', 'youthful', 'fresh', 'new'),
    ('easy', 'hard', 'simple', 'effortless', 'straightforward'),
    ('day', 'night', 'morning', 'noon', 'dusk'),
    ('up', 'down', 'above', 'high', 'over'),
    ('begin', 'end', 'start', 'commence', 'initiate'),
    ('bright', 'dark', 'luminous', 'shiny', 'radiant'),
    ('clean', 'dirty', 'spotless', 'pure', 'hygienic'),
    ('deep', 'shallow', 'profound', 'vast', 'intense'),
    ('dry', 'wet', 'arid', 'parched', 'dehydrated'),
    ('early', 'late', 'prompt', 'timely', 'punctual'),
    ('empty', 'full', 'hollow', 'vacant', 'bare'),
    ('first', 'last', 'initial', 'primary', 'foremost'),
    ('give', 'take', 'donate', 'provide', 'offer'),
    ('good', 'bad', 'great', 'fine', 'excellent'),
    ('heavy', 'light', 'massive', 'weighty', 'ponderous'),
    ('inside', 'outside', 'within', 'interior', 'internal'),
    ('left', 'right', 'remaining', 'west', 'port'),
    ('loud', 'quiet', 'noisy', 'boisterous', 'thunderous'),
    ('love', 'hate', 'adore', 'cherish', 'treasure'),
    ('open', 'close', 'unlock', 'unseal', 'unfasten'),
    ('peace', 'war', 'harmony', 'tranquility', 'calm'),
    ('public', 'private', 'open', 'common', 'shared'),
    ('right', 'wrong', 'correct', 'proper', 'accurate'),
    ('safe', 'dangerous', 'secure', 'protected', 'shielded'),
    ('same', 'different', 'identical', 'equal', 'similar'),
    ('smooth', 'rough', 'even', 'silky', 'level'),
    ('start', 'finish', 'begin', 'commence', 'initiate'),
    ('success', 'failure', 'victory', 'triumph', 'achievement'),
    ('victory', 'defeat', 'win', 'triumph', 'success'),
    ('win', 'lose', 'triumph', 'prevail', 'succeed'),
    ('wide', 'narrow', 'broad', 'spacious', 'expansive'),
    ('true', 'false', 'correct', 'real', 'accurate'),
    ('ancient', 'modern', 'old', 'antique', 'archaic'),
]

EN_SPELLING = [
    ('accommodate', 'accomodate', 'acommodate', 'accomadate'),
    ('necessary', 'neccessary', 'necessery', 'neccesary'),
    ('definitely', 'definately', 'definitly', 'definately'),
    ('separate', 'seperate', 'seperete', 'separte'),
    ('receive', 'recieve', 'receeve', 'recive'),
    ('achieve', 'acheive', 'achive', 'acheive'),
    ('believe', 'beleive', 'belive', 'beleev'),
    ('colleague', 'colleague', 'colleague', 'colligue'),
    ('embarrass', 'embarass', 'embarras', 'embarase'),
    ('environment', 'enviroment', 'enviornment', 'envirnment'),
    ('government', 'goverment', 'governmint', 'govermant'),
    ('independent', 'independant', 'indepandent', 'indipendnt'),
    ('jewelry', 'jewlery', 'jewellery', 'jewlry'),
    ('knowledge', 'knowlege', 'knowladge', 'knolege'),
    ('license', 'licence', 'lisence', 'licanse'),
    ('maintenance', 'maintainance', 'maintenence', 'maintanence'),
    ('miscellaneous', 'miscellanous', 'miscelaneous', 'miscellanious'),
    ('noticeable', 'noticable', 'notiseable', 'noticeble'),
    ('occasionally', 'occassionally', 'ocasionally', 'occasionaly'),
    ('occurrence', 'occurence', 'ocurrence', 'occurrance'),
    ('parallel', 'paralel', 'parallell', 'parrallel'),
    ('possession', 'posession', 'possesssion', 'possesion'),
    ('privilege', 'priviledge', 'privilege', 'privelege'),
    ('questionnaire', 'questionaire', 'questionnare', 'questionnaire'),
    ('recommend', 'recomend', 'reccomend', 'recommendd'),
    ('rhythm', 'rythm', 'rhythym', 'rhythem'),
    ('restaurant', 'restaraunt', 'resturant', 'restarant'),
    ('schedule', 'schedual', 'scedule', 'shedule'),
    ('temperature', 'tempereture', 'temprature', 'tempature'),
    ('Wednesday', 'Wensday', 'Wednsday', 'Wenesday'),
    ('February', 'Febuary', 'Feburary', 'Febraury'),
]

EN_IDIOMS = [
    ('break the ice', 'to start a conversation', 'to destroy ice', 'to feel cold', 'to hurry'),
    ('hit the nail on the head', 'to be exactly right', 'to work with tools', 'to fail', 'to get angry'),
    ('once in a blue moon', 'very rarely', 'every day', 'once a year', 'at midnight'),
    ('piece of cake', 'something very easy', 'a dessert', 'a small problem', 'a big task'),
    ('under the weather', 'feeling ill', 'standing in rain', 'being outdoors', 'feeling happy'),
    ('bite the bullet', 'to face something difficult', 'to eat quickly', 'to get injured', 'to be brave always'),
    ('let the cat out of the bag', 'to reveal a secret', 'to free a pet', 'to be careless', 'to shop'),
    ('the ball is in your court', 'it is your turn to act', 'you lost the game', 'the game is over', 'you are winning'),
    ('burn the midnight oil', 'to work late at night', 'to set a fire', 'to waste oil', 'to cook dinner'),
    ('cost an arm and a leg', 'to be very expensive', 'to be cheap', 'to be painful', 'to be priceless'),
    ('spill the beans', 'to reveal a secret', 'to drop food', 'to cook beans', 'to be clumsy'),
    ('when pigs fly', 'something that will never happen', 'a rare event', 'an everyday event', 'a weather event'),
    ('a blessing in disguise', 'a good thing that seemed bad', 'a hidden curse', 'a disguise', 'a surprise'),
    ('add fuel to the fire', 'to make a situation worse', 'to start a fire', 'to cook', 'to calm down'),
    ('back to the drawing board', 'to start over', 'to draw pictures', 'to go to class', 'to give up'),
    ('beat around the bush', 'to avoid the main point', 'to search in bushes', 'to move fast', 'to be direct'),
    ('best of both worlds', 'an ideal situation', 'a difficult choice', 'a compromise', 'an impossible task'),
    ('by the skin of your teeth', 'to barely succeed', 'to fail completely', 'to succeed easily', 'to hurt yourself'),
    ('call it a day', 'to stop working for the day', 'to celebrate', 'to start work', 'to sleep'),
    ('caught red-handed', 'to be caught in the act', 'to have red hands', 'to be guilty always', 'to be in danger'),
    ('cross that bridge when you come to it', 'to deal with a problem later', 'to cross a river', 'to plan ahead', 'to avoid problems'),
    ('cut corners', 'to do something poorly to save time', 'to build a shape', 'to be precise', 'to work slowly'),
    ('devils advocate', 'to argue the opposite side', 'a lawyer', 'a demon', 'a critic'),
    ('feel under the weather', 'to feel unwell', 'to be happy', 'to be outside', 'to be energetic'),
    ('get your act together', 'to organize yourself', 'to perform a play', 'to act', 'to dance'),
    ('give the benefit of the doubt', 'to trust someone', 'to doubt someone', 'to punish someone', 'to ignore someone'),
    ('go the extra mile', 'to make extra effort', 'to walk far', 'to drive', 'to give up'),
    ('in hot water', 'to be in trouble', 'to be warm', 'to bathe', 'to be relaxed'),
    ('jump on the bandwagon', 'to follow a trend', 'to ride a bus', 'to play music', 'to avoid trends'),
    ('keep your chin up', 'to stay optimistic', 'to look up', 'to be sad', 'to be proud'),
    ('kill two birds with one stone', 'to solve two problems at once', 'to hunt', 'to be cruel', 'to waste time'),
    ('let bygones be bygones', 'to forget past quarrels', 'to remember the past', 'to get angry', 'to move house'),
    ('make a long story short', 'to summarize briefly', 'to tell a long story', 'to write a book', 'to delay'),
    ('miss the boat', 'to miss an opportunity', 'to miss a flight', 'to lose a ship', 'to arrive late'),
    ('on the fence', 'to be undecided', 'to sit high', 'to be decided', 'to be outside'),
]

EN_GRAMMAR = [
    Q('She ___ to school every day.', 'goes', 'go', 'going', 'gone'),
    Q('They ___ playing football now.', 'are', 'is', 'am', 'be'),
    Q('I have ___ my homework.', 'done', 'did', 'do', 'does'),
    Q('He ___ a doctor.', 'is', 'are', 'am', 'be'),
    Q('We ___ to the park yesterday.', 'went', 'go', 'gone', 'going'),
    Q('She can ___ English fluently.', 'speak', 'speaks', 'speaking', 'spoken'),
    Q('This is the book ___ I bought.', 'that', 'who', 'whom', 'whose'),
    Q('There ___ many students in the class.', 'are', 'is', 'am', 'be'),
    Q('My brother is ___ than me.', 'taller', 'tallest', 'tall', 'more tall'),
    Q('She is the ___ girl in the class.', 'smartest', 'smarter', 'smart', 'more smart'),
    Q('I ___ never been to London.', 'have', 'has', 'had', 'having'),
    Q('They ___ watching TV last night.', 'were', 'was', 'are', 'is'),
    Q('Please ___ me your pen.', 'give', 'gives', 'giving', 'given'),
    Q('He has lived here ___ 2010.', 'since', 'for', 'from', 'at'),
    Q('We have known each other ___ five years.', 'for', 'since', 'from', 'during'),
    Q('The train ___ already left.', 'has', 'have', 'had been', 'is'),
    Q('I am looking forward to ___ you.', 'meeting', 'meet', 'met', 'meets'),
    Q('She asked me ___ I was tired.', 'whether', 'that', 'which', 'what'),
    Q('Neither of the answers ___ correct.', 'is', 'are', 'were', 'be'),
    Q('Each of the students ___ given a book.', 'was', 'were', 'are', 'be'),
    Q('If it rains, we ___ at home.', 'will stay', 'stay', 'stayed', 'staying'),
    Q('He ___ his homework before dinner.', 'finished', 'finish', 'finishes', 'finishing'),
    Q('The children ___ playing in the garden.', 'are', 'is', 'am', 'be'),
    Q('I would like ___ a cup of tea.', 'to have', 'have', 'having', 'had'),
    Q('She sings ___ than her sister.', 'better', 'best', 'good', 'well'),
]

EN_SPELL_QS = [Q('Which of the following is spelled correctly?', c, *w) for c, *w in EN_SPELLING]

EN_SYN_QS = [
    Q('Which word is a synonym of "{}"?'.format(w), s, *wlist)
    for w, s, *wlist in EN_SYNONYMS
]

EN_ANT_QS = [
    Q('Which word is an antonym of "{}"?'.format(w), a, *wlist)
    for w, a, *wlist in EN_ANTONYMS
]

EN_IDIOM_QS = [
    Q('What is the meaning of the idiom "{}"?'.format(idiom), meaning, *wlist)
    for idiom, meaning, *wlist in EN_IDIOMS
]


def build_english(rng):
    return EN_SYN_QS + EN_ANT_QS + EN_SPELL_QS + EN_IDIOM_QS + list(EN_GRAMMAR)


# =====================================================================
# Current Affairs
# =====================================================================

CA_CURATED = [
    Q('The United Nations was founded in which year?', '1945', '1948', '1950', '1939'),
    Q('Which organisation gives the Nobel Peace Prize?', 'Norwegian Nobel Committee', 'United Nations', 'European Union', 'World Bank'),
    Q('The World Health Organization is an agency of which body?', 'United Nations', 'European Union', 'World Bank', 'NATO'),
    Q('Which country hosted the 2020 Summer Olympics (held in 2021)?', 'Japan', 'China', 'Brazil', 'United Kingdom'),
    Q('The IMF is headquartered in which city?', 'Washington D.C.', 'New York', 'Geneva', 'London'),
    Q('Which is the largest economy in the world by nominal GDP?', 'United States', 'China', 'Germany', 'Japan'),
    Q('The G20 includes how many member countries?', '20', '19', '21', '25'),
    Q('Which country is the headquarters of NATO?', 'Belgium', 'France', 'United States', 'Germany'),
    Q('The Kyoto Protocol is related to what?', 'Climate change', 'Nuclear weapons', 'Trade', 'Space'),
    Q('The Paris Agreement deals with which issue?', 'Climate change', 'Trade barriers', 'Cybersecurity', 'Migration'),
    Q('Which is the highest civilian award in the United States?', 'Presidential Medal of Freedom', 'Nobel Prize', 'Pulitzer Prize', 'Oscar'),
    Q('Which country launched the first artificial satellite, Sputnik?', 'Soviet Union', 'United States', 'China', 'Germany'),
    Q('Who is the head of the World Bank as of recent years?', 'Ajay Banga', 'Christine Lagarde', 'Jim Kim', 'Kristalina Georgieva'),
    Q('The headquarters of the European Union is in which city?', 'Brussels', 'Paris', 'Geneva', 'Strasbourg'),
    Q('Which country is the largest producer of tea?', 'China', 'India', 'Kenya', 'Sri Lanka'),
    Q('Which is the largest technology company by revenue?', 'Apple', 'Microsoft', 'Amazon', 'Alphabet'),
    Q('Which social media company changed its name to Meta?', 'Facebook', 'Twitter', 'Instagram', 'Snapchat'),
    Q('The International Space Station is a project of how many space agencies?', 'Five', 'Two', 'Ten', 'Three'),
    Q('Which space agency launched the Artemis program?', 'NASA', 'ESA', 'ISRO', 'Roscosmos'),
    Q('The James Webb Space Telescope was launched by which agency?', 'NASA', 'ESA', 'JAXA', 'CNSA'),
    Q('Which country has the largest armed forces?', 'China', 'United States', 'India', 'Russia'),
    Q('The Commonwealth of Nations has its headquarters in which city?', 'London', 'New York', 'Geneva', 'Ottawa'),
    Q('Which country won the most medals in the 2020 Olympics?', 'United States', 'China', 'Japan', 'Russia'),
    Q('The FIFA World Cup is held every how many years?', '4', '2', '3', '5'),
    Q('Which country hosted the 2014 FIFA World Cup?', 'Brazil', 'Russia', 'Germany', 'South Africa'),
    Q('The Nobel Prize is awarded in how many categories?', '6', '5', '7', '4'),
    Q('Who founded the World Wide Web Foundation?', 'Tim Berners-Lee', 'Bill Gates', 'Mark Zuckerberg', 'Steve Jobs'),
    Q('Which country is the largest exporter of oil?', 'United States', 'Saudi Arabia', 'Russia', 'Canada'),
    Q('The European Union currency is the?', 'Euro', 'Pound', 'Franc', 'Krone'),
    Q('Which country is not a member of the European Union?', 'Norway', 'France', 'Germany', 'Italy'),
    Q('The United Nations Security Council has how many permanent members?', '5', '6', '10', '15'),
    Q('Which country is the largest producer of cotton?', 'India', 'China', 'United States', 'Brazil'),
    Q('The Oscars are awards for which industry?', 'Film', 'Music', 'Literature', 'Sport'),
    Q('Which festival was declared a UN holiday in 2024?', 'Lunar New Year', 'Diwali', 'Thanksgiving', 'Oktoberfest'),
    Q('The worlds largest cryptocurrency by market cap is?', 'Bitcoin', 'Ethereum', 'Tether', 'Ripple'),
    Q('Which country banned ChatGPT in 2024 before lifting it?', 'Italy', 'France', 'Germany', 'Spain'),
    Q('The Indian Space Research Organisation launched which Moon mission in 2023?', 'Chandrayaan-3', 'Mangalyaan', 'Gaganyaan', 'Aditya'),
    Q('Which country landed a rover on the Moon in 2023?', 'India', 'China', 'United States', 'Russia'),
    Q('The world population surpassed which milestone in 2022?', '8 billion', '7 billion', '9 billion', '10 billion'),
    Q('Which is the most visited city in the world?', 'Bangkok', 'Paris', 'London', 'Dubai'),
    Q('The Great Barrier Reef is a UNESCO World Heritage Site in which country?', 'Australia', 'Mexico', 'Belize', 'Maldives'),
    Q('Which country won the Cricket World Cup in 2023?', 'Australia', 'India', 'England', 'New Zealand'),
    Q('The worlds largest e-commerce company is?', 'Amazon', 'Alibaba', 'Walmart', 'eBay'),
    Q('Which country is the largest producer of solar energy?', 'China', 'Germany', 'United States', 'India'),
    Q('The COP28 climate summit was held in which country?', 'United Arab Emirates', 'Egypt', 'Scotland', 'Poland'),
    Q('Which country launched the worlds first 6G test?', 'China', 'United States', 'South Korea', 'Finland'),
    Q('The Nobel Prize in Literature is awarded by which country institution?', 'Sweden', 'Norway', 'Denmark', 'Finland'),
    Q('The world economic forum annual meeting is held in which town?', 'Davos', 'Geneva', 'Zurich', 'Basel'),
    Q('Which is the largest airline alliance in the world?', 'Star Alliance', 'SkyTeam', 'Oneworld', 'Ufly Alliance'),
    Q('The Red Cross was founded by whom?', 'Henry Dunant', 'Florence Nightingale', 'Mahatma Gandhi', 'Albert Schweitzer'),
    Q('Which country has the highest life expectancy?', 'Japan', 'Switzerland', 'Australia', 'Canada'),
    Q('The worlds largest desert is?', 'Antarctic Desert', 'Sahara', 'Arabian', 'Gobi'),
    Q('Which country is the largest producer of bananas?', 'India', 'Ecuador', 'China', 'Brazil'),
    Q('The International Criminal Court is in which city?', 'The Hague', 'Geneva', 'New York', 'Vienna'),
    Q('Which company produces the iPhone?', 'Apple', 'Samsung', 'Google', 'Sony'),
    Q('The worlds fastest supercomputer in recent TOP500 lists is?', 'Frontier', 'Summit', 'Fugaku', 'Titan'),
    Q('Which country was the first to recognise same-sex marriage?', 'Netherlands', 'United States', 'Canada', 'South Africa'),
    Q('The metro system in which city is the largest in the world?', 'Shanghai', 'Tokyo', 'London', 'Moscow'),
    Q('Which country celebrates its independence on July 4?', 'United States', 'France', 'India', 'Mexico'),
    Q('The worlds largest exporter of services is?', 'United States', 'China', 'Germany', 'United Kingdom'),
    Q('Which is the most popular social media platform by active users?', 'Facebook', 'Instagram', 'TikTok', 'X'),
    Q('The Universal Postal Union is headquartered in?', 'Bern', 'Paris', 'London', 'Geneva'),
    Q('Which country is home to the Taj Mahal?', 'India', 'Pakistan', 'Bangladesh', 'Nepal'),
    Q('The worlds largest producer of milk is?', 'India', 'United States', 'China', 'Brazil'),
    Q('Which country hosted COP27 in 2022?', 'Egypt', 'UAE', 'Scotland', 'Germany'),
    Q('The Internet is estimated to be used by what fraction of the world population?', 'About two-thirds', 'About half', 'About one-third', 'Almost all'),
    Q('Which country has the highest number of internet users?', 'China', 'India', 'United States', 'Indonesia'),
    Q('The world chess champion who retained the title in 2024 is?', 'Gukesh Dommaraju', 'Magnus Carlsen', 'Ian Nepomniachtchi', 'Ding Liren'),
    Q('The Olympics symbol has how many rings?', '5', '4', '6', '3'),
    Q('Which country invented the QR code?', 'Japan', 'China', 'South Korea', 'United States'),
    Q('The worlds largest free-trade area, the African Continental Free Trade Area, covers how many countries?', '54', '44', '35', '20'),
]


def build_current_affairs(rng):
    return list(CA_CURATED)


# =====================================================================
# Sports
# =====================================================================

SPORTS_CURATED = [
    Q('How many players are on a football (soccer) team on the field?', '11', '10', '12', '9'),
    Q('How many players are on a basketball team on the court?', '5', '6', '4', '7'),
    Q('How many innings are there in a standard baseball game?', '9', '7', '6', '10'),
    Q('Which country won the 2018 FIFA World Cup?', 'France', 'Germany', 'Brazil', 'Croatia'),
    Q('Which country won the 2022 FIFA World Cup?', 'Argentina', 'France', 'Brazil', 'Morocco'),
    Q('Who is known as the GOAT in basketball with 6 NBA titles?', 'Michael Jordan', 'LeBron James', 'Kobe Bryant', 'Magic Johnson'),
    Q('The Olympics are held every how many years?', '4', '2', '3', '5'),
    Q('The modern Olympics began in which year?', '1896', '1900', '1904', '1888'),
    Q('Which city hosted the 2016 Summer Olympics?', 'Rio de Janeiro', 'London', 'Tokyo', 'Beijing'),
    Q('Which country invented cricket?', 'England', 'Australia', 'India', 'South Africa'),
    Q('The Ashes series is contested between which two countries?', 'England and Australia', 'India and Pakistan', 'Australia and India', 'England and South Africa'),
    Q('How many runs are scored on a six in cricket?', '6', '4', '5', '3'),
    Q('How many balls are in an over in cricket?', '6', '4', '5', '8'),
    Q('Which country won the 2011 Cricket World Cup?', 'India', 'Sri Lanka', 'Australia', 'Pakistan'),
    Q('Which country won the 2019 Cricket World Cup?', 'England', 'New Zealand', 'Australia', 'India'),
    Q('The Wimbledon Championship is associated with which sport?', 'Tennis', 'Golf', 'Cricket', 'Football'),
    Q('How many Grand Slam tournaments are there in tennis each year?', '4', '3', '5', '2'),
    Q('Who has won the most Grand Slam men singles titles?', 'Novak Djokovic', 'Roger Federer', 'Rafael Nadal', 'Pete Sampras'),
    Q('The Tour de France is a race in which sport?', 'Cycling', 'Running', 'Swimming', 'Motorsport'),
    Q('Which country hosts the Tour de France?', 'France', 'Italy', 'Spain', 'Belgium'),
    Q('Formula 1 has how many teams typically on the grid?', '10', '8', '12', '14'),
    Q('Who is a legendary Formula 1 driver with 7 world titles?', 'Michael Schumacher', 'Lewis Hamilton', 'Ayrton Senna', 'Sebastian Vettel'),
    Q('The Super Bowl is the championship of which sport?', 'American Football', 'Basketball', 'Baseball', 'Soccer'),
    Q('Which sport uses a shuttlecock?', 'Badminton', 'Tennis', 'Squash', 'Table tennis'),
    Q('How many points is a touchdown in American football?', '6', '3', '7', '5'),
    Q('Which country dominates the sport of sumo wrestling?', 'Japan', 'China', 'Mongolia', 'Korea'),
    Q('The Stanley Cup is awarded in which sport?', 'Ice hockey', 'Basketball', 'Baseball', 'Cricket'),
    Q('Which is the most-watched sport in the world?', 'Football (soccer)', 'Cricket', 'Basketball', 'Tennis'),
    Q('Usain Bolt is a world record holder in which sport?', 'Sprint running', 'Swimming', 'Cycling', 'Long jump'),
    Q('What is Usain Bolts world record for the 100m?', '9.58 seconds', '9.63 seconds', '9.72 seconds', '9.85 seconds'),
    Q('How long is a marathon?', '42.195 km', '40 km', '26.2 miles only', '45 km'),
    Q('Which country invented basketball?', 'United States', 'Canada', 'England', 'Spain'),
    Q('Who invented basketball?', 'James Naismith', 'Michael Jordan', 'William Morgan', 'Luther Gulick'),
    Q('Volleyball was invented in which country?', 'United States', 'Japan', 'Brazil', 'Italy'),
    Q('How many players are on a volleyball team on the court?', '6', '5', '7', '4'),
    Q('The Ryder Cup is a competition in which sport?', 'Golf', 'Tennis', 'Cricket', 'Sailing'),
    Q('Which country has won the most FIFA World Cup titles?', 'Brazil', 'Germany', 'Italy', 'Argentina'),
    Q('How many FIFA World Cup titles has Brazil won?', '5', '4', '6', '3'),
    Q('Which athlete is known as the fastest man alive?', 'Usain Bolt', 'Carl Lewis', 'Tyson Gay', 'Justin Gatlin'),
    Q('The Olympic motto is what?', 'Faster, Higher, Stronger', 'Higher, Better, Faster', 'Stronger, Faster, Higher', 'Fast, Far, Brave'),
    Q('Which sport is played at Augusta National?', 'Golf', 'Tennis', 'Polo', 'Cricket'),
    Q('The Super Bowl trophy is named after whom?', 'Vince Lombardi', 'Tom Brady', 'Pete Rozelle', 'Walter Payton'),
    Q('Which country won the Rugby World Cup 2019?', 'South Africa', 'England', 'New Zealand', 'Wales'),
    Q('How many minutes is a standard football match?', '90', '80', '100', '120'),
    Q('How many minutes is an NBA basketball quarter?', '12', '10', '15', '8'),
    Q('Which swimmer holds the most Olympic gold medals?', 'Michael Phelps', 'Mark Spitz', 'Ian Thorpe', 'Katie Ledecky'),
    Q('How many Olympic gold medals has Michael Phelps won?', '23', '18', '20', '25'),
    Q('The Boston Marathon is held in which country?', 'United States', 'England', 'Canada', 'Australia'),
    Q('Which country dominates the sport of table tennis at the Olympics?', 'China', 'Japan', 'South Korea', 'Germany'),
    Q('The World Series is the championship of which sport?', 'Baseball', 'Basketball', 'Soccer', 'Hockey'),
    Q('How many bases are there in baseball?', '4', '3', '5', '2'),
    Q('Which country won the 2023 FIFA Womens World Cup?', 'Spain', 'England', 'United States', 'Sweden'),
    Q('The Triple Crown in horse racing involves how many races?', '3', '2', '4', '5'),
    Q('Which boxer was known as The Greatest?', 'Muhammad Ali', 'Mike Tyson', 'Joe Frazier', 'Sugar Ray Leonard'),
    Q('The NFL season champion is decided at which event?', 'Super Bowl', 'World Series', 'Stanley Cup', 'NBA Finals'),
    Q('Which country hosted the 2022 Winter Olympics?', 'China', 'Japan', 'South Korea', 'Russia'),
    Q('The Olympic flame is lit in which city?', 'Olympia, Greece', 'Athens', 'Rome', 'Lausanne'),
    Q('Which country invented table tennis?', 'England', 'China', 'Japan', 'United States'),
    Q('The Davis Cup is the international championship of which sport?', 'Tennis', 'Cricket', 'Golf', 'Badminton'),
    Q('Which country has won the most Olympic gold medals overall?', 'United States', 'China', 'Soviet Union', 'Germany'),
    Q('How many players are on a field hockey team?', '11', '10', '9', '8'),
    Q('The Ballon dOr is awarded in which sport?', 'Football', 'Basketball', 'Tennis', 'Cricket'),
    Q('Who won the most Ballon dOr awards?', 'Lionel Messi', 'Cristiano Ronaldo', 'Michel Platini', 'Johan Cruyff'),
    Q('The kookaburra and duke are brands of balls used in which sport?', 'Cricket', 'Tennis', 'Golf', 'Basketball'),
    Q('Which sport is known as the beautiful game?', 'Football', 'Cricket', 'Tennis', 'Rugby'),
]


def build_sports(rng):
    return list(SPORTS_CURATED)


# =====================================================================
# Movies & TV
# =====================================================================

MOVIES_CURATED = [
    Q('Which film won the Best Picture Oscar in 2020?', 'Parasite', '1917', 'Joker', 'Once Upon a Time in Hollywood'),
    Q('Who directed the movie Titanic?', 'James Cameron', 'Steven Spielberg', 'Christopher Nolan', 'Ridley Scott'),
    Q('Who played Jack in the movie Titanic?', 'Leonardo DiCaprio', 'Brad Pitt', 'Tom Cruise', 'Johnny Depp'),
    Q('Which actor plays Iron Man in the MCU?', 'Robert Downey Jr.', 'Chris Evans', 'Chris Hemsworth', 'Mark Ruffalo'),
    Q('Which film is the highest-grossing of all time?', 'Avatar', 'Avengers: Endgame', 'Titanic', 'Star Wars'),
    Q('Who directed Inception?', 'Christopher Nolan', 'Steven Spielberg', 'Quentin Tarantino', 'James Cameron'),
    Q('Which franchise features a character named Darth Vader?', 'Star Wars', 'Star Trek', 'Harry Potter', 'The Matrix'),
    Q('Who directed the trilogy The Lord of the Rings?', 'Peter Jackson', 'James Cameron', 'George Lucas', 'Ridley Scott'),
    Q('Which studio produced The Godfather?', 'Paramount Pictures', 'Universal', 'Warner Bros', 'Disney'),
    Q('Which animated film features a character named Woody?', 'Toy Story', 'Finding Nemo', 'Shrek', 'Monsters Inc'),
    Q('Who voiced the Genie in the 1992 Aladdin?', 'Robin Williams', 'Will Smith', 'Eddie Murphy', 'Dan Castellaneta'),
    Q('Which film series features a wizard named Harry Potter?', 'Harry Potter', 'Percy Jackson', 'Narnia', 'Lord of the Rings'),
    Q('Which movie features the quote "I am your father"?', 'Star Wars: The Empire Strikes Back', 'The Matrix', 'Back to the Future', 'Terminator'),
    Q('Who directed the movie Pulp Fiction?', 'Quentin Tarantino', 'Martin Scorsese', 'Coen Brothers', 'David Fincher'),
    Q('Which actor played the Joker in The Dark Knight?', 'Heath Ledger', 'Jared Leto', 'Jack Nicholson', 'Joaquin Phoenix'),
    Q('Which movie franchise features a character named Forrest Gump?', 'Forrest Gump', 'Saving Private Ryan', 'Cast Away', 'Big'),
    Q('Who played Forrest Gump?', 'Tom Hanks', 'Robin Williams', 'Kevin Costner', 'Harrison Ford'),
    Q('Which TV series features the characters Walter White and Jesse Pinkman?', 'Breaking Bad', 'The Wire', 'Ozark', 'Narcos'),
    Q('Which TV series is set in the fictional Westeros?', 'Game of Thrones', 'The Witcher', 'Vikings', 'Lord of the Rings'),
    Q('Which sitcom features the character Chandler Bing?', 'Friends', 'Seinfeld', 'How I Met Your Mother', 'The Big Bang Theory'),
    Q('Which TV series features a scientist named Sheldon Cooper?', 'The Big Bang Theory', 'Friends', 'Seinfeld', 'Frasier'),
    Q('Which movie features the character Jack Sparrow?', 'Pirates of the Caribbean', 'National Treasure', 'The Mummy', 'Moulin Rouge'),
    Q('Who plays Jack Sparrow?', 'Johnny Depp', 'Orlando Bloom', 'Keira Knightley', 'Russell Crowe'),
    Q('Which film won the first ever Best Picture Oscar?', 'Wings', 'Sunrise', 'The Jazz Singer', 'The Crowd'),
    Q('Which director is known for the movie Jaws?', 'Steven Spielberg', 'George Lucas', 'Francis Ford Coppola', 'Alfred Hitchcock'),
    Q('Who directed the movie Psycho?', 'Alfred Hitchcock', 'Steven Spielberg', 'Martin Scorsese', 'Roman Polanski'),
    Q('Which film series follows a character named Neo?', 'The Matrix', 'Inception', 'Tron', 'Blade Runner'),
    Q('Which actor plays Neo in The Matrix?', 'Keanu Reeves', 'Tom Cruise', 'Matt Damon', 'Will Smith'),
    Q('Which movie features the quote "To infinity and beyond"?', 'Toy Story', 'Up', 'WALL-E', 'Cars'),
    Q('Which studio produced Toy Story?', 'Pixar', 'DreamWorks', 'Blue Sky', 'Disney'),
    Q('Which TV series features the character Eleven?', 'Stranger Things', 'Dark', 'The OA', 'Twin Peaks'),
    Q('Which movie features a character named Marty McFly?', 'Back to the Future', 'E.T.', 'Ghostbusters', 'Gremlins'),
    Q('Which animated series features a character named Homer Simpson?', 'The Simpsons', 'Family Guy', 'South Park', 'Futurama'),
    Q('Which movie is about a shark attack at a beach town?', 'Jaws', 'Deep Blue Sea', 'Sharknado', 'The Shallows'),
    Q('Which film features the character James Bond?', 'Casino Royale', 'The Bourne Identity', 'Mission: Impossible', 'Jack Ryan'),
    Q('Which actor was the first James Bond on film?', 'Sean Connery', 'Roger Moore', 'Pierce Brosnan', 'Daniel Craig'),
    Q('Which movie features a car named Herbie?', 'The Love Bug', 'Cars', 'Fast and Furious', 'Smokey and the Bandit'),
    Q('Which TV series is a medieval fantasy featuring dragons?', 'Game of Thrones', 'Vikings', 'The Witcher', 'Merlin'),
    Q('Which film is based on the board game about a ship?', 'Battleship', 'Clue', 'Monopoly', 'Jumanji'),
    Q('Which movie stars Keanu Reeves as John Wick?', 'John Wick', 'The Matrix', 'Speed', 'Point Break'),
    Q('Which animated film features a character named Simba?', 'The Lion King', 'Tarzan', 'Aladdin', 'Hercules'),
    Q('Which Disney movie features a character named Ariel?', 'The Little Mermaid', 'Frozen', 'Moana', 'Tangled'),
    Q('Which movie features the quote "Houston, we have a problem"?', 'Apollo 13', 'Gravity', 'The Martian', 'Interstellar'),
    Q('Which film won the Best Picture Oscar in 2019?', 'Green Book', 'Roma', 'Black Panther', 'A Star Is Born'),
    Q('Which director directed the movie 1917?', 'Sam Mendes', 'Christopher Nolan', 'Steven Spielberg', 'Peter Jackson'),
    Q('Which TV series features the character Rick Grimes?', 'The Walking Dead', 'Supernatural', 'Fear the Walking Dead', 'Stranger Things'),
    Q('Which film series features a character named Rocky Balboa?', 'Rocky', 'Rambo', 'Creed', 'First Blood'),
    Q('Who played Rocky Balboa?', 'Sylvester Stallone', 'Arnold Schwarzenegger', 'Bruce Willis', 'Jean-Claude Van Damme'),
    Q('Which movie features a character named Hermione Granger?', 'Harry Potter', 'The Hunger Games', 'Twilight', 'Percy Jackson'),
    Q('Which film features the character Ethan Hunt?', 'Mission: Impossible', 'The Bourne Identity', 'Jack Reacher', 'Die Hard'),
    Q('Which animated movie features a character named Shrek?', 'Shrek', 'Madagascar', 'Kung Fu Panda', 'Ice Age'),
    Q('Which film is famous for the line "May the force be with you"?', 'Star Wars', 'Star Trek', 'Guardians of the Galaxy', 'The Matrix'),
    Q('Which director directed the movie E.T.?', 'Steven Spielberg', 'George Lucas', 'James Cameron', 'Ridley Scott'),
    Q('Which TV series features the character Tony Stark?', 'Iron Man (MCU)', 'Arrow', 'The Flash', 'Agents of SHIELD'),
    Q('Which film features the quote "I feel the need, the need for speed"?', 'Top Gun', 'Days of Thunder', 'Gone in 60 Seconds', 'Fast and Furious'),
]


def build_movies(rng):
    return list(MOVIES_CURATED)


# =====================================================================
# Music
# =====================================================================

MUSIC_CURATED = [
    Q('How many notes are in a standard musical scale?', '7', '5', '8', '6'),
    Q('How many strings does a standard violin have?', '4', '6', '5', '3'),
    Q('How many strings does a standard cello have?', '4', '5', '6', '3'),
    Q('Which instrument has 88 keys?', 'Piano', 'Organ', 'Accordion', 'Harpsichord'),
    Q('Which composer wrote the Fifth Symphony?', 'Ludwig van Beethoven', 'Mozart', 'Bach', 'Chopin'),
    Q('Who is known as the King of Pop?', 'Michael Jackson', 'Elvis Presley', 'Prince', 'Freddie Mercury'),
    Q('Who is known as the Queen of Pop?', 'Madonna', 'Lady Gaga', 'Beyonce', 'Britney Spears'),
    Q('Which band performed the song "Bohemian Rhapsody"?', 'Queen', 'The Beatles', 'Pink Floyd', 'Led Zeppelin'),
    Q('Which band released the album "Abbey Road"?', 'The Beatles', 'The Rolling Stones', 'Pink Floyd', 'Queen'),
    Q('Which artist released the album "Thriller"?', 'Michael Jackson', 'Prince', 'Madonna', 'Whitney Houston'),
    Q('What is the highest female voice type?', 'Soprano', 'Alto', 'Mezzo-soprano', 'Tenor'),
    Q('What is the highest male voice type?', 'Tenor', 'Baritone', 'Bass', 'Countertenor'),
    Q('Which musical note lasts the longest?', 'Whole note', 'Half note', 'Quarter note', 'Eighth note'),
    Q('How many beats are in a 4/4 time signature?', '4', '3', '2', '6'),
    Q('Which genre of music originated in New Orleans?', 'Jazz', 'Rock', 'Country', 'Blues'),
    Q('Which instrument is central to flamenco music?', 'Guitar', 'Piano', 'Violin', 'Drums'),
    Q('Who composed the Four Seasons?', 'Antonio Vivaldi', 'Bach', 'Beethoven', 'Handel'),
    Q('Which composer was deaf in his later life?', 'Beethoven', 'Mozart', 'Bach', 'Schubert'),
    Q('Who wrote the opera "The Magic Flute"?', 'Mozart', 'Beethoven', 'Wagner', 'Verdi'),
    Q('Which artist is known for the song "Like a Rolling Stone"?', 'Bob Dylan', 'Bruce Springsteen', 'John Lennon', 'Neil Young'),
    Q('Which band is known for the album "Dark Side of the Moon"?', 'Pink Floyd', 'Led Zeppelin', 'Queen', 'The Who'),
    Q('Which singer performed "I Will Always Love You"?', 'Whitney Houston', 'Mariah Carey', 'Celine Dion', 'Adele'),
    Q('Which instrument has a mouthpiece and keys, used in jazz?', 'Saxophone', 'Trombone', 'Trumpet', 'Clarinet'),
    Q('Which music genre features heavy use of electric guitars and drums?', 'Rock', 'Jazz', 'Classical', 'Folk'),
    Q('Who is known as the King of Rock and Roll?', 'Elvis Presley', 'Chuck Berry', 'Little Richard', 'Buddy Holly'),
    Q('Which festival is the largest music festival in the US?', 'Coachella', 'Woodstock', 'Lollapalooza', 'SXSW'),
    Q('How many strings does a ukulele have?', '4', '6', '5', '3'),
    Q('Which string instrument is played with a bow?', 'Violin', 'Guitar', 'Harp', 'Mandolin'),
    Q('Which instrument is a member of the brass family?', 'Trumpet', 'Saxophone', 'Flute', 'Clarinet'),
    Q('Who composed the Moonlight Sonata?', 'Beethoven', 'Mozart', 'Chopin', 'Liszt'),
    Q('Which singer is known as the Boss?', 'Bruce Springsteen', 'Bon Jovi', 'Tom Petty', 'Bob Seger'),
    Q('Which band released the album "Nevermind"?', 'Nirvana', 'Pearl Jam', 'Soundgarden', 'Metallica'),
    Q('Which rapper is known for the album "The Marshall Mathers LP"?', 'Eminem', 'Jay-Z', 'Kendrick Lamar', 'Snoop Dogg'),
    Q('Which music streaming platform was founded in Sweden?', 'Spotify', 'Apple Music', 'Tidal', 'SoundCloud'),
    Q('What does the musical term "forte" mean?', 'Loud', 'Soft', 'Fast', 'Slow'),
    Q('What does the musical term "piano" mean in Italian?', 'Soft', 'Loud', 'Instrument', 'Slow'),
    Q('Which composer wrote "Clair de Lune"?', 'Claude Debussy', 'Chopin', 'Ravel', 'Satie'),
    Q('Which instrument is the largest in the string family?', 'Double bass', 'Cello', 'Viola', 'Violin'),
    Q('Who wrote the song "Yesterday" for The Beatles?', 'Paul McCartney', 'John Lennon', 'George Harrison', 'Ringo Starr'),
    Q('Which singer performed "Rolling in the Deep"?', 'Adele', 'Beyonce', 'Katy Perry', 'Rihanna'),
    Q('Which genre features the sitar prominently?', 'Indian classical music', 'Jazz', 'Country', 'Reggae'),
    Q('Which artist is known for the album "Purple Rain"?', 'Prince', 'Michael Jackson', 'Stevie Wonder', 'David Bowie'),
    Q('Which band featured the singer Freddie Mercury?', 'Queen', 'The Beatles', 'Led Zeppelin', 'The Rolling Stones'),
    Q('What is the interval between two adjacent keys on a piano called?', 'Semitone', 'Whole tone', 'Octave', 'Chord'),
    Q('How many semitones are in an octave?', '12', '8', '7', '10'),
    Q('Which instrument is used to keep rhythm in a band?', 'Drums', 'Piano', 'Saxophone', 'Flute'),
    Q('Which music genre originated in Jamaica?', 'Reggae', 'Salsa', 'Flamenco', 'Rumba'),
    Q('Who is known as the Duke of Jazz?', 'Duke Ellington', 'Louis Armstrong', 'Miles Davis', 'Count Basie'),
    Q('Which musician was known as Satchmo?', 'Louis Armstrong', 'Duke Ellington', 'Miles Davis', 'Charlie Parker'),
    Q('Which singer performed the song "My Heart Will Go On"?', 'Celine Dion', 'Whitney Houston', 'Mariah Carey', 'Adele'),
]


def build_music(rng):
    return list(MUSIC_CURATED)


# =====================================================================
# Business & Economics
# =====================================================================

BUSINESS_CURATED = [
    Q('What does GDP stand for?', 'Gross Domestic Product', 'Gross Domestic Profit', 'General Domestic Product', 'Gross Development Product'),
    Q('What is inflation?', 'A general rise in prices', 'A fall in prices', 'A rise in wages', 'A fall in GDP'),
    Q('What is a monopoly?', 'A market with a single seller', 'A market with many sellers', 'A type of tax', 'A business strategy'),
    Q('Which is the largest stock exchange by market cap?', 'New York Stock Exchange', 'NASDAQ', 'London Stock Exchange', 'Tokyo Stock Exchange'),
    Q('What is a dividend?', 'A share of profits paid to shareholders', 'A type of loan', 'An expense', 'A tax'),
    Q('What is an IPO?', 'Initial Public Offering', 'Internal Profit Organization', 'Investment Public Option', 'International Price Offering'),
    Q('What does ROI stand for?', 'Return on Investment', 'Rate of Interest', 'Return on Income', 'Ratio of Investment'),
    Q('What is a balance sheet?', 'A statement of assets and liabilities', 'A profit report', 'A cash flow statement', 'A budget'),
    Q('What does the law of supply state?', 'Price rises when supply falls', 'Price falls when supply falls', 'Demand is fixed', 'Supply equals demand always'),
    Q('What is a startup?', 'A newly founded company', 'A failing company', 'A government agency', 'A bank'),
    Q('Who is known as the founder of Amazon?', 'Jeff Bezos', 'Bill Gates', 'Elon Musk', 'Mark Zuckerberg'),
    Q('Who is the founder of Tesla?', 'Elon Musk', 'Jeff Bezos', 'Nikola Tesla', 'Steve Jobs'),
    Q('Who founded Microsoft?', 'Bill Gates and Paul Allen', 'Steve Jobs', 'Mark Zuckerberg', 'Larry Page'),
    Q('Who co-founded Apple?', 'Steve Jobs and Steve Wozniak', 'Bill Gates', 'Jeff Bezos', 'Elon Musk'),
    Q('What is a hedge fund?', 'A pooled investment fund with active strategies', 'A savings account', 'A government bond', 'A mutual index fund'),
    Q('What is compound interest?', 'Interest calculated on both principal and past interest', 'Interest on principal only', 'A fixed fee', 'A tax'),
    Q('What is an asset?', 'Something of value owned', 'A liability', 'A debt', 'An expense'),
    Q('What is a liability?', 'A financial obligation', 'An asset', 'An investment', 'A profit'),
    Q('What is revenue?', 'Total income from sales', 'Net profit', 'Gross profit only', 'Cost of goods'),
    Q('What is the difference between revenue and profit?', 'Profit is revenue minus expenses', 'They are the same', 'Revenue is after tax', 'Profit is before sales'),
    Q('What is a budget deficit?', 'Spending exceeds revenue', 'Revenue exceeds spending', 'Balanced budget', 'A tax cut'),
    Q('What is fiscal policy?', 'Government decisions on taxes and spending', 'Central bank interest rates', 'Trade policy', 'Monetary supply'),
    Q('What is monetary policy?', 'Central bank control of money and interest rates', 'Government taxation', 'Trade tariffs', 'Foreign aid'),
    Q('Which organization is the central bank of the US?', 'Federal Reserve', 'World Bank', 'IMF', 'Treasury Department'),
    Q('What is a tariff?', 'A tax on imports', 'A subsidy', 'A quota', 'A loan'),
    Q('What is outsourcing?', 'Contracting work to external companies', 'Hiring more staff', 'Buying companies', 'Exporting goods'),
    Q('What is a merger?', 'Two companies combining into one', 'A company split', 'A bankruptcy', 'An acquisition only'),
    Q('What is bankruptcy?', 'Legal inability to pay debts', 'High profitability', 'A type of tax', 'A stock split'),
    Q('What is the Dow Jones?', 'A stock market index', 'A bank', 'A bond', 'A currency'),
    Q('What does NASDAQ stand for?', 'National Association of Securities Dealers Automated Quotations', 'North American Stock Data', 'National Stock Exchange', 'North American Securities Dealers'),
    Q('What is a bull market?', 'A market with rising prices', 'A market with falling prices', 'A sideways market', 'A new market'),
    Q('What is a bear market?', 'A market with falling prices', 'A market with rising prices', 'A stable market', 'A regulated market'),
    Q('What is cryptocurrency?', 'A digital currency using cryptography', 'A paper currency', 'A stock', 'A bond'),
    Q('Who is credited with creating Bitcoin?', 'Satoshi Nakamoto', 'Elon Musk', 'Vitalik Buterin', 'Mark Zuckerberg'),
    Q('What is an index fund?', 'A fund that tracks a market index', 'A managed stock picker', 'A hedge fund', 'A pension'),
    Q('What is net worth?', 'Assets minus liabilities', 'Total income', 'Total savings', 'Revenue'),
    Q('What is a stock?', 'A share of ownership in a company', 'A loan to a company', 'A bond', 'A currency'),
    Q('What is a bond?', 'A debt instrument', 'A share of ownership', 'A type of cash', 'A tax credit'),
    Q('What is depreciation?', 'The decrease in asset value over time', 'An increase in asset value', 'A tax refund', 'A type of income'),
    Q('What is capital?', 'Money used to generate wealth', 'A type of debt', 'An expense', 'A liability'),
    Q('What is a venture capitalist?', 'An investor in startups', 'A bank', 'A government body', 'A tax collector'),
    Q('What is market share?', 'A company share of total sales in a market', 'The stock price', 'The number of employees', 'Total revenue'),
    Q('What is a cartel?', 'An agreement among firms to control prices', 'A government agency', 'A type of tax', 'A stock exchange'),
    Q('Which country has the largest economy in Europe?', 'Germany', 'France', 'United Kingdom', 'Italy'),
    Q('What is the World Trade Organization responsible for?', 'Regulating international trade', 'Setting interest rates', 'Providing loans to countries', 'Monitoring climate'),
    Q('What is microeconomics the study of?', 'Individual markets and actors', 'The whole economy', 'Government budgets', 'International trade'),
    Q('What is macroeconomics the study of?', 'The economy as a whole', 'Individual firms', 'Single markets', 'Consumer behaviour only'),
    Q('What is a trade deficit?', 'Imports exceed exports', 'Exports exceed imports', 'Balanced trade', 'No trade'),
    Q('What is a subsidy?', 'Government financial support', 'A tax on goods', 'A type of loan', 'A trade barrier'),
    Q('Which company was formerly called Google?', 'Alphabet', 'Meta', 'Amazon', 'Microsoft'),
    Q('What is the blockchain?', 'A distributed digital ledger', 'A type of bank', 'A stock exchange', 'An encryption algorithm'),
]


def build_business(rng):
    return list(BUSINESS_CURATED)


# =====================================================================
# Artificial Intelligence
# =====================================================================

AI_CURATED = [
    Q('What does AI stand for?', 'Artificial Intelligence', 'Automated Interface', 'Advanced Integration', 'Analog Input'),
    Q('What is machine learning?', 'Systems that learn from data', 'Systems that follow rules', 'A type of database', 'A programming language'),
    Q('Which is a supervised learning algorithm?', 'Linear regression', 'K-means', 'DBSCAN', 'Apriori'),
    Q('Which is an unsupervised learning algorithm?', 'K-means clustering', 'Logistic regression', 'Decision tree', 'SVM'),
    Q('What is a neural network?', 'A model inspired by the human brain', 'A computer network', 'A database', 'A data type'),
    Q('What is deep learning?', 'Neural networks with many layers', 'Learning deeply about data', 'A type of database', 'A search algorithm'),
    Q('What is a training dataset?', 'Data used to teach a model', 'Data used to test a model', 'Unused data', 'Raw sensor data'),
    Q('What is overfitting?', 'A model that performs well on training but poorly on new data', 'A model that underfits', 'A model with no data', 'A type of error'),
    Q('What is a loss function?', 'A measure of prediction error', 'A data loss', 'A memory leak', 'A type of optimizer'),
    Q('Which framework is popular for deep learning?', 'TensorFlow', 'Django', 'Flask', 'React'),
    Q('What does NLP stand for?', 'Natural Language Processing', 'Neural Language Program', 'New Language Protocol', 'Natural Logic Processing'),
    Q('What is computer vision?', 'Teaching computers to understand images', 'A type of monitor', 'Image storage', 'A programming language'),
    Q('What is a chatbot?', 'A program that simulates conversation', 'A search engine', 'A compiler', 'A database'),
    Q('What is reinforcement learning?', 'Learning through rewards and penalties', 'Learning from labeled data', 'Learning from unlabeled data', 'A type of search'),
    Q('What is an algorithm in AI?', 'A set of rules to solve a problem', 'A database table', 'A computer virus', 'A network protocol'),
    Q('What is a generative model?', 'A model that creates new data', 'A model that classifies data', 'A model that clusters data', 'A model that deletes data'),
    Q('What is GPT?', 'A generative pre-trained transformer', 'A type of computer', 'A search engine', 'A database'),
    Q('What is a transformer?', 'A neural network architecture', 'A power device', 'A database tool', 'A data type'),
    Q('What is the Turing test?', 'A test of machine intelligence', 'A hardware test', 'A software bug', 'A data test'),
    Q('Who proposed the Turing test?', 'Alan Turing', 'Albert Einstein', 'John McCarthy', 'Marvin Minsky'),
    Q('Who coined the term Artificial Intelligence?', 'John McCarthy', 'Alan Turing', 'Norbert Wiener', 'Marvin Minsky'),
    Q('What is a dataset?', 'A collection of data samples', 'A data type', 'A file format', 'A database table'),
    Q('What is feature engineering?', 'Selecting and creating input variables', 'Debugging code', 'Deploying models', 'Testing hardware'),
    Q('What is a bias in machine learning?', 'Systematic error in predictions', 'A hardware issue', 'A faster model', 'A data type'),
    Q('What is accuracy in ML?', 'The proportion of correct predictions', 'The speed of a model', 'The size of data', 'The loss value'),
    Q('What is a regression problem?', 'Predicting a continuous value', 'Predicting a category', 'Sorting data', 'Clustering data'),
    Q('What is a classification problem?', 'Predicting a category', 'Predicting a continuous value', 'Clustering data', 'Generating data'),
    Q('What is clustering?', 'Grouping similar data points', 'Predicting values', 'Ordering data', 'Deleting data'),
    Q('What is a hyperparameter?', 'A parameter set before training', 'A parameter learned during training', 'A data sample', 'A model output'),
    Q('What is gradient descent?', 'An optimization algorithm', 'A data structure', 'A loss function', 'A neural layer'),
    Q('What is an epoch in training?', 'One full pass over the training data', 'A type of neuron', 'A layer', 'A batch'),
    Q('What is a batch in ML?', 'A subset of training data processed together', 'A type of error', 'A hyperparameter', 'A neural network'),
    Q('What is an activation function?', 'A function that decides neuron output', 'A data loader', 'A loss function', 'An optimizer'),
    Q('Which is a common activation function?', 'ReLU', 'SQL', 'JSON', 'HTTP'),
    Q('What is a convolutional neural network used for?', 'Image processing', 'Text translation only', 'Audio only', 'Database queries'),
    Q('What is an LSTM?', 'A type of recurrent neural network', 'A database', 'A data type', 'A network cable'),
    Q('What is transfer learning?', 'Reusing a trained model for a new task', 'Transferring files', 'Moving data centers', 'Copying databases'),
    Q('What is an autoencoder?', 'A network that learns to reconstruct input', 'A data encoder', 'A file format', 'A network protocol'),
    Q('What is a recommendation system?', 'A system that suggests items', 'A search engine', 'A database', 'A spam filter'),
    Q('Which company developed ChatGPT?', 'OpenAI', 'Google', 'Meta', 'Microsoft'),
    Q('What is a prompt?', 'The input given to an AI model', 'A type of error', 'A data sample', 'A model weight'),
    Q('What is fine-tuning?', 'Further training a model on specific data', 'Deleting a model', 'Compressing a model', 'Testing hardware'),
    Q('What is inference in ML?', 'Using a trained model to make predictions', 'Training a model', 'Collecting data', 'Cleaning data'),
    Q('What is a weight in a neural network?', 'A learned parameter', 'A data point', 'A layer', 'An output'),
    Q('What is a neuron in an ANN?', 'A basic computational unit', 'A brain cell', 'A database row', 'A network router'),
    Q('What is a token in NLP?', 'A unit of text', 'A data type', 'A model', 'A layer'),
    Q('What is sentiment analysis?', 'Determining the emotion in text', 'Analyzing data size', 'Analyzing network traffic', 'Compressing text'),
    Q('What is speech recognition?', 'Converting speech to text', 'Converting text to speech', 'Analyzing music', 'Translating languages'),
    Q('What is a hallucination in AI?', 'A model generating false information', 'A hardware error', 'A data leak', 'A loss value'),
    Q('What is an AI agent?', 'An AI system that takes actions', 'A human worker', 'A database', 'A web server'),
    Q('What is RAG?', 'Retrieval-augmented generation', 'A database query', 'A neural layer', 'A data format'),
    Q('What is an embedding?', 'A vector representation of data', 'A data type', 'A model layer', 'A loss function'),
    Q('What is dimensionality reduction?', 'Reducing the number of features', 'Reducing data size', 'Increasing features', 'Compressing files'),
    Q('What is PCA?', 'Principal Component Analysis', 'Personal Computer App', 'Program Control Algorithm', 'Parameter Classifier'),
    Q('What is an SVM?', 'Support Vector Machine', 'System Virtual Machine', 'Statistical Variance Model', 'Supervised Vector Model'),
    Q('What is a decision tree?', 'A tree-like model of decisions', 'A data structure only', 'A type of database', 'A network topology'),
    Q('What is a random forest?', 'An ensemble of decision trees', 'A single tree', 'A data structure', 'A clustering method'),
    Q('What is ensemble learning?', 'Combining multiple models', 'Training one model', 'A data type', 'A loss function'),
    Q('What is bias-variance tradeoff?', 'Balancing model error sources', 'A data quality issue', 'A hardware limit', 'A hyperparameter'),
]


def build_ai(rng):
    return list(AI_CURATED)


# =====================================================================
# Cybersecurity
# =====================================================================

CYBER_CURATED = [
    Q('What is phishing?', 'A fraud attempt to steal information', 'A type of firewall', 'A network protocol', 'A virus vaccine'),
    Q('What is malware?', 'Malicious software', 'A type of hardware', 'A network cable', 'A data format'),
    Q('Which is a type of malware that demands payment?', 'Ransomware', 'Adware', 'Spyware', 'Firewall'),
    Q('What is a firewall used for?', 'Filtering network traffic', 'Speeding up networks', 'Storing data', 'Compiling code'),
    Q('What is encryption?', 'Converting data into a secure code', 'Deleting data', 'Compressing data', 'Sorting data'),
    Q('What is a VPN?', 'A secure private network over the internet', 'A type of virus', 'A data format', 'A firewall'),
    Q('What does VPN stand for?', 'Virtual Private Network', 'Very Private Network', 'Virtual Public Network', 'Verified Packet Network'),
    Q('What is two-factor authentication?', 'Using two verification methods', 'Using two passwords', 'Two-step login only', 'Two network cards'),
    Q('What is a brute force attack?', 'Trying many passwords repeatedly', 'A power outage', 'A data breach', 'A phishing email'),
    Q('What is SQL injection?', 'Injecting malicious SQL into queries', 'A database backup', 'A query optimizer', 'A data type'),
    Q('What is a DDoS attack?', 'Overwhelming a service with traffic', 'A data leak', 'A password attack', 'A type of virus'),
    Q('What does DDoS stand for?', 'Distributed Denial of Service', 'Direct Denial of Service', 'Dynamic Data Offload Service', 'Distributed Data System'),
    Q('What is a man-in-the-middle attack?', 'Intercepting communication between parties', 'A type of firewall', 'A data backup', 'A type of virus'),
    Q('What is a zero-day vulnerability?', 'An unknown unpatched vulnerability', 'A patch released today', 'A type of malware', 'A network issue'),
    Q('What is a patch?', 'A software update that fixes issues', 'A type of malware', 'A network cable', 'A data format'),
    Q('What is social engineering?', 'Manipulating people to reveal information', 'A type of malware', 'A network attack', 'A programming method'),
    Q('What is a password manager?', 'Software that stores passwords securely', 'A type of hacker', 'A network protocol', 'A firewall'),
    Q('What is a strong password?', 'Long, complex and unique', 'Short and simple', 'Same for all accounts', 'Your name only'),
    Q('What is the principle of least privilege?', 'Giving only necessary access', 'Giving all users admin access', 'Removing all access', 'Sharing passwords'),
    Q('What is a security audit?', 'A review of security practices', 'A data backup', 'A type of malware', 'A network scan'),
    Q('What is a virus?', 'A self-replicating malicious program', 'A type of firewall', 'A network cable', 'A data format'),
    Q('What is a worm?', 'Self-spreading malware without a host', 'A type of firewall', 'A virus vaccine', 'A password'),
    Q('What is a Trojan horse?', 'Malware disguised as legitimate software', 'A network device', 'A type of encryption', 'A data format'),
    Q('What is a keylogger?', 'Software that records keystrokes', 'A type of firewall', 'A network protocol', 'A password manager'),
    Q('What is a botnet?', 'A network of infected computers', 'A type of firewall', 'A data center', 'A social network'),
    Q('What is HTTPS?', 'Secure HTTP with encryption', 'A type of firewall', 'A faster HTTP', 'An email protocol'),
    Q('What does TLS stand for?', 'Transport Layer Security', 'Transfer Layer Security', 'Transmission Line Service', 'Total Log Security'),
    Q('What is a certificate in HTTPS?', 'A digital identity credential', 'A type of virus', 'A password', 'A network cable'),
    Q('What is a hash?', 'A one-way data fingerprint', 'An encrypted password only', 'A type of firewall', 'A network protocol'),
    Q('What is MD5?', 'An outdated hash function', 'A modern encryption', 'A firewall', 'A password'),
    Q('What is a salt in password hashing?', 'Random data added to passwords', 'A type of attack', 'A network cable', 'A password'),
    Q('What is an antivirus?', 'Software that detects malware', 'A firewall', 'A network protocol', 'A password manager'),
    Q('What is a white hat hacker?', 'An ethical hacker', 'A malicious hacker', 'A script kiddie', 'A virus'),
    Q('What is a black hat hacker?', 'A malicious hacker', 'An ethical hacker', 'A security auditor', 'A firewall'),
    Q('What is penetration testing?', 'Authorized simulated attacks', 'A data backup', 'A type of malware', 'A network scan'),
    Q('What is a vulnerability?', 'A weakness in a system', 'A type of malware', 'A firewall', 'A network protocol'),
    Q('What is an exploit?', 'Code that takes advantage of a vulnerability', 'A type of firewall', 'A security patch', 'A data format'),
    Q('What is a security patch?', 'An update that fixes vulnerabilities', 'A type of malware', 'A network cable', 'A password'),
    Q('What is data breach?', 'Unauthorized access to data', 'A data backup', 'A type of firewall', 'A network upgrade'),
    Q('What is ransomware encryption?', 'Locking data until payment', 'Deleting data', 'Compressing data', 'Backing up data'),
    Q('What is a honeypot?', 'A decoy system to trap attackers', 'A type of honey', 'A firewall', 'A password manager'),
    Q('What is an IDS?', 'Intrusion Detection System', 'Internet Data Service', 'Internal Defense System', 'Input Data Source'),
    Q('What is an IPS?', 'Intrusion Prevention System', 'Internet Protocol Service', 'Internal Processing System', 'Input Password System'),
    Q('What is authentication?', 'Verifying a users identity', 'Encrypting data', 'Filtering traffic', 'Backing up data'),
    Q('What is authorization?', 'Giving permission to access resources', 'Verifying identity', 'Encrypting data', 'Blocking traffic'),
    Q('What is non-repudiation?', 'Proof that a message was sent', 'A type of attack', 'A firewall rule', 'A password'),
    Q('What is a digital signature?', 'A cryptographic way to verify authenticity', 'A typed name', 'A password', 'A fingerprint scan'),
    Q('What is a phishing email characteristic?', 'Urgency and suspicious links', 'Clear sender', 'No attachments', 'Personal greeting'),
    Q('What is whaling?', 'Phishing targeting high-profile victims', 'A type of whale', 'A network attack', 'A virus'),
    Q('What is vishing?', 'Voice phishing over phone', 'Video phishing', 'A type of virus', 'A network attack'),
    Q('What is smishing?', 'Phishing via SMS', 'Smiling phishing', 'A type of virus', 'A network attack'),
    Q('What is a zero-trust model?', 'Trusting nothing by default', 'Trusting everything', 'No security model', 'A firewall'),
    Q('What is endpoint security?', 'Securing devices like laptops', 'Securing the network only', 'Securing the cloud only', 'Securing emails only'),
    Q('What is identity theft?', 'Stealing someones identity details', 'A type of virus', 'A network attack', 'A data format'),
    Q('What is a security key?', 'A hardware authentication device', 'A type of virus', 'A password', 'A firewall'),
    Q('What is a log in cybersecurity?', 'A record of system events', 'A type of malware', 'A network cable', 'A password'),
    Q('What is incident response?', 'Handling a security incident', 'A data backup', 'A firewall rule', 'A network scan'),
    Q('What is a threat actor?', 'Someone who causes security harm', 'A security tool', 'A firewall', 'A data format'),
    Q('What is a vulnerability scanner?', 'A tool that finds weaknesses', 'A malware type', 'A firewall', 'A password manager'),
    Q('What is a security policy?', 'Rules for protecting information', 'A type of malware', 'A network cable', 'A password'),
]


def build_cyber(rng):
    return list(CYBER_CURATED)


# =====================================================================
# Networking
# =====================================================================

NET_CURATED = [
    Q('What does OSI stand for?', 'Open Systems Interconnection', 'Open Source Internet', 'Operating System Interface', 'Online System Integration'),
    Q('How many layers are in the OSI model?', '7', '5', '6', '4'),
    Q('Which layer of the OSI model is the physical layer?', 'Layer 1', 'Layer 2', 'Layer 3', 'Layer 7'),
    Q('Which OSI layer handles routing?', 'Network layer', 'Data link layer', 'Transport layer', 'Application layer'),
    Q('Which protocol operates at the network layer?', 'IP', 'TCP', 'HTTP', 'FTP'),
    Q('Which protocol operates at the transport layer?', 'TCP', 'IP', 'Ethernet', 'HTTP'),
    Q('What does TCP stand for?', 'Transmission Control Protocol', 'Transfer Control Protocol', 'Transport Communication Protocol', 'Total Control Protocol'),
    Q('What does IP stand for?', 'Internet Protocol', 'Internal Protocol', 'Internet Process', 'Integrated Protocol'),
    Q('What does UDP stand for?', 'User Datagram Protocol', 'Unified Data Protocol', 'Universal Datagram Protocol', 'User Data Pack'),
    Q('Which protocol is connection-oriented?', 'TCP', 'UDP', 'ICMP', 'ARP'),
    Q('Which protocol is connectionless?', 'UDP', 'TCP', 'HTTP', 'FTP'),
    Q('What is an IP address?', 'A unique network address', 'A web address', 'An email address', 'A file name'),
    Q('How many bits are in an IPv4 address?', '32', '64', '128', '16'),
    Q('How many bits are in an IPv6 address?', '128', '32', '64', '256'),
    Q('What does IPv6 provide over IPv4?', 'Larger address space', 'Faster speed only', 'Less security', 'Smaller packets'),
    Q('What is a subnet mask used for?', 'Separating network and host parts', 'Encrypting data', 'Routing emails', 'Storing data'),
    Q('What does a router do?', 'Routes packets between networks', 'Connects devices in a LAN', 'Stores files', 'Blocks malware'),
    Q('What does a switch do?', 'Connects devices within a network', 'Routes between networks', 'Modulates signals', 'Stores data'),
    Q('What is a MAC address?', 'A hardware address of a network device', 'An IP address', 'A web address', 'A password'),
    Q('How many bits are in a MAC address?', '48', '32', '64', '16'),
    Q('What does LAN stand for?', 'Local Area Network', 'Long Area Network', 'Large Access Network', 'Local Access Node'),
    Q('What does WAN stand for?', 'Wide Area Network', 'Wireless Area Network', 'World Access Network', 'Wide Access Node'),
    Q('What does Wi-Fi use to transmit data?', 'Radio waves', 'Light', 'Sound', 'Electricity only'),
    Q('What is the standard for Wi-Fi?', 'IEEE 802.11', 'IEEE 802.3', 'IEEE 802.1', 'IEEE 802.5'),
    Q('What is Ethernet?', 'A wired networking technology', 'A wireless technology', 'A protocol suite', 'An IP version'),
    Q('What is DNS?', 'Domain Name System', 'Data Network Service', 'Dynamic Name Server', 'Digital Network System'),
    Q('What does DHCP stand for?', 'Dynamic Host Configuration Protocol', 'Data Host Control Protocol', 'Dynamic Host Control Process', 'Digital Host Configuration Protocol'),
    Q('What is a gateway?', 'A device connecting different networks', 'A type of cable', 'A virus', 'An IP address'),
    Q('What is a proxy server?', 'An intermediary between client and server', 'A type of router', 'A firewall only', 'A DNS server'),
    Q('What is a packet?', 'A unit of data transmitted', 'A type of cable', 'A virus', 'A port'),
    Q('What is a port in networking?', 'A logical connection endpoint', 'A physical connector', 'A file', 'A protocol'),
    Q('Which port is used by HTTP by default?', '80', '443', '8080', '21'),
    Q('Which port is used by HTTPS by default?', '443', '80', '8080', '22'),
    Q('Which port is used by FTP by default?', '21', '22', '25', '80'),
    Q('Which port is used by SSH by default?', '22', '21', '80', '443'),
    Q('Which protocol is used for email sending?', 'SMTP', 'FTP', 'HTTP', 'SNMP'),
    Q('Which protocol retrieves email?', 'IMAP', 'SMTP', 'FTP', 'HTTP'),
    Q('What does IMAP stand for?', 'Internet Message Access Protocol', 'Internet Mail Application Protocol', 'Instant Message Access Process', 'Internal Mail Access Protocol'),
    Q('What does FTP stand for?', 'File Transfer Protocol', 'Fast Transfer Protocol', 'File Transmission Process', 'Final Transfer Protocol'),
    Q('Which protocol is used to translate domain names to IP?', 'DNS', 'DHCP', 'HTTP', 'FTP'),
    Q('What is a firewall in networking?', 'A filter for network traffic', 'A router', 'A cable', 'A server'),
    Q('What is bandwidth?', 'Maximum data transfer rate', 'The delay', 'The packet size', 'The IP address'),
    Q('What is latency?', 'The delay in data transmission', 'The data rate', 'The packet size', 'The bandwidth'),
    Q('What is throughput?', 'Actual data transferred over time', 'The maximum rate', 'The delay', 'The error rate'),
    Q('What is a star topology?', 'All devices connected to a central hub', 'Devices in a ring', 'Devices in a line', 'Devices all connected'),
    Q('What is a mesh topology?', 'Every device connected to every other', 'Devices in a ring', 'Devices in a line', 'Devices to a hub'),
    Q('What is CSMA/CD?', 'A collision detection method', 'An encryption method', 'A routing protocol', 'A DNS record'),
    Q('What is a hub?', 'A basic device that broadcasts data', 'A smart switch', 'A router', 'A modem'),
    Q('What is a modem?', 'Modulates and demodulates signals', 'A type of switch', 'A router', 'A firewall'),
    Q('What is an SSID?', 'The name of a Wi-Fi network', 'An IP address', 'A password', 'A MAC address'),
    Q('What is a VPN?', 'A secure tunnel over the internet', 'A type of cable', 'A firewall', 'A proxy'),
    Q('What is NAT?', 'Network Address Translation', 'Network Access Table', 'Node Address Transfer', 'Network Action Terminal'),
    Q('What is a protocol?', 'A set of rules for communication', 'A type of cable', 'A network device', 'A data format'),
    Q('What is the ping command used for?', 'Testing network connectivity', 'Sending emails', 'Transferring files', 'Encrypting data'),
    Q('What does ICMP stand for?', 'Internet Control Message Protocol', 'Internet Connection Message Protocol', 'Internal Control Message Process', 'Integrated Communication Protocol'),
    Q('What is a traceroute used for?', 'Showing the path packets take', 'Testing speed', 'Encrypting data', 'Blocking traffic'),
    Q('What is a load balancer?', 'Distributes traffic across servers', 'A type of cable', 'A router', 'A firewall'),
    Q('What is the cloud in networking?', 'Remote servers accessed over the internet', 'A weather service', 'A local server', 'A data cable'),
    Q('What is a server?', 'A computer that provides services', 'A type of cable', 'A network protocol', 'An IP address'),
]


def build_networking(rng):
    return list(NET_CURATED)


# =====================================================================
# Database Systems
# =====================================================================

DB_CURATED = [
    Q('What does DBMS stand for?', 'Database Management System', 'Data Backup Management System', 'Digital Binary Memory System', 'Dynamic Buffer Management System'),
    Q('What is a database?', 'An organized collection of data', 'A type of computer', 'A network protocol', 'A programming language'),
    Q('Which is a relational database?', 'PostgreSQL', 'MongoDB', 'Redis', 'Neo4j'),
    Q('Which is a NoSQL database?', 'MongoDB', 'MySQL', 'PostgreSQL', 'Oracle'),
    Q('What is a table in a database?', 'A collection of records', 'A file', 'A query', 'A server'),
    Q('What is a row in a database table called?', 'Record', 'Column', 'Table', 'Index'),
    Q('What is a column in a database table called?', 'Field', 'Record', 'Row', 'Table'),
    Q('What is a primary key?', 'A unique identifier for a record', 'A foreign key', 'An index', 'A table name'),
    Q('What is a foreign key?', 'A key referencing another table', 'A primary key', 'A duplicate key', 'An index'),
    Q('What is a composite key?', 'A key made of multiple columns', 'A single-column key', 'A foreign key', 'An index'),
    Q('What does SQL stand for?', 'Structured Query Language', 'Simple Query Language', 'System Query Logic', 'Standard Query Language'),
    Q('Which SQL command retrieves data?', 'SELECT', 'GET', 'FETCH', 'PULL'),
    Q('Which SQL command inserts data?', 'INSERT', 'ADD', 'CREATE', 'PUT'),
    Q('Which SQL command updates data?', 'UPDATE', 'MODIFY', 'CHANGE', 'SET'),
    Q('Which SQL command deletes data?', 'DELETE', 'DROP', 'REMOVE', 'TRUNCATE'),
    Q('What is a query?', 'A request for data', 'A data type', 'A table', 'A server'),
    Q('What is an index?', 'A structure that speeds up queries', 'A table copy', 'A stored procedure', 'A backup'),
    Q('What is normalization?', 'Reducing redundancy in data', 'Encrypting data', 'Increasing data size', 'Sorting data'),
    Q('What is the first normal form (1NF)?', 'Atomic values in columns', 'No duplicate columns', 'No transitive dependencies', 'All keys primary'),
    Q('What is ACID in databases?', 'Atomicity, Consistency, Isolation, Durability', 'Access, Control, Index, Data', 'All, Create, Insert, Delete', 'Auto, Check, Input, Drop'),
    Q('What is a transaction?', 'A unit of work with multiple operations', 'A single query', 'A table', 'A backup'),
    Q('What is a JOIN?', 'Combining rows from multiple tables', 'A data type', 'A primary key', 'A backup'),
    Q('What is an inner join?', 'Only matching rows from both tables', 'All rows from left table', 'All rows from both', 'No rows'),
    Q('What is a left join?', 'All rows from left and matches from right', 'Only matching rows', 'All rows from right', 'No rows'),
    Q('What is a view in a database?', 'A virtual table based on a query', 'A physical table', 'An index', 'A backup'),
    Q('What is a stored procedure?', 'A saved set of SQL statements', 'A table', 'An index', 'A view'),
    Q('What is a trigger in a database?', 'Code that runs on data changes', 'A table constraint', 'An index', 'A view'),
    Q('What is a constraint?', 'A rule applied to data', 'A data type', 'A query', 'An index'),
    Q('What is the UNIQUE constraint?', 'Values must be distinct', 'Values can be null', 'Values must be numeric', 'Values must repeat'),
    Q('What is the NOT NULL constraint?', 'Column cannot be empty', 'Column must be empty', 'Column must be unique', 'Column is primary'),
    Q('What is a schema?', 'The structure of a database', 'A type of query', 'A data row', 'A server'),
    Q('What is a backup?', 'A copy of data for recovery', 'A query', 'An index', 'A transaction'),
    Q('What is data redundancy?', 'Duplicate data storage', 'Missing data', 'Encrypted data', 'Indexed data'),
    Q('What is data integrity?', 'Accuracy and consistency of data', 'Data encryption', 'Data size', 'Data speed'),
    Q('What is a data warehouse?', 'A system for analysis of large data', 'A transaction database', 'An index', 'A backup'),
    Q('What is ETL?', 'Extract, Transform, Load', 'Enter, Transfer, Load', 'Extract, Test, Load', 'Edit, Transform, Log'),
    Q('What is a primary key value?', 'Must be unique and not null', 'Can be null', 'Can be duplicated', 'Is optional'),
    Q('What is a candidate key?', 'A column that could be primary key', 'A foreign key', 'A duplicate column', 'An index'),
    Q('What is a super key?', 'A set of columns identifying a record', 'A primary key', 'A foreign key', 'An index'),
    Q('What is cardinality?', 'The number of rows in a table', 'The number of columns', 'A data type', 'A constraint'),
    Q('What is a relationship in DB design?', 'An association between tables', 'A data type', 'A query', 'An index'),
    Q('What is a one-to-many relationship?', 'One record relates to many records', 'Many records relate to one', 'One to one', 'Many to many'),
    Q('What is many-to-many relationship?', 'Records relate on both sides', 'One to one', 'One to many', 'No relationship'),
    Q('What is a junction table?', 'A table linking many-to-many relations', 'A primary key', 'An index', 'A backup'),
    Q('What is query optimization?', 'Making queries run faster', 'Deleting queries', 'Encrypting queries', 'Storing queries'),
    Q('What is an ORM?', 'Object-Relational Mapping', 'Online Record Manager', 'Ordered Relational Model', 'Object Request Method'),
    Q('Which SQL function counts rows?', 'COUNT()', 'SUM()', 'MAX()', 'AVG()'),
    Q('Which SQL function returns the sum?', 'SUM()', 'COUNT()', 'AVG()', 'MAX()'),
    Q('Which SQL clause filters grouped data?', 'HAVING', 'WHERE', 'GROUP BY only', 'ORDER BY'),
    Q('What is a database transaction rollback?', 'Undoing a transaction', 'Committing a transaction', 'Backing up data', 'Deleting a table'),
    Q('What is a database commit?', 'Saving a transaction permanently', 'Undoing a transaction', 'Deleting data', 'Creating a backup'),
    Q('What is concurrency control?', 'Managing simultaneous data access', 'Encrypting data', 'Backing up data', 'Indexing data'),
    Q('What is a deadlock in databases?', 'Transactions waiting on each other', 'A data type', 'A query', 'A backup'),
    Q('What is a NoSQL key-value store?', 'Redis', 'MySQL', 'PostgreSQL', 'Oracle'),
    Q('Which database is document-oriented?', 'MongoDB', 'MySQL', 'SQLite', 'Oracle'),
    Q('What is sharding?', 'Splitting data across servers', 'Encrypting data', 'Sorting data', 'Backing up data'),
    Q('What is a data model?', 'A way of structuring data', 'A type of query', 'An index', 'A backup'),
    Q('What is the entity-relationship model?', 'A diagram of tables and relationships', 'A query plan', 'A data type', 'A constraint'),
]


def build_database(rng):
    return list(DB_CURATED)


# =====================================================================
# Web Development
# =====================================================================

WEB_CURATED = [
    Q('What does HTML stand for?', 'HyperText Markup Language', 'Hyper Text Machine Language', 'High Tech Markup Language', 'HyperText Model Language'),
    Q('What does CSS stand for?', 'Cascading Style Sheets', 'Computer Style Sheets', 'Creative Style System', 'Cascading System Sheets'),
    Q('What does JavaScript add to a web page?', 'Interactivity', 'Structure', 'Styling', 'Storage'),
    Q('Which tag defines a hyperlink in HTML?', '<a>', '<link>', '<href>', '<url>'),
    Q('Which HTML tag is used for the largest heading?', '<h1>', '<h6>', '<head>', '<header>'),
    Q('Which attribute specifies an image source?', 'src', 'href', 'alt', 'img'),
    Q('Which CSS property changes text color?', 'color', 'font-color', 'text-color', 'background-color'),
    Q('Which CSS property changes the background color?', 'background-color', 'color', 'bgcolor', 'background'),
    Q('Which CSS unit is relative to the root font size?', 'rem', 'px', 'em', 'pt'),
    Q('Which is a CSS framework?', 'Bootstrap', 'Django', 'Express', 'Laravel'),
    Q('Which is a JavaScript framework?', 'React', 'Flask', 'Rails', 'Laravel'),
    Q('Which is a backend framework for Python?', 'Django', 'React', 'Angular', 'Vue'),
    Q('Which JavaScript library is used for DOM manipulation?', 'jQuery', 'jQuery UI only', 'Bootstrap', 'Sass'),
    Q('What does the DOM represent?', 'The document structure of a web page', 'A database', 'A server', 'A browser plugin'),
    Q('Which HTTP method fetches data?', 'GET', 'POST', 'PUT', 'DELETE'),
    Q('Which HTTP method submits data?', 'POST', 'GET', 'PUT', 'PATCH'),
    Q('Which HTTP status means page not found?', '404', '200', '500', '301'),
    Q('Which HTTP status means server error?', '500', '404', '200', '302'),
    Q('What does API stand for?', 'Application Programming Interface', 'Application Process Integration', 'Automated Program Interface', 'Advanced Protocol Interface'),
    Q('Which format is used for web APIs?', 'JSON', 'CSV', 'XML only', 'YAML only'),
    Q('What is a frontend?', 'The user-facing part of a website', 'The server code', 'The database', 'The network'),
    Q('What is a backend?', 'The server-side part of an application', 'The UI', 'The CSS', 'The HTML'),
    Q('What is a full-stack developer?', 'One who works on frontend and backend', 'A frontend specialist', 'A backend specialist', 'A database admin'),
    Q('Which tag creates a dropdown list in HTML?', '<select>', '<dropdown>', '<option>', '<list>'),
    Q('Which HTML attribute makes an input required?', 'required', 'mandatory', 'needed', 'force'),
    Q('Which CSS property makes text bold?', 'font-weight', 'font-style', 'text-style', 'bold'),
    Q('Which CSS property adds space inside an element?', 'padding', 'margin', 'border', 'spacing'),
    Q('Which CSS property adds space outside an element?', 'margin', 'padding', 'border', 'outline'),
    Q('What is responsive design?', 'Design that adapts to screen size', 'Fast loading design', 'Animated design', 'Dark design'),
    Q('Which CSS feature creates responsive layouts with columns?', 'Grid and Flexbox', 'Tables', 'Frames', 'Flash'),
    Q('What does a media query do?', 'Applies CSS based on device conditions', 'Loads media files', 'Creates animations', 'Caches images'),
    Q('Which HTML element holds JavaScript?', '<script>', '<js>', '<javascript>', '<code>'),
    Q('Which HTML element holds CSS?', '<style>', '<css>', '<stylesheet>', '<design>'),
    Q('What is a browser?', 'Software to view web pages', 'A web server', 'A database', 'An OS'),
    Q('Which company makes the Chrome browser?', 'Google', 'Microsoft', 'Mozilla', 'Apple'),
    Q('What is a URL?', 'Uniform Resource Locator', 'Universal Resource Link', 'Uniform Response Locator', 'Universal Request Link'),
    Q('Which protocol is used to load web pages?', 'HTTP/HTTPS', 'FTP', 'SMTP', 'SSH'),
    Q('What is a web server?', 'A computer that serves web pages', 'A browser', 'A database', 'A router'),
    Q('What is hosting?', 'Storing a website on a server', 'Designing a website', 'Debugging a website', 'SEO'),
    Q('What is a CMS?', 'Content Management System', 'Computer Management System', 'Content Markup System', 'Cloud Management Service'),
    Q('Which is a popular CMS?', 'WordPress', 'Django', 'React', 'MySQL'),
    Q('What is SEO?', 'Search Engine Optimization', 'Server Engine Operation', 'Site Enhancement Order', 'Search Engine Order'),
    Q('What is a cookie?', 'A small piece of data stored by a browser', 'A type of malware', 'A web server', 'A CSS file'),
    Q('What is localStorage?', 'Browser storage for data', 'A database', 'A cache only', 'A server'),
    Q('What is sessionStorage?', 'Browser storage that lasts for the session', 'Permanent browser storage', 'A database', 'A cache'),
    Q('What is a PWA?', 'Progressive Web App', 'Private Web App', 'Personal Web Address', 'Public Web Application'),
    Q('What is web accessibility?', 'Making sites usable for everyone', 'Making sites fast', 'Making sites secure', 'Making sites animated'),
    Q('What does aria-label do?', 'Provides an accessible label', 'Changes color', 'Adds animation', 'Loads data'),
    Q('What is a single-page application?', 'An app that loads once and updates dynamically', 'A site with one page', 'A static site', 'A blog'),
    Q('Which is a build tool for frontend?', 'Webpack', 'Django', 'Flask', 'MySQL'),
    Q('What is npm?', 'A Node.js package manager', 'A database', 'A web server', 'A CSS framework'),
    Q('What is Node.js?', 'A JavaScript runtime', 'A database', 'A browser', 'An OS'),
    Q('What is TypeScript?', 'A typed superset of JavaScript', 'A database', 'A CSS framework', 'A Python library'),
    Q('What is SASS?', 'A CSS preprocessor', 'A database', 'A JS framework', 'A web server'),
    Q('Which element is used for a form in HTML?', '<form>', '<input>', '<button>', '<field>'),
    Q('What does the target="_blank" attribute do?', 'Opens a link in a new tab', 'Opens in same tab', 'Opens a file', 'Refreshes the page'),
    Q('Which tag embeds a video in HTML5?', '<video>', '<media>', '<film>', '<play>'),
    Q('What is a CDN?', 'Content Delivery Network', 'Content Data Node', 'Central Data Network', 'Code Delivery Network'),
    Q('What is caching?', 'Storing copies of data for speed', 'Deleting data', 'Encrypting data', 'Compressing data'),
    Q('What is minification?', 'Removing unnecessary characters from code', 'Adding comments', 'Encrypting code', 'Compiling code'),
    Q('Which tool inspects network requests in a browser?', 'Developer tools', 'Command prompt', 'Text editor', 'SQL client'),
]


def build_web(rng):
    return list(WEB_CURATED)


# =====================================================================
# Operating Systems
# =====================================================================

OS_CURATED = [
    Q('What is an operating system?', 'Software that manages hardware and software', 'A type of browser', 'A programming language', 'A database'),
    Q('Which is an operating system?', 'Linux', 'Chrome', 'Firefox', 'Photoshop'),
    Q('Which is a mobile operating system?', 'Android', 'Windows XP', 'Ubuntu Server', 'Debian'),
    Q('What is the kernel?', 'The core of the OS', 'A user interface', 'A file type', 'A browser'),
    Q('What is a process?', 'A program in execution', 'A file', 'A hardware device', 'A user'),
    Q('What is a thread?', 'The smallest unit of execution', 'A process', 'A file', 'A memory cell'),
    Q('What is multitasking?', 'Running multiple tasks at once', 'Running one task', 'Deleting tasks', 'Renaming tasks'),
    Q('What is scheduling?', 'Deciding which process runs next', 'Deleting processes', 'Storing files', 'Managing memory only'),
    Q('What is a scheduler algorithm FIFO?', 'First come, first served', 'Shortest first', 'Random', 'Priority only'),
    Q('What is round-robin scheduling?', 'Each process gets a time slice', 'Longest first', 'Random', 'No scheduling'),
    Q('What is a context switch?', 'Switching between processes', 'A type of virus', 'A reboot', 'A file operation'),
    Q('What is a deadlock?', 'Processes waiting for each other forever', 'A crash', 'A memory leak', 'A reboot'),
    Q('What are the four conditions for deadlock?', 'Mutual exclusion, hold and wait, no preemption, circular wait', 'One condition only', 'Two conditions', 'None'),
    Q('What is a semaphore?', 'A synchronization mechanism', 'A file', 'A process', 'A thread'),
    Q('What is a mutex?', 'A mutual exclusion lock', 'A file type', 'A process', 'A scheduler'),
    Q('What is a race condition?', 'Multiple processes accessing shared data unsafely', 'A fast process', 'A hardware fault', 'A type of virus'),
    Q('What is virtual memory?', 'Using disk as extension of RAM', 'A type of ROM', 'Cache memory', 'Register memory'),
    Q('What is paging?', 'Dividing memory into fixed pages', 'Compressing files', 'Encrypting data', 'Clearing cache'),
    Q('What is segmentation?', 'Dividing memory into variable segments', 'Dividing into fixed pages', 'Compressing files', 'Encrypting data'),
    Q('What is a page fault?', 'Accessing a page not in memory', 'A disk error', 'A crash', 'A virus'),
    Q('What is thrashing?', 'Excessive paging reducing performance', 'A reboot', 'A disk failure', 'A virus'),
    Q('What is a file system?', 'How files are stored and organized', 'A type of file', 'A process', 'A thread'),
    Q('Which file system does Windows commonly use?', 'NTFS', 'ext4', 'APFS', 'FAT12'),
    Q('Which file system does Linux commonly use?', 'ext4', 'NTFS', 'HFS+', 'exFAT'),
    Q('Which file system does macOS commonly use?', 'APFS', 'ext4', 'NTFS', 'FAT32'),
    Q('What is an inode in Linux?', 'A data structure for a file', 'A user', 'A process', 'A directory'),
    Q('What is a directory?', 'A folder containing files', 'A type of file', 'A process', 'A device'),
    Q('What is the root directory in Linux?', '/', 'C:\\', '\\', 'home'),
    Q('What is the root user in Linux?', 'A superuser with all permissions', 'A regular user', 'A guest user', 'A system service'),
    Q('What is the command to list files in Linux?', 'ls', 'dir', 'list', 'show'),
    Q('What is the command to change directories in Linux?', 'cd', 'chdir', 'move', 'go'),
    Q('What is the command to copy files in Linux?', 'cp', 'copy', 'mv', 'cpdir'),
    Q('What is the command to move files in Linux?', 'mv', 'move', 'cp', 'rm'),
    Q('What is the command to delete files in Linux?', 'rm', 'del', 'delete', 'remove'),
    Q('What does chmod do?', 'Changes file permissions', 'Changes file owner', 'Changes directory', 'Deletes a file'),
    Q('What does chown do?', 'Changes file owner', 'Changes permissions', 'Creates a file', 'Moves a file'),
    Q('What is the shell?', 'A command-line interface to the OS', 'A GUI', 'A browser', 'A kernel'),
    Q('Which shell is common on Linux?', 'Bash', 'PowerShell', 'CMD', 'Zsh only'),
    Q('What is a daemon?', 'A background process', 'A virus', 'A user', 'A file'),
    Q('What is a service in Linux?', 'A background daemon', 'A GUI app', 'A shell script', 'A kernel module'),
    Q('What is systemd?', 'An init system for Linux', 'A browser', 'A file system', 'A compiler'),
    Q('What is the BIOS?', 'Firmware that boots the computer', 'An OS', 'A driver', 'A browser'),
    Q('What is UEFI?', 'A modern boot firmware', 'An OS', 'A file system', 'A protocol'),
    Q('What is a bootloader?', 'Software that loads the OS', 'A virus', 'A driver', 'A shell'),
    Q('What is GRUB?', 'A common Linux bootloader', 'An OS', 'A file system', 'A browser'),
    Q('What is a driver?', 'Software that controls hardware', 'A virus', 'A process', 'A file'),
    Q('What is an interrupt?', 'A signal to the CPU', 'A crash', 'A reboot', 'A file'),
    Q('What is a system call?', 'A request to the kernel', 'A shell command', 'A reboot', 'A virus'),
    Q('What is the difference between user mode and kernel mode?', 'Kernel mode has full access', 'User mode has full access', 'They are identical', 'Both limited'),
    Q('What is RAM used for?', 'Temporary data storage for running programs', 'Permanent storage', 'Only for the OS', 'Only for files'),
    Q('What is swap space?', 'Disk space used as virtual memory', 'A partition for boot', 'A cache', 'A file system'),
    Q('What is a process state?', 'The current status of a process', 'A file state', 'A memory state', 'A CPU state'),
    Q('What is the ready state of a process?', 'Waiting for CPU', 'Running', 'Terminated', 'Blocked on IO'),
    Q('What is an idle process?', 'A process that does nothing', 'A high priority process', 'A virus', 'A kernel process'),
    Q('What is a zombie process?', 'A terminated process waiting for parent', 'An undead virus', 'A sleeping process', 'A running process'),
    Q('What is an orphan process?', 'A process whose parent has ended', 'A zombie', 'A running process', 'A daemon'),
    Q('What is IPC?', 'Inter-Process Communication', 'Internet Protocol Control', 'Internal Process Cache', 'Input Process Command'),
    Q('What is a pipe?', 'A way to connect process output to input', 'A file', 'A network cable', 'A process'),
    Q('What is shared memory?', 'Memory shared between processes', 'A type of cache', 'A file system', 'A device'),
    Q('What is preemptive scheduling?', 'OS can interrupt a process', 'Process runs to completion', 'No scheduling', 'Batch scheduling'),
    Q('What is a time slice?', 'The time a process runs in round-robin', 'A type of clock', 'A file size', 'A memory unit'),
]


def build_os(rng):
    return list(OS_CURATED)


# =====================================================================
# Data Structures & Algorithms
# =====================================================================

DSA_CURATED = [
    Q('Which data structure uses FIFO?', 'Queue', 'Stack', 'Tree', 'Graph'),
    Q('Which data structure uses LIFO?', 'Stack', 'Queue', 'Array', 'Heap'),
    Q('What is the time complexity of accessing an array by index?', 'O(1)', 'O(n)', 'O(log n)', 'O(n^2)'),
    Q('What is the time complexity of linear search?', 'O(n)', 'O(1)', 'O(log n)', 'O(n^2)'),
    Q('What is the time complexity of binary search?', 'O(log n)', 'O(n)', 'O(1)', 'O(n^2)'),
    Q('Which sorting algorithm has O(n log n) average time?', 'Merge sort', 'Bubble sort', 'Selection sort', 'Insertion sort'),
    Q('Which sorting algorithm has O(n^2) worst case?', 'Bubble sort', 'Merge sort', 'Heap sort', 'Quick sort best'),
    Q('Which data structure is a collection of key-value pairs?', 'Hash table', 'Stack', 'Queue', 'Array'),
    Q('What is the average lookup time of a hash table?', 'O(1)', 'O(n)', 'O(log n)', 'O(n^2)'),
    Q('What is a linked list made of?', 'Nodes with pointers', 'Arrays', 'Hash tables', 'Trees'),
    Q('What is the time complexity of inserting at the head of a linked list?', 'O(1)', 'O(n)', 'O(log n)', 'O(n^2)'),
    Q('What is a binary tree?', 'A tree where each node has at most two children', 'A tree with many children', 'An array', 'A queue'),
    Q('What is a binary search tree property?', 'Left child is smaller, right child is larger', 'All nodes are equal', 'Random order', 'Sorted like an array'),
    Q('What is the height of a balanced BST with n nodes?', 'O(log n)', 'O(n)', 'O(n^2)', 'O(1)'),
    Q('Which traversal visits left, root, right?', 'In-order', 'Pre-order', 'Post-order', 'Level-order'),
    Q('Which traversal visits root, left, right?', 'Pre-order', 'In-order', 'Post-order', 'Level-order'),
    Q('Which traversal visits left, right, root?', 'Post-order', 'Pre-order', 'In-order', 'Level-order'),
    Q('What is a heap?', 'A specialized tree-based structure', 'A linked list', 'An array', 'A stack'),
    Q('Which heap property is used in a max-heap?', 'Parent is greater than children', 'Parent is smaller than children', 'All equal', 'Random'),
    Q('What is a priority queue often implemented with?', 'Heap', 'Stack', 'Array', 'Linked list'),
    Q('What is a graph?', 'A set of vertices and edges', 'A list', 'A queue', 'A stack'),
    Q('Which algorithm finds the shortest path in a weighted graph?', "Dijkstra's algorithm", 'BFS', 'DFS', 'Merge sort'),
    Q('Which algorithm finds the shortest path in an unweighted graph?', 'BFS', "Dijkstra's algorithm", 'DFS', 'Binary search'),
    Q('What is the time complexity of DFS on a graph?', 'O(V + E)', 'O(V)', 'O(E)', 'O(V^2)'),
    Q('Which algorithm finds a minimum spanning tree?', "Prim's algorithm", 'Dijkstra', 'Binary search', 'Quick sort'),
    Q('What is dynamic programming?', 'Solving problems by breaking into subproblems', 'A type of sorting', 'A data structure', 'A graph'),
    Q('What is memoization?', 'Storing results of subproblems', 'A sorting method', 'A memory unit', 'A data structure'),
    Q('Which problem is solved by the knapsack algorithm?', 'Maximizing value within weight limit', 'Sorting items', 'Finding shortest path', 'Searching a tree'),
    Q('What is recursion?', 'A function calling itself', 'A loop', 'A data type', 'A sort'),
    Q('What is the base case in recursion?', 'The stopping condition', 'The first call', 'The return type', 'The function name'),
    Q('What is the space complexity of recursion with depth n?', 'O(n)', 'O(1)', 'O(n^2)', 'O(log n)'),
    Q('Which sort is stable and O(n log n) worst case?', 'Merge sort', 'Quick sort', 'Selection sort', 'Heap sort'),
    Q('Which sort is in-place and O(n log n) average?', 'Quick sort', 'Merge sort', 'Bubble sort', 'Counting sort'),
    Q('Which algorithm counts occurrences to sort?', 'Counting sort', 'Bubble sort', 'Merge sort', 'Selection sort'),
    Q('What is the time complexity of bubble sort?', 'O(n^2)', 'O(n)', 'O(log n)', 'O(n log n)'),
    Q('Which data structure supports O(1) push and pop?', 'Stack', 'Queue', 'Tree', 'Graph'),
    Q('Which data structure is used for level-order traversal?', 'Queue', 'Stack', 'Tree', 'Graph'),
    Q('Which data structure is used for DFS?', 'Stack', 'Queue', 'Heap', 'Hash table'),
    Q('Which data structure is used for BFS?', 'Queue', 'Stack', 'Heap', 'Array'),
    Q('What is a circular queue?', 'A queue that wraps around', 'A stack', 'A double-ended queue', 'An array'),
    Q('What is a deque?', 'A double-ended queue', 'A circular array', 'A stack', 'A priority queue'),
    Q('What is the worst-case time of searching in a hash table?', 'O(n)', 'O(1)', 'O(log n)', 'O(n log n)'),
    Q('What is collision in hashing?', 'Two keys hashing to same slot', 'A crash', 'A sort', 'A memory leak'),
    Q('What is chaining in hashing?', 'Using linked lists for collisions', 'A sorting method', 'A tree', 'A queue'),
    Q('What is a trie?', 'A tree for storing strings', 'A hash table', 'A queue', 'A stack'),
    Q('What is a suffix array used for?', 'String processing', 'Sorting numbers', 'Graph traversal', 'Memory management'),
    Q('What is the greedy algorithm?', 'Making locally optimal choices', 'Trying all options', 'A sort', 'A search'),
    Q('Which problem does the greedy method solve optimally?', 'Activity selection', '0/1 knapsack', 'TSP', 'Bin packing'),
    Q('What is divide and conquer?', 'Splitting a problem into subproblems', 'A sort only', 'A search only', 'A loop'),
    Q('What is the master theorem used for?', 'Analyzing divide-and-conquer recurrences', 'Sorting', 'Hashing', 'Graph coloring'),
    Q('What is amortized analysis?', 'Average cost over operations', 'Worst-case analysis', 'Best-case analysis', 'A type of sort'),
    Q('What is a doubly linked list?', 'A list with both next and prev pointers', 'A list with one pointer', 'An array', 'A hash table'),
    Q('What is the time to delete from a doubly linked list given the node?', 'O(1)', 'O(n)', 'O(log n)', 'O(n^2)'),
    Q('Which data structure is a balanced BST in the standard library?', 'Red-black tree', 'Array', 'Queue', 'Stack'),
    Q('What is an AVL tree?', 'A self-balancing BST', 'An array', 'A queue', 'A hash table'),
    Q('What is a B-tree?', 'A balanced multi-way tree for storage', 'A binary tree', 'An array', 'A graph'),
    Q('Which algorithm is used to sort nearly sorted data efficiently?', 'Insertion sort', 'Bubble sort', 'Merge sort', 'Quick sort'),
    Q('What is the time complexity of building a heap?', 'O(n)', 'O(n log n)', 'O(n^2)', 'O(log n)'),
    Q('What is the worst case of quick sort?', 'O(n^2)', 'O(n log n)', 'O(n)', 'O(log n)'),
]


def build_dsa(rng):
    return list(DSA_CURATED)


# =====================================================================
# Aptitude & Logical Reasoning
# =====================================================================

APT_CURATED = [
    Q('If 5 machines produce 5 widgets in 5 minutes, how long does 1 machine take for 1 widget?', '5 minutes', '1 minute', '25 minutes', '10 minutes'),
    Q('Which number is odd one out: 2, 4, 8, 10, 14?', '10', '4', '8', '14'),
    Q('Which number is odd one out: 3, 6, 9, 12, 15, 18, 20?', '20', '3', '12', '18'),
    Q('If all roses are flowers and some flowers fade, what follows?', 'Some roses may fade', 'All roses fade', 'No roses fade', 'All flowers are roses'),
    Q('What comes next: A, C, E, G, ?', 'I', 'H', 'J', 'F'),
    Q('What comes next: 1, 1, 2, 3, 5, 8, ?', '13', '11', '10', '21'),
    Q('A clock shows 3:15. What is the angle between the hands?', '7.5 degrees', '30 degrees', '15 degrees', '0 degrees'),
    Q('If you throw a dice twice, what is the probability of getting a 6 both times?', '1/36', '1/6', '1/12', '1/18'),
    Q('What is the next letter in the series: Z, X, V, T, R, ?', 'P', 'Q', 'S', 'N'),
    Q('A train 100m long crosses a pole in 10 seconds. What is its speed?', '10 m/s', '100 m/s', '1 m/s', '5 m/s'),
    Q('If John is twice as old as his son and the sum is 60, how old is the son?', '20', '30', '40', '15'),
    Q('Which word does not belong: Apple, Banana, Carrot, Grape?', 'Carrot', 'Apple', 'Banana', 'Grape'),
    Q('What is the next number: 2, 6, 18, 54, ?', '162', '108', '72', '81'),
    Q('If the day after tomorrow is Sunday, what day is today?', 'Friday', 'Saturday', 'Thursday', 'Monday'),
    Q('How many faces does a cube have?', '6', '8', '4', '12'),
    Q('How many edges does a cube have?', '12', '8', '6', '10'),
    Q('Which figure has 5 sides?', 'Pentagon', 'Hexagon', 'Quadrilateral', 'Triangle'),
    Q('If 8 men can build a wall in 6 days, how long will 12 men take?', '4 days', '6 days', '8 days', '9 days'),
    Q('The number of days in the month of February in a leap year is?', '29', '28', '30', '31'),
    Q('If A is taller than B and B is taller than C, who is the shortest?', 'C', 'A', 'B', 'Cannot determine'),
    Q('What is the sum of the first 10 natural numbers?', '55', '50', '45', '60'),
    Q('A bag has 4 red and 6 blue balls. Probability of picking red?', '0.4', '0.6', '0.5', '0.3'),
    Q('What is the next term: 1, 4, 9, 16, 25, ?', '36', '30', '35', '49'),
    Q('If Monday is the first day, what is the 100th day?', 'Tuesday', 'Monday', 'Wednesday', 'Sunday'),
    Q('Which is the largest: 0.5, 1/3, 0.25, 2/5?', '0.5', '1/3', '0.25', '2/5'),
    Q('A number increased by 20% becomes 120. What is the number?', '100', '96', '90', '110'),
    Q('What is 5% of 60?', '3', '6', '30', '5'),
    Q('The next number in the series 5, 10, 20, 40 is?', '80', '60', '50', '100'),
    Q('If today is Saturday, what day will it be in 10 days?', 'Tuesday', 'Monday', 'Sunday', 'Wednesday'),
    Q('How many corners does a triangle have?', '3', '4', '2', '5'),
    Q('Which number is prime: 11, 21, 27, 33?', '11', '21', '27', '33'),
    Q('If 3x = 27, what is x?', '9', '3', '24', '81'),
    Q('What is the value of 7 x 8 - 6?', '50', '58', '42', '56'),
    Q('A shirt costs $40 with 25% discount. What is the price?', '$30', '$35', '$25', '$10'),
    Q('Which number is odd one out: 121, 144, 169, 180?', '180', '121', '144', '169'),
    Q('How many minutes are in 3 hours?', '180', '120', '150', '300'),
    Q('What is 1/4 of 100?', '25', '20', '40', '75'),
    Q('If the price of an item doubles every year and costs $10 now, what will it cost in 3 years?', '$80', '$40', '$60', '$30'),
    Q('Which shape has 4 equal sides?', 'Square', 'Rectangle', 'Triangle', 'Circle'),
    Q('If it takes 3 painters 2 days to paint a house, how many days for 6 painters?', '1 day', '2 days', '3 days', '4 days'),
]


def build_aptitude(rng):
    return (list(APT_CURATED) + percent_pool(rng, 25) + arithmetic_pool(rng, 40)
            + sequence_pool(rng, 25) + ratio_pool(rng, 20) + age_pool(rng, 15))


# =====================================================================
# Linux & DevOps
# =====================================================================

LINUX_CURATED = [
    Q('Which command lists files in Linux?', 'ls', 'dir', 'list', 'show'),
    Q('Which command changes directories in Linux?', 'cd', 'chdir', 'move', 'go'),
    Q('Which command copies files in Linux?', 'cp', 'copy', 'mv', 'dd'),
    Q('Which command moves files in Linux?', 'mv', 'move', 'cp', 'rm'),
    Q('Which command removes files in Linux?', 'rm', 'del', 'delete', 'remove'),
    Q('Which command shows the current directory?', 'pwd', 'ls', 'cd', 'whoami'),
    Q('Which command shows the manual of a command?', 'man', 'help', 'info', 'doc'),
    Q('Which command shows running processes?', 'ps', 'ls', 'top -v', 'jobs'),
    Q('Which command shows disk usage?', 'df', 'du only', 'free', 'mount'),
    Q('Which command shows memory usage?', 'free', 'mem', 'df', 'top -m'),
    Q('Which command displays system information?', 'uname', 'sysinfo', 'system', 'host'),
    Q('Which command shows the user identity?', 'whoami', 'user', 'id -u', 'me'),
    Q('Which command searches text in files?', 'grep', 'find', 'sed', 'awk'),
    Q('Which command finds files?', 'find', 'grep', 'locate -f', 'search'),
    Q('Which command prints text to the terminal?', 'echo', 'print', 'printf -v', 'cat -e'),
    Q('Which command reads a file content?', 'cat', 'read', 'open', 'view'),
    Q('Which command shows the first 10 lines of a file?', 'head', 'tail', 'top', 'less'),
    Q('Which command shows the last 10 lines of a file?', 'tail', 'head', 'bottom', 'less'),
    Q('Which command views a file page by page?', 'less', 'cat', 'more -f', 'grep'),
    Q('Which command compresses files with gzip?', 'gzip', 'zip', 'tar -z', 'compress'),
    Q('Which command creates an archive?', 'tar', 'zip', 'gzip', 'ar'),
    Q('Which command changes file permissions?', 'chmod', 'chown', 'chgrp', 'chroot'),
    Q('Which command changes file owner?', 'chown', 'chmod', 'chgrp', 'usermod'),
    Q('Which command is used to become superuser?', 'sudo', 'su only', 'root', 'admin'),
    Q('Which command installs packages on Debian/Ubuntu?', 'apt', 'yum', 'dnf', 'pacman'),
    Q('Which command installs packages on RHEL/Fedora?', 'dnf', 'apt', 'apt-get', 'pacman'),
    Q('Which command is used to manage services on modern Linux?', 'systemctl', 'service only', 'init', 'rc'),
    Q('Which directory contains user binaries in Linux?', '/usr/bin', '/etc', '/var', '/tmp'),
    Q('Which directory contains system configuration?', '/etc', '/usr', '/var', '/home'),
    Q('Which directory contains temporary files?', '/tmp', '/etc', '/var', '/opt'),
    Q('Which directory contains user home directories?', '/home', '/etc', '/root only', '/usr'),
    Q('What is the default shell in most Linux distros?', 'Bash', 'Zsh', 'Fish', 'Csh'),
    Q('Which command prints environment variables?', 'env', 'envp', 'getenv', 'vars'),
    Q('Which command shows network interfaces?', 'ip', 'net', 'ifconfig -a', 'route'),
    Q('Which command tests network connectivity?', 'ping', 'trace', 'netstat', 'nslookup'),
    Q('Which command shows open ports?', 'ss', 'ps', 'top', 'ls'),
    Q('Which command shows IP routes?', 'ip route', 'route -a', 'net route', 'traceroute'),
    Q('Which command resolves a domain name?', 'dig', 'ping -d', 'hostname', 'ifconfig'),
    Q('Which command downloads files?', 'wget', 'fetch', 'download', 'pull'),
    Q('Which command shows CPU usage interactively?', 'top', 'ps', 'free', 'df'),
    Q('Which command kills a process by name?', 'killall', 'kill', 'stop', 'end'),
    Q('Which command kills a process by PID?', 'kill', 'killall', 'stop', 'rm'),
    Q('What is a symlink?', 'A shortcut to another file', 'A hard link', 'A copy', 'A directory'),
    Q('Which command creates a symbolic link?', 'ln -s', 'link -s', 'symlink', 'mkdir'),
    Q('Which command creates a directory?', 'mkdir', 'md', 'createdir', 'mk'),
    Q('Which command removes a directory?', 'rmdir', 'rm', 'del', 'rdir'),
    Q('Which file contains user accounts?', '/etc/passwd', '/etc/shadow only', '/etc/users', '/home'),
    Q('Which file contains encrypted passwords?', '/etc/shadow', '/etc/passwd', '/etc/users', '/etc/security'),
    Q('What is Docker?', 'A containerization platform', 'A database', 'A web server', 'An OS'),
    Q('What is a Docker image?', 'A template for containers', 'A running container', 'A volume', 'A network'),
    Q('What is a Docker container?', 'A running instance of an image', 'A template', 'A volume', 'An image'),
    Q('Which file defines a Docker image?', 'Dockerfile', 'docker.yml', 'container.json', 'Docker.conf'),
    Q('Which command builds a Docker image?', 'docker build', 'docker create', 'docker make', 'docker run'),
    Q('Which command runs a Docker container?', 'docker run', 'docker build', 'docker start', 'docker exec'),
    Q('What is Kubernetes?', 'A container orchestration platform', 'A container runtime', 'A database', 'A CI tool'),
    Q('What is a Kubernetes pod?', 'A group of containers', 'A node', 'A service', 'A volume'),
    Q('What is Helm in Kubernetes?', 'A package manager', 'A runtime', 'A database', 'A network'),
    Q('What is CI/CD?', 'Continuous Integration / Continuous Deployment', 'Code Injection and Deletion', 'Computer Interface Control', 'Central Input Device'),
    Q('Which tool is used for CI/CD pipelines?', 'Jenkins', 'Docker only', 'Nginx', 'MySQL'),
    Q('What is Terraform used for?', 'Infrastructure as code', 'Containerization', 'CI/CD', 'Monitoring'),
    Q('What is Ansible?', 'A configuration management tool', 'A database', 'A web server', 'A container'),
    Q('What is Nginx commonly used for?', 'A web server and reverse proxy', 'A database', 'A CI tool', 'An OS'),
    Q('What is Grafana used for?', 'Monitoring dashboards', 'Containerization', 'CI/CD', 'Database storage'),
    Q('What is Prometheus?', 'A monitoring and alerting toolkit', 'A database', 'A web server', 'A package manager'),
    Q('What is Git used for?', 'Version control', 'Containerization', 'Monitoring', 'Deployment only'),
    Q('Which command stages files in Git?', 'git add', 'git commit', 'git push', 'git status'),
    Q('Which command commits changes in Git?', 'git commit', 'git add', 'git push', 'git save'),
    Q('Which command pushes commits to remote?', 'git push', 'git pull', 'git commit', 'git clone'),
    Q('Which command pulls changes from remote?', 'git pull', 'git push', 'git fetch only', 'git sync'),
    Q('Which command clones a repository?', 'git clone', 'git copy', 'git pull', 'git init'),
    Q('Which command shows the Git status?', 'git status', 'git list', 'git state', 'git check'),
    Q('What is a Linux distribution?', 'An OS built on the Linux kernel', 'A version of Windows', 'A type of CPU', 'A shell'),
    Q('Which command shows the Linux kernel version?', 'uname -r', 'kernel -v', 'version', 'os -r'),
    Q('Which command shows all environment variables?', 'env', 'vars', 'printenv -v', 'set -e'),
    Q('What is SSH used for?', 'Secure remote access', 'File compression', 'Web serving', 'DNS'),
    Q('Which command copies files over SSH?', 'scp', 'cp -ssh', 'ssh-copy', 'ftp'),
    Q('Which command synchronizes files?', 'rsync', 'sync', 'cp', 'mv'),
    Q('What is a crontab?', 'A schedule of recurring jobs', 'A log file', 'A shell', 'A package'),
    Q('Which command edits the crontab?', 'crontab -e', 'cron -e', 'edit cron', 'crontab edit'),
    Q('What is the default port for SSH?', '22', '21', '80', '443'),
    Q('Which command shows open network connections?', 'netstat', 'ls', 'ps', 'df'),
    Q('What is a load balancer in DevOps?', 'A tool that distributes traffic', 'A database', 'A compiler', 'A log'),
    Q('What is observability?', 'Monitoring, logging and tracing', 'A type of container', 'A database', 'A CI tool'),
    Q('Which tool manages multiple Docker containers?', 'Docker Compose', 'Dockerfile', 'Nginx', 'Git'),
    Q('What is the file for Docker Compose?', 'docker-compose.yml', 'Dockerfile', 'compose.json', 'docker.yml'),
]


def build_linux(rng):
    return list(LINUX_CURATED)


# =====================================================================
# Category registry
# =====================================================================

def _mk(name, slug, emoji, g1, g2, desc, count, fragments, build):
    return {
        'name': name, 'slug': slug, 'emoji': emoji,
        'gradient_from': g1, 'gradient_to': g2, 'description': desc,
        'count': count, 'title_fragments': fragments, 'build': build,
    }


CATEGORIES = [
    _mk('General Knowledge', 'general-knowledge', '🧠', '#6366f1', '#a855f7',
        'Facts about the world around us.', 70,
        ['World Capitals', 'Famous Scientists', 'Nobel Prize Winners', 'Wonders of the World',
         'Great Inventions', 'Flags of the World', 'World Currencies', 'National Symbols',
         'Human Body Facts', 'Solar System', 'World Leaders', 'Famous Books',
         'Space Exploration', 'World Records', 'Cultural Festivals', 'Everyday Science',
         'Geography Basics', 'General Trivia', 'Famous People', 'History of Science',
         'Amazing Animals', 'Global Facts', 'Planet Earth', 'Discovery Quiz',
         'World Knowledge', 'Popular Culture', 'Interesting Facts', 'Did You Know'],
        build_gk),
    _mk('Computer Science', 'computer-science', '💻', '#3b82f6', '#8b5cf6',
        'Core concepts of computing.', 70,
        ['Operating System Basics', 'Computer Architecture', 'Software Engineering Principles',
         'Compiler Design', 'Theory of Computation', 'Binary and Number Systems', 'Boolean Logic',
         'Computer Hardware', 'Memory Management', 'Programming Paradigms', 'Data Representation',
         'Computer Networks Basics', 'Database Fundamentals', 'Cloud Computing', 'Big Data',
         'Software Testing', 'Computer History', 'System Design', 'File Systems', 'Computer Graphics',
         'Web Technologies', 'Information Systems', 'Computational Thinking', 'IT Fundamentals',
         'Computer Security Basics', 'Software Engineering', 'Digital Logic', 'Computer Science'],
        build_cs),
    _mk('Programming', 'programming', '👨‍💻', '#f59e0b', '#ef4444',
        'Hands-on programming and languages.', 60,
        ['Python Basics', 'Java OOP Concepts', 'C++ STL Challenge', 'JavaScript ES6 Fundamentals',
         'Django Models', 'REST API Essentials', 'Python Data Structures', 'Java Collections',
         'C++ Pointers', 'JavaScript Arrays', 'SQL Queries', 'Flask Web Development',
         'Python Functions', 'Java Threads', 'C++ Templates', 'JavaScript Promises',
         'HTML CSS Basics', 'Object Oriented Programming', 'Functional Programming', 'Debugging Skills',
         'Code Output Challenge', 'Algorithm Implementation', 'Version Control with Git', 'Code Refactoring',
         'Database Programming', 'Web Frameworks', 'Clean Code', 'Programming Logic',
         'Syntax Challenge', 'Language Features'],
        build_prog),
    _mk('Mathematics', 'mathematics', '📐', '#10b981', '#22d3ee',
        'Numbers, formulas and problem solving.', 50,
        ['Arithmetic Basics', 'Algebra Essentials', 'Geometry Fundamentals', 'Percentage Problems',
         'Number Theory', 'Fractions and Decimals', 'Mental Math Challenge', 'Quadratic Equations',
         'Trigonometry Basics', 'Calculus Concepts', 'Probability Essentials', 'Statistics Basics',
         'Ratios and Proportions', 'Powers and Roots', 'Sequences and Series', 'Math Puzzles',
         'Logic and Reasoning', 'Measurements', 'Vedic Math', 'Speed Math',
         'Mathematical Reasoning', 'Everyday Math', 'Math Challenge', 'Quick Calculations',
         'Mathematical Constants', 'Prime Numbers', 'Geometry Challenge', 'Math Fundamentals'],
        build_math),
    _mk('Science', 'science', '🔬', '#22d3ee', '#6366f1',
        'Physics, chemistry and biology.', 45,
        ['Physics Fundamentals', 'Chemistry Essentials', 'Biology Basics', 'Human Anatomy',
         'Periodic Table', 'Chemical Reactions', 'Electricity and Magnetism', 'Energy and Motion',
         'Cells and Genetics', 'Planet Science', 'Space Science', 'States of Matter',
         'Acids and Bases', 'Human Physiology', 'Environmental Science', 'Materials Science',
         'Scientific Discoveries', 'Units and Measurements', 'Forces and Motion', 'Heat and Temperature',
         'Sound and Light', 'Life Processes', 'Earth Science', 'Water Science',
         'Science Trivia', 'Atomic Structure', 'The Human Body', 'World of Science',
         'Lab Knowledge', 'Scientific Method'],
        build_science),
    _mk('History', 'world-history', '🏛️', '#f59e0b', '#ef4444',
        'Civilizations and turning points.', 40,
        ['Ancient Civilizations', 'World War II', 'Mughal Empire', 'French Revolution',
         'Roman Empire', 'Ancient Egypt', 'World War I', 'Medieval History',
         'Renaissance', 'Famous Empires', 'Explorers and Voyages', 'Industrial Revolution',
         'Famous Leaders', 'Cold War Era', 'Ancient Greece', 'Byzantine Empire',
         'Mongol Empire', 'Ottoman Empire', 'British Empire', 'Historic Battles',
         'World History', 'Modern History', 'Historic Documents', 'Age of Discovery',
         'Famous Rulers', 'Time of Revolution', 'Classical Antiquity', 'Historical Figures'],
        build_history),
    _mk('Geography', 'geography', '🌍', '#10b981', '#22d3ee',
        'Countries, rivers, mountains and oceans.', 35,
        ['World Capitals', 'Major Rivers', 'Mountain Ranges', 'Countries and Flags',
         'Oceans and Seas', 'Deserts of the World', 'Continents', 'World Geography',
         'Rivers of the World', 'Highest Peaks', 'Lakes and Basins', 'Island Nations',
         'Geographical Facts', 'Landmarks', 'Climate and Weather', 'Population Geography',
         'World Maps', 'Physical Geography', 'National Parks', 'Terrains',
         'Global Geography', 'Geography Trivia', 'The Equator', 'Time Zones',
         'Geographic Wonders', 'Natural Features', 'Geography Challenge'],
        build_geography),
    _mk('English', 'english', '📚', '#f472b6', '#a855f7',
        'Vocabulary, grammar and idioms.', 30,
        ['Synonym Challenge', 'Antonym Practice', 'Spelling Bee', 'Idioms and Phrases',
         'Grammar Essentials', 'Vocabulary Builder', 'Sentence Correction', 'Word Meanings',
         'English Grammar', 'Phrasal Verbs', 'Prefixes and Suffixes', 'Reading Comprehension Basics',
         'Parts of Speech', 'Tenses Practice', 'Common Mistakes', 'Word Usage',
         'English Language', 'Formal English', 'Improve Your English', 'Language Skills',
         'Word Power', 'English Fundamentals', 'Phrase Mastery', 'Grammar Rules',
         'Vocabulary Test', 'English Quiz'],
        build_english),
    _mk('Current Affairs', 'current-affairs', '📰', '#f87171', '#fbbf24',
        'Recent events and global updates.', 25,
        ['Global Events', 'International Organizations', 'World Records', 'Business News',
         'Technology News', 'Sports Update', 'Space Missions', 'Environmental News',
         'Economics Update', 'Politics Basics', 'Awards and Honours', 'Summits and Conferences',
         'Science News', 'New Developments', 'World Affairs', 'Current Events',
         'Recent History', 'Milestones', 'Global Updates', 'News Quiz',
         'Around the World', 'Trending Topics', 'Stay Informed'],
        build_current_affairs),
    _mk('Sports', 'sports', '⚽', '#22c55e', '#84cc16',
        'Games, records and champions.', 20,
        ['Football Quiz', 'Cricket Challenge', 'Olympics Trivia', 'Tennis Fundamentals',
         'Basketball Basics', 'Formula 1 Racing', 'Athletics Records', 'Rugby Rules',
         'Baseball Essentials', 'Sports Records', 'Winter Sports', 'World Champions',
         'Sports History', 'Famous Athletes', 'Sports Trivia', 'The Beautiful Game',
         'Champions League', 'Sports Legends', 'Game Rules', 'Grand Slams'],
        build_sports),
    _mk('Movies & TV', 'movies-tv', '🎬', '#a855f7', '#f472b6',
        'Films, series and cinema trivia.', 15,
        ['Classic Movies', 'Hollywood Trivia', 'TV Series Quiz', 'Superhero Films',
         'Movie Quotes', 'Famous Directors', 'Oscar Winners', 'Animated Films',
         'Movie Franchises', 'Actors and Roles', 'Film History', 'Blockbuster Quiz',
         'Cinema Classics', 'TV Shows', 'Movie Trivia'],
        build_movies),
    _mk('Music', 'music', '🎵', '#f472b6', '#f59e0b',
        'Instruments, artists and theory.', 10,
        ['Music Theory Basics', 'Famous Artists', 'Classical Composers', 'Instruments Quiz',
         'Rock Legends', 'Jazz Essentials', 'Pop Music Trivia', 'Music History',
         'Vocal Ranges', 'Music Genres'],
        build_music),
    _mk('Business & Economics', 'business-economics', '📈', '#f59e0b', '#84cc16',
        'Markets, money and management.', 10,
        ['Economics Basics', 'Stock Market Fundamentals', 'Business Terms', 'Famous Entrepreneurs',
         'Company Quiz', 'Financial Literacy', 'Money Management', 'Market Analysis',
         'Trading Basics', 'Business Strategy'],
        build_business),
    _mk('Artificial Intelligence', 'ai', '🤖', '#8b5cf6', '#22d3ee',
        'Machine learning and intelligent systems.', 10,
        ['Machine Learning Basics', 'Deep Learning Fundamentals', 'Neural Networks',
         'Natural Language Processing', 'Computer Vision', 'AI Concepts', 'ML Algorithms',
         'AI Applications', 'Data Science Basics', 'AI Ethics'],
        build_ai),
    _mk('Cybersecurity', 'cybersecurity', '🛡️', '#ef4444', '#f97316',
        'Protecting systems and data.', 10,
        ['Security Fundamentals', 'Network Security', 'Ethical Hacking Basics', 'Cryptography Essentials',
         'Malware Awareness', 'Password Security', 'Web Security', 'Security Best Practices',
         'Cyber Threats', 'Information Security'],
        build_cyber),
    _mk('Networking', 'networking', '🌐', '#22d3ee', '#3b82f6',
        'Protocols, devices and the internet.', 10,
        ['Network Basics', 'OSI Model', 'TCP IP Fundamentals', 'Routing and Switching',
         'Network Protocols', 'Wireless Networking', 'Network Security', 'IP Addressing',
         'Network Devices', 'Internet Fundamentals'],
        build_networking),
    _mk('Database Systems', 'database-systems', '🗄️', '#10b981', '#3b82f6',
        'SQL, design and data management.', 10,
        ['SQL Essentials', 'Database Design', 'Normalization Basics', 'Transactions and ACID',
         'NoSQL Fundamentals', 'Query Optimization', 'Database Concepts', 'Data Modeling',
         'Indexing Basics', 'Relational Databases'],
        build_database),
    _mk('Web Development', 'web-development', '🖥️', '#6366f1', '#22d3ee',
        'HTML, CSS, JavaScript and the web.', 10,
        ['HTML Fundamentals', 'CSS Styling', 'JavaScript Basics', 'Frontend Development',
         'Backend Basics', 'HTTP Essentials', 'Web Design', 'Responsive Design',
         'Web Security Basics', 'Web APIs'],
        build_web),
    _mk('Operating Systems', 'operating-systems', '⚙️', '#64748b', '#0ea5e9',
        'Processes, memory and filesystems.', 10,
        ['OS Fundamentals', 'Process Management', 'Memory Management', 'Linux Basics',
         'File Systems', 'Scheduling Algorithms', 'Concurrency Basics', 'OS Architecture',
         'Deadlocks', 'System Administration'],
        build_os),
    _mk('Data Structures & Algorithms', 'dsa', '🧮', '#f59e0b', '#ef4444',
        'Efficient problem solving.', 10,
        ['Data Structures Basics', 'Sorting Algorithms', 'Searching Algorithms', 'Graph Theory',
         'Trees and Heaps', 'Complexity Analysis', 'Hashing Fundamentals', 'Dynamic Programming',
         'Recursion Practice', 'Algorithm Design'],
        build_dsa),
    _mk('Aptitude & Logical Reasoning', 'aptitude', '🧩', '#f97316', '#fbbf24',
        'Quantitative and logical thinking.', 10,
        ['Quantitative Aptitude', 'Logical Reasoning', 'Number Series', 'Puzzle Solving',
         'Percentage and Ratio', 'Speed and Time', 'Analogy Practice', 'Critical Thinking',
         'Mental Ability', 'Reasoning Skills'],
        build_aptitude),
    _mk('Linux & DevOps', 'linux-devops', '🐧', '#0ea5e9', '#22c55e',
        'Systems, shells and deployment.', 10,
        ['Linux Commands', 'Shell Scripting', 'Docker Basics', 'Kubernetes Fundamentals',
         'CI CD Pipelines', 'Infrastructure as Code', 'System Administration', 'DevOps Tools',
         'Version Control', 'Cloud Deployment'],
        build_linux),
]


