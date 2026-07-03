"""
Management command: python manage.py populate_demo
Creates demo data for the Rustili platform.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate demo data for Rustili platform'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')

        self._create_users()
        self._create_categories()
        self._create_courses()
        self._create_vocabulary()
        self._create_grammar()
        self._create_achievements()
        self._create_quizzes()
        self._create_leaderboard()

        self.stdout.write(self.style.SUCCESS('✅ Demo data created successfully!'))

    def _create_users(self):
        from apps.accounts.models import User

        # Admin
        if not User.objects.filter(email='admin@rustili.uz').exists():
            admin = User.objects.create_superuser(
                username='admin', email='admin@rustili.uz',
                password='admin123', first_name='Admin', last_name='Rustili',
                role='admin', email_verified=True
            )
            self.stdout.write(f'  Created admin: admin@rustili.uz / admin123')

        # Teacher
        if not User.objects.filter(email='teacher@rustili.uz').exists():
            teacher = User.objects.create_user(
                username='teacher1', email='teacher@rustili.uz',
                password='teacher123', first_name='Sarah', last_name='Johnson',
                role='teacher', email_verified=True, is_active=True,
                bio='Experienced English teacher with 10+ years in education.'
            )
            self.stdout.write(f'  Created teacher: teacher@rustili.uz / teacher123')

        # Students
        students_data = [
            ('ali@example.com', 'ali_student', 'Ali', 'Karimov', 850),
            ('zulfiya@example.com', 'zulfiya1', 'Zulfiya', 'Rahimova', 650),
            ('bobur@example.com', 'bobur1', 'Bobur', 'Toshmatov', 1200),
            ('nilufar@example.com', 'nilufar1', 'Nilufar', 'Yusupova', 450),
            ('sherzod@example.com', 'sherzod1', 'Sherzod', 'Mirzayev', 2000),
        ]

        for email, username, first, last, xp in students_data:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    username=username, email=email, password='demo123',
                    first_name=first, last_name=last,
                    role='student', email_verified=True, is_active=True
                )
                try:
                    from apps.gamification.models import UserProgress
                    prog, _ = UserProgress.objects.get_or_create(user=user)
                    prog.xp = xp
                    from apps.core.utils import calculate_level
                    prog.level = calculate_level(xp)
                    prog.streak_days = xp // 100
                    prog.save()
                except Exception as e:
                    pass

        self.stdout.write(f'  Created demo students')

    def _create_categories(self):
        from apps.courses.models import Category
        cats = [
            ('General English', 'general-english', '📚', '#6366f1'),
            ('Business English', 'business-english', '💼', '#8b5cf6'),
            ('Travel English', 'travel-english', '✈️', '#3b82f6'),
            ('Academic English', 'academic-english', '🎓', '#10b981'),
            ('Daily Conversation', 'daily-conversation', '💬', '#f59e0b'),
        ]
        for name, slug, icon, color in cats:
            Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'color': color}
            )
        self.stdout.write(f'  Created {len(cats)} categories')

    def _create_courses(self):
        from apps.courses.models import Category, Course, Lesson
        from apps.accounts.models import User

        try:
            teacher = User.objects.get(email='teacher@rustili.uz')
        except User.DoesNotExist:
            teacher = None

        try:
            gen_cat = Category.objects.get(slug='general-english')
            biz_cat = Category.objects.get(slug='business-english')
            conv_cat = Category.objects.get(slug='daily-conversation')
        except Category.DoesNotExist:
            return

        courses_data = [
            {
                'title': 'English for Beginners (A1)',
                'slug': 'english-beginners-a1',
                'description': 'Start your English journey with basic vocabulary, greetings, and simple conversations.',
                'short_description': 'Perfect starting point for complete beginners.',
                'level': 'A1',
                'category': gen_cat,
                'duration_hours': 20,
                'xp_reward': 500,
                'is_featured': True,
            },
            {
                'title': 'Everyday English Conversations',
                'slug': 'everyday-english-conversations',
                'description': 'Learn how to have natural conversations in everyday situations.',
                'short_description': 'Natural conversations for daily life.',
                'level': 'A2',
                'category': conv_cat,
                'duration_hours': 15,
                'xp_reward': 400,
                'is_featured': True,
            },
            {
                'title': 'Business English Professional',
                'slug': 'business-english-professional',
                'description': 'Master business vocabulary, emails, presentations and meetings.',
                'short_description': 'English skills for the workplace.',
                'level': 'B2',
                'category': biz_cat,
                'duration_hours': 30,
                'xp_reward': 800,
                'is_featured': True,
            },
        ]

        for data in courses_data:
            course, created = Course.objects.get_or_create(
                slug=data['slug'],
                defaults={**data, 'teacher': teacher, 'is_published': True}
            )

            if created:
                lesson_types = ['reading', 'vocabulary', 'grammar', 'listening', 'quiz']
                for i, lt in enumerate(lesson_types):
                    Lesson.objects.create(
                        course=course,
                        title=f'{lt.title()} Practice {i+1}',
                        slug=f'{lt}-practice-{i+1}-{course.slug[:10]}',
                        lesson_type=lt,
                        content=f'This is a {lt} lesson content for {course.title}.',
                        duration_minutes=20 + i * 5,
                        xp_reward=50,
                        order=i,
                        is_published=True,
                    )

        self.stdout.write(f'  Created {len(courses_data)} courses with lessons')

    def _create_vocabulary(self):
        from apps.vocabulary.models import WordCategory, Word

        cats = [
            ('Common Words', 'common-words', '⭐'),
            ('Body & Health', 'body-health', '🏥'),
            ('Food & Drinks', 'food-drinks', '🍎'),
            ('Animals', 'animals', '🐾'),
            ('Colors & Shapes', 'colors-shapes', '🎨'),
        ]

        for name, slug, icon in cats:
            WordCategory.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon})

        try:
            common = WordCategory.objects.get(slug='common-words')
        except WordCategory.DoesNotExist:
            return

        words = [
            ('hello', "'həˈloʊ'", "Salom", "Hi there!", "greeting"),
            ('beautiful', "'bjuːtɪfl'", "Chiroyli", "What a beautiful day!", "adjective"),
            ('understand', "'ʌndəˈstænd'", "Tushunmoq", "I understand English.", "verb"),
            ('important', "'ɪmˈpɔːrtnt'", "Muhim", "This is very important.", "adjective"),
            ('family', "'fæmɪli'", "Oila", "My family is big.", "noun"),
            ('friend', "'frend'", "Do'st", "She is my best friend.", "noun"),
            ('happy', "'hæpi'", "Baxtli", "I am very happy today.", "adjective"),
            ('travel', "'trævl'", "Sayohat", "I love to travel.", "verb/noun"),
            ('language', "'læŋɡwɪdʒ'", "Til", "English is a global language.", "noun"),
            ('learn', "'lɜːrn'", "O'rganmoq", "I learn English every day.", "verb"),
        ]

        for i, (word, pron, trans, example, pos) in enumerate(words):
            Word.objects.get_or_create(
                word=word,
                defaults={
                    'pronunciation': pron,
                    'translation_uz': trans,
                    'example_sentence': example,
                    'part_of_speech': pos,
                    'category': common,
                    'difficulty': 'easy',
                    'order': i,
                }
            )

        self.stdout.write(f'  Created {len(words)} vocabulary words')

    def _create_grammar(self):
        from apps.grammar.models import GrammarTopic, GrammarExample, GrammarExercise

        topics = [
            {
                'title': 'Present Simple Tense',
                'slug': 'present-simple',
                'level': 'A1',
                'icon': '⏰',
                'explanation': 'The present simple tense is used for habitual actions, general truths, and permanent situations.\n\nFormula:\n- I/You/We/They + verb\n- He/She/It + verb + s/es\n\nExamples:\n- I work every day.\n- She works in a hospital.\n- The sun rises in the east.',
                'examples': [
                    ('I play tennis every weekend.', 'Men har hafta oxiri tennis o\'ynamanM.', True),
                    ('She work in a hospital.', 'U kasalxonada ishlaydi. (noto\'g\'ri)', False),
                    ('They study English at school.', 'Ular maktabda ingliz tilini o\'rganadilar.', True),
                ],
                'exercises': [
                    ('Fill in: She ___ (work) every day.', 'works', 'fill_blank', 'He/She/It + verb + s'),
                    ('Choose the correct form:', 'works', 'multiple_choice', 'Third person singular'),
                ]
            },
            {
                'title': 'Articles: a, an, the',
                'slug': 'articles-a-an-the',
                'level': 'A1',
                'icon': '📝',
                'explanation': 'Articles in English are words placed before nouns.\n\n"a/an" - indefinite article (used for first mention or general reference)\n"the" - definite article (used for specific things)\n\nRules:\n- "a" before consonant sounds: a book, a car\n- "an" before vowel sounds: an apple, an hour\n- "the" for specific items: the sun, the book I mentioned',
                'examples': [
                    ('I saw a cat in the garden.', 'Men bog\'da bir mushuk ko\'rdim.', True),
                    ('She is an engineer.', 'U muhandis.', True),
                    ('The moon is bright tonight.', 'Bugun kechasi oy yorqin.', True),
                ],
                'exercises': [
                    ('Fill in: I have ___ umbrella.', 'an', 'fill_blank', '"umbrella" starts with a vowel sound'),
                ]
            },
        ]

        for data in topics:
            topic, created = GrammarTopic.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'title': data['title'],
                    'level': data['level'],
                    'icon': data['icon'],
                    'explanation': data['explanation'],
                    'is_published': True,
                }
            )

            if created:
                for i, (sent, trans, correct) in enumerate(data.get('examples', [])):
                    GrammarExample.objects.create(
                        topic=topic, sentence=sent, translation=trans,
                        is_correct=correct, order=i
                    )
                for i, (q, ans, etype, expl) in enumerate(data.get('exercises', [])):
                    GrammarExercise.objects.create(
                        topic=topic, question=q, correct_answer=ans,
                        exercise_type=etype, explanation=expl, order=i
                    )

        self.stdout.write(f'  Created {len(topics)} grammar topics')

    def _create_achievements(self):
        from apps.gamification.models import Achievement

        achievements = [
            ('First Lesson!', 'Complete your first lesson.', '🎯', 'learning', 50, 10, 'lessons_completed', 1),
            ('Word Wizard', 'Learn 50 vocabulary words.', '🧙', 'learning', 100, 20, 'words_learned', 50),
            ('Quiz Master', 'Complete 10 quizzes.', '❓', 'learning', 150, 30, 'quizzes_completed', 10),
            ('Streak Starter', 'Maintain a 3-day streak.', '🔥', 'streak', 75, 15, 'streak_days', 3),
            ('Dedicated Learner', 'Maintain a 7-day streak.', '💪', 'streak', 200, 40, 'streak_days', 7),
            ('Grammar Guru', 'Complete 5 grammar topics.', '📝', 'learning', 100, 20, 'grammar_topics', 5),
            ('Level 5 Achiever', 'Reach Level 5.', '⭐', 'milestone', 300, 50, 'level', 5),
            ('XP Hunter', 'Earn 1000 XP total.', '⚡', 'milestone', 200, 40, 'total_xp', 1000),
        ]

        for name, desc, icon, cat, xp, coin, ctype, cval in achievements:
            Achievement.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc, 'icon': icon, 'category': cat,
                    'xp_reward': xp, 'coin_reward': coin,
                    'condition_type': ctype, 'condition_value': cval
                }
            )
        self.stdout.write(f'  Created {len(achievements)} achievements')

    def _create_quizzes(self):
        from apps.quiz.models import Quiz, Question, Choice

        quiz, created = Quiz.objects.get_or_create(
            title='General English Test',
            defaults={
                'description': 'Test your general English knowledge.',
                'quiz_type': 'general',
                'time_limit_minutes': 15,
                'pass_score': 70,
                'xp_reward': 100,
                'is_published': True,
            }
        )

        if created:
            questions_data = [
                {
                    'text': 'What is the plural of "child"?',
                    'type': 'mcq',
                    'choices': [('childs', False), ('children', True), ('childes', False), ('childs', False)],
                    'explanation': '"child" has an irregular plural: children'
                },
                {
                    'text': 'She ___ to school every day.',
                    'type': 'mcq',
                    'choices': [('go', False), ('goes', True), ('going', False), ('gone', False)],
                    'explanation': 'Third person singular (she) takes "goes"'
                },
                {
                    'text': 'True or False: "I am" is the contracted form of "I am".',
                    'type': 'true_false',
                    'choices': [('True', True), ('False', False)],
                    'explanation': "I'm = I am"
                },
            ]

            for i, qdata in enumerate(questions_data):
                q = Question.objects.create(
                    quiz=quiz,
                    text=qdata['text'],
                    question_type=qdata['type'],
                    explanation=qdata.get('explanation', ''),
                    points=10,
                    order=i
                )
                for j, (text, is_correct) in enumerate(qdata['choices']):
                    Choice.objects.create(question=q, text=text, is_correct=is_correct, order=j)

        self.stdout.write('  Created quiz with questions')

    def _create_leaderboard(self):
        from apps.gamification.models import UserProgress, LeaderboardEntry
        from apps.accounts.models import User

        students = User.objects.filter(role='student').order_by('-progress__xp')
        LeaderboardEntry.objects.filter(period='weekly').delete()

        for rank, student in enumerate(students, 1):
            try:
                xp = student.progress.xp
            except Exception:
                xp = 0
            LeaderboardEntry.objects.create(
                user=student, period='weekly', xp=xp, rank=rank
            )
        self.stdout.write(f'  Created leaderboard entries')
