from django.core.management.base import BaseCommand
from django.db import transaction

from quizzes.models import Category, Choice, Question, Quiz

QUIZ_DATA = [
    {
        'category': ('Tech & Science', 'tech', '🚀', '#6366f1', '#a855f7',
                     'Everything about programming, space and the world around us.'),
        'quizzes': [
            {
                'title': 'General Knowledge: Computer Science',
                'slug': 'computer-science-basics',
                'description': 'Test your fundamentals of programming, data structures and how computers really work.',
                'difficulty': 'easy',
                'duration_minutes': 6,
                'questions': [
                    {
                        'text': 'What does CPU stand for?',
                        'choices': [
                            ('Central Processing Unit', True),
                            ('Computer Personal Unit', False),
                            ('Central Program Utility', False),
                            ('Control Processing Unit', False),
                        ],
                    },
                    {
                        'text': 'Which data structure uses the FIFO (First In, First Out) principle?',
                        'choices': [
                            ('Stack', False),
                            ('Queue', True),
                            ('Array', False),
                            ('Linked List', False),
                        ],
                    },
                    {
                        'text': 'In binary, the decimal number 10 is represented as:',
                        'choices': [
                            ('1010', True),
                            ('1100', False),
                            ('1001', False),
                            ('1110', False),
                        ],
                    },
                    {
                        'text': 'Which language is primarily used for styling web pages?',
                        'choices': [
                            ('HTML', False),
                            ('Python', False),
                            ('CSS', True),
                            ('Java', False),
                        ],
                    },
                    {
                        'text': 'What is the time complexity of binary search on a sorted array?',
                        'choices': [
                            ('O(n)', False),
                            ('O(n log n)', False),
                            ('O(log n)', True),
                            ('O(1)', False),
                        ],
                    },
                ],
            },
            {
                'title': 'Space Exploration Trivia',
                'slug': 'space-exploration',
                'description': 'From the Moon landing to Mars rovers — how well do you know our journey to the stars?',
                'difficulty': 'medium',
                'duration_minutes': 5,
                'questions': [
                    {
                        'text': 'In which year did Apollo 11 land humans on the Moon?',
                        'choices': [
                            ('1967', False),
                            ('1969', True),
                            ('1971', False),
                            ('1965', False),
                        ],
                    },
                    {
                        'text': 'Which planet is known as the Red Planet?',
                        'choices': [
                            ('Venus', False),
                            ('Jupiter', False),
                            ('Mars', True),
                            ('Mercury', False),
                        ],
                    },
                    {
                        'text': 'What is the name of the galaxy we live in?',
                        'choices': [
                            ('Andromeda', False),
                            ('Milky Way', True),
                            ('Sombrero', False),
                            ('Whirlpool', False),
                        ],
                    },
                    {
                        'text': 'Who was the first human to travel into space?',
                        'choices': [
                            ('Neil Armstrong', False),
                            ('Buzz Aldrin', False),
                            ('Yuri Gagarin', True),
                            ('Alan Shepard', False),
                        ],
                    },
                    {
                        'text': 'The Hubble Space Telescope was launched by which agency?',
                        'choices': [
                            ('ESA', False),
                            ('Roscosmos', False),
                            ('NASA', True),
                            ('JAXA', False),
                        ],
                    },
                ],
            },
            {
                'title': 'The World Wide Web',
                'slug': 'world-wide-web',
                'description': 'Protocols, pioneers and the pipes that power the internet you use every day.',
                'difficulty': 'hard',
                'duration_minutes': 5,
                'questions': [
                    {
                        'text': 'Who invented the World Wide Web?',
                        'choices': [
                            ('Tim Berners-Lee', True),
                            ('Vint Cerf', False),
                            ('Bill Gates', False),
                            ('Larry Page', False),
                        ],
                    },
                    {
                        'text': 'Which protocol provides secure communication over a computer network?',
                        'choices': [
                            ('FTP', False),
                            ('HTTP', False),
                            ('TLS', True),
                            ('SMTP', False),
                        ],
                    },
                    {
                        'text': 'What does the "404" status code mean?',
                        'choices': [
                            ('Server Error', False),
                            ('Not Found', True),
                            ('Unauthorized', False),
                            ('Redirect', False),
                        ],
                    },
                    {
                        'text': 'Which port is the default for HTTPS traffic?',
                        'choices': [
                            ('80', False),
                            ('8080', False),
                            ('443', True),
                            ('25', False),
                        ],
                    },
                    {
                        'text': 'DNS primarily translates domain names into:',
                        'choices': [
                            ('MAC addresses', False),
                            ('IP addresses', True),
                            ('Port numbers', False),
                            ('SSL certificates', False),
                        ],
                    },
                ],
            },
        ],
    },
    {
        'category': ('History & Culture', 'history', '🏛️', '#f59e0b', '#ef4444',
                     'Timeless stories, famous figures and the events that shaped our world.'),
        'quizzes': [
            {
                'title': 'Ancient Civilizations',
                'slug': 'ancient-civilizations',
                'description': 'Pyramids, emperors and engineering feats from the world of antiquity.',
                'difficulty': 'medium',
                'duration_minutes': 6,
                'questions': [
                    {
                        'text': 'The Great Pyramid of Giza was built for which pharaoh?',
                        'choices': [
                            ('Tutankhamun', False),
                            ('Ramses II', False),
                            ('Khufu', True),
                            ('Cleopatra', False),
                        ],
                    },
                    {
                        'text': 'Which ancient civilization built Machu Picchu?',
                        'choices': [
                            ('Aztec', False),
                            ('Maya', False),
                            ('Inca', True),
                            ('Olmec', False),
                        ],
                    },
                    {
                        'text': 'The Roman Colosseum was primarily used for:',
                        'choices': [
                            ('Religious ceremonies', False),
                            ('Gladiatorial contests', True),
                            ('Government meetings', False),
                            ('Public libraries', False),
                        ],
                    },
                    {
                        'text': 'Which empire built the Great Wall that is best known today?',
                        'choices': [
                            ('Mongol Empire', False),
                            ('Ming Dynasty', True),
                            ('Han Dynasty', False),
                            ('Qin Dynasty', False),
                        ],
                    },
                    {
                        'text': 'Socrates, Plato and Aristotle were philosophers from:',
                        'choices': [
                            ('Rome', False),
                            ('Greece', True),
                            ('Egypt', False),
                            ('Persia', False),
                        ],
                    },
                ],
            },
            {
                'title': 'World Landmarks',
                'slug': 'world-landmarks',
                'description': 'Identify the icons and the stories behind the world\'s most famous structures.',
                'difficulty': 'easy',
                'duration_minutes': 4,
                'questions': [
                    {
                        'text': 'The Eiffel Tower is located in which city?',
                        'choices': [
                            ('London', False),
                            ('Paris', True),
                            ('Rome', False),
                            ('Berlin', False),
                        ],
                    },
                    {
                        'text': 'The Statue of Liberty was a gift from which country?',
                        'choices': [
                            ('France', True),
                            ('Spain', False),
                            ('United Kingdom', False),
                            ('Italy', False),
                        ],
                    },
                    {
                        'text': 'Santorini\'s famous white buildings belong to which country?',
                        'choices': [
                            ('Italy', False),
                            ('Greece', True),
                            ('Turkey', False),
                            ('Spain', False),
                        ],
                    },
                    {
                        'text': 'Which landmark is located in Agra, India?',
                        'choices': [
                            ('Gateway of India', False),
                            ('Red Fort', False),
                            ('Taj Mahal', True),
                            ('Qutub Minar', False),
                        ],
                    },
                ],
            },
        ],
    },
    {
        'category': ('Nature & Geography', 'nature', '🌍', '#10b981', '#22d3ee',
                     'Oceans, mountains, creatures and the natural wonders of planet Earth.'),
        'quizzes': [
            {
                'title': 'Geography Challenge',
                'slug': 'geography-challenge',
                'description': 'Rivers, capitals, deserts and oceans — can you ace the ultimate geography test?',
                'difficulty': 'medium',
                'duration_minutes': 5,
                'questions': [
                    {
                        'text': 'What is the longest river in the world?',
                        'choices': [
                            ('Amazon', False),
                            ('Nile', True),
                            ('Yangtze', False),
                            ('Mississippi', False),
                        ],
                    },
                    {
                        'text': 'Which country has the most natural lakes?',
                        'choices': [
                            ('Canada', True),
                            ('USA', False),
                            ('Russia', False),
                            ('Brazil', False),
                        ],
                    },
                    {
                        'text': 'Mount Everest is part of which mountain range?',
                        'choices': [
                            ('Andes', False),
                            ('Rockies', False),
                            ('Himalayas', True),
                            ('Alps', False),
                        ],
                    },
                    {
                        'text': 'The Sahara Desert is located on which continent?',
                        'choices': [
                            ('Asia', False),
                            ('Australia', False),
                            ('Africa', True),
                            ('South America', False),
                        ],
                    },
                    {
                        'text': 'Which is the smallest ocean in the world?',
                        'choices': [
                            ('Indian Ocean', False),
                            ('Atlantic Ocean', False),
                            ('Arctic Ocean', True),
                            ('Pacific Ocean', False),
                        ],
                    },
                ],
            },
            {
                'title': 'Wildlife Wonders',
                'slug': 'wildlife-wonders',
                'description': 'From the fastest to the rarest — test your knowledge of the animal kingdom.',
                'difficulty': 'easy',
                'duration_minutes': 4,
                'questions': [
                    {
                        'text': 'What is the fastest land animal?',
                        'choices': [
                            ('Lion', False),
                            ('Cheetah', True),
                            ('Peregrine Falcon', False),
                            ('Greyhound', False),
                        ],
                    },
                    {
                        'text': 'Which animal is known as the king of the jungle?',
                        'choices': [
                            ('Tiger', False),
                            ('Lion', True),
                            ('Elephant', False),
                            ('Leopard', False),
                        ],
                    },
                    {
                        'text': 'What is the largest mammal in the world?',
                        'choices': [
                            ('African Elephant', False),
                            ('Blue Whale', True),
                            ('Giraffe', False),
                            ('Polar Bear', False),
                        ],
                    },
                    {
                        'text': 'Which bird cannot fly?',
                        'choices': [
                            ('Penguin', True),
                            ('Sparrow', False),
                            ('Eagle', False),
                            ('Hawk', False),
                        ],
                    },
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed the database with demo categories and quizzes.'

    @transaction.atomic
    def handle(self, *args, **options):
        for cat_data in QUIZ_DATA:
            name, slug, emoji, g_from, g_to, desc = cat_data['category']
            category, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'emoji': emoji,
                    'gradient_from': g_from,
                    'gradient_to': g_to,
                    'description': desc,
                },
            )
            for quiz_data in cat_data['quizzes']:
                quiz, created = Quiz.objects.get_or_create(
                    slug=quiz_data['slug'],
                    defaults={
                        'title': quiz_data['title'],
                        'description': quiz_data['description'],
                        'difficulty': quiz_data['difficulty'],
                        'duration_minutes': quiz_data['duration_minutes'],
                        'category': category,
                    },
                )
                if not created:
                    continue
                for i, q_data in enumerate(quiz_data['questions']):
                    question = Question.objects.create(
                        quiz=quiz, text=q_data['text'], order=i
                    )
                    for j, (text, is_correct) in enumerate(q_data['choices']):
                        Choice.objects.create(
                            question=question,
                            text=text,
                            is_correct=is_correct,
                            order=j,
                        )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {Category.objects.count()} categories and {Quiz.objects.count()} quizzes.'
        ))
