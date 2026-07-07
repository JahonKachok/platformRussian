"""
Management command: python manage.py populate_demo
Creates demo data for the LingvoCompetence (Russian language learning) platform.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate demo data for LingvoCompetence platform (Russian language learning)'

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

        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))

    def _create_users(self):
        from apps.accounts.models import User

        if not User.objects.filter(email='admin@lingvocompetence.uz').exists():
            User.objects.create_superuser(
                username='admin', email='admin@lingvocompetence.uz',
                password='admin123', first_name='Admin', last_name='LingvoCompetence',
                role='admin', email_verified=True
            )
            self.stdout.write('  Created admin: admin@lingvocompetence.uz / admin123')

        if not User.objects.filter(email='teacher@lingvocompetence.uz').exists():
            User.objects.create_user(
                username='teacher1', email='teacher@lingvocompetence.uz',
                password='teacher123', first_name='Наталья', last_name='Иванова',
                role='teacher', email_verified=True, is_active=True,
                bio='Rus tili o\'qituvchisi, 10 yillik tajriba.'
            )
            self.stdout.write('  Created teacher: teacher@lingvocompetence.uz / teacher123')

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
                except Exception:
                    pass

        self.stdout.write('  Created demo students')

    def _create_categories(self):
        from apps.courses.models import Category
        cats = [
            ('Umumiy rus tili', 'umumiy-rus-tili', '📚', '#6366f1'),
            ('Biznes rus tili', 'biznes-rus-tili', '💼', '#8b5cf6'),
            ('Sayohat uchun rus tili', 'sayohat-rus-tili', '✈️', '#3b82f6'),
            ('Akademik rus tili', 'akademik-rus-tili', '🎓', '#10b981'),
            ('Kundalik muloqot', 'kundalik-muloqot', '💬', '#f59e0b'),
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
            teacher = User.objects.get(email='teacher@lingvocompetence.uz')
        except User.DoesNotExist:
            teacher = None

        try:
            gen_cat = Category.objects.get(slug='umumiy-rus-tili')
            biz_cat = Category.objects.get(slug='biznes-rus-tili')
            conv_cat = Category.objects.get(slug='kundalik-muloqot')
        except Category.DoesNotExist:
            return

        courses_data = [
            {
                'title': 'Rus tili: Boshlang\'ich daraja (A1)',
                'slug': 'rus-tili-boshlangich-a1',
                'description': 'Rus alifbosi, asosiy so\'zlar, salomlashish va oddiy gaplardan boshlang.',
                'short_description': 'Mutlaq boshlang\'ichlar uchun eng yaxshi kurs.',
                'level': 'A1',
                'category': gen_cat,
                'duration_hours': 20,
                'xp_reward': 500,
                'is_featured': True,
            },
            {
                'title': 'Kundalik rus tili muloqoti',
                'slug': 'kundalik-rus-tili-muloqoti',
                'description': 'Kundalik hayotda tabiiy ravishda rus tilida so\'zlashishni o\'rganing.',
                'short_description': 'Kundalik hayot uchun tabiiy muloqot.',
                'level': 'A2',
                'category': conv_cat,
                'duration_hours': 15,
                'xp_reward': 400,
                'is_featured': True,
            },
            {
                'title': 'Biznes rus tili',
                'slug': 'biznes-rus-tili',
                'description': 'Biznes leksikasi, elektron xatlar, taqdimotlar va yig\'ilishlar uchun rus tili.',
                'short_description': 'Ish joyida kerakli rus tili ko\'nikmalari.',
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
                lesson_titles = {
                    'reading': 'O\'qish mashqi',
                    'vocabulary': 'Leksika mashqi',
                    'grammar': 'Grammatika mashqi',
                    'listening': 'Tinglash mashqi',
                    'quiz': 'Test',
                }
                for i, lt in enumerate(lesson_types):
                    Lesson.objects.create(
                        course=course,
                        title=f'{lesson_titles[lt]} {i + 1}',
                        slug=f'{lt}-mashq-{i + 1}-{course.slug[:10]}',
                        lesson_type=lt,
                        content=f'Bu {course.title} kursi uchun {lesson_titles[lt].lower()} darsidir.',
                        duration_minutes=20 + i * 5,
                        xp_reward=50,
                        order=i,
                        is_published=True,
                    )

        self.stdout.write(f'  Created {len(courses_data)} courses with lessons')

    def _create_vocabulary(self):
        from apps.vocabulary.models import WordCategory, Word

        cats = [
            ('Umumiy so\'zlar', 'umumiy-sozlar', '⭐'),
            ('Tana va sog\'liq', 'tana-sogliq', '🏥'),
            ('Ovqat va ichimliklar', 'ovqat-ichimliklar', '🍎'),
            ('Hayvonlar', 'hayvonlar', '🐾'),
            ('Ranglar va shakllar', 'ranglar-shakllar', '🎨'),
        ]

        for name, slug, icon in cats:
            WordCategory.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon})

        # Russian words per category: (word, pronunciation, translation_uz, example_sentence, part_of_speech, difficulty)
        words_by_category = {
            'umumiy-sozlar': [
                ('привет', 'prʲɪˈvʲet', 'Salom', 'Привет! Как дела?', 'undov', 'easy'),
                ('спасибо', 'spɐˈsʲibə', 'Rahmat', 'Большое спасибо!', 'undov', 'easy'),
                ('пожалуйста', 'pɐˈʐalʊstə', 'Iltimos / Marhamat', 'Дайте, пожалуйста, книгу.', 'undov', 'easy'),
                ('да', 'da', 'Ha', 'Да, я понимаю.', 'yukla', 'easy'),
                ('нет', 'nʲet', "Yo'q", 'Нет, это неправильно.', 'yukla', 'easy'),
                ('хорошо', 'xərɐˈʂo', 'Yaxshi / Xo\'p', 'Всё хорошо, спасибо.', 'sifat/yukla', 'easy'),
                ('понимать', 'pənʲɪˈmatʲ', 'Tushunmoq', 'Я понимаю по-русски.', 'fe\'l', 'medium'),
                ('говорить', 'ɡəvɐˈrʲitʲ', 'Gapirmoq / So\'zlamoq', 'Он говорит по-русски.', 'fe\'l', 'medium'),
                ('учить', 'ʊˈtʲitʲ', "O'rganmoq", 'Я учу русский язык.', 'fe\'l', 'medium'),
                ('язык', 'jɪˈzɨk', 'Til', 'Русский язык красивый.', 'ot', 'easy'),
            ],
            'tana-sogliq': [
                ('голова', 'ɡɐˈɫəvə', 'Bosh', 'У меня болит голова.', 'ot', 'easy'),
                ('рука', 'rʊˈka', "Qo'l", 'Дай мне руку.', 'ot', 'easy'),
                ('нога', 'nɐˈɡa', 'Oyoq', 'У меня болит нога.', 'ot', 'easy'),
                ('глаз', 'ɡɫas', "Ko'z", 'У него красивые глаза.', 'ot', 'easy'),
                ('сердце', 'ˈsʲertsə', 'Yurak', 'Моё сердце бьётся быстро.', 'ot', 'medium'),
                ('здоровье', 'zdɐˈrovʲjə', 'Salomatlik', 'Здоровье — самое важное.', 'ot', 'medium'),
                ('больной', 'bɐlʲˈnoj', 'Kasal', 'Он больной сегодня.', 'sifat', 'easy'),
                ('врач', 'vratɕ', 'Shifokor', 'Врач осмотрел пациента.', 'ot', 'easy'),
                ('болеть', 'bɐˈlʲetʲ', "Og'rimoq", 'У меня болит голова.', "fe'l", 'medium'),
                ('лекарство', 'lʲɪˈkarstvə', 'Dori', 'Прими это лекарство.', 'ot', 'medium'),
            ],
            'ovqat-ichimliklar': [
                ('хлеб', 'xlʲep', 'Non', 'Купи хлеб в магазине.', 'ot', 'easy'),
                ('вода', 'vɐˈda', 'Suv', 'Дай мне стакан воды.', 'ot', 'easy'),
                ('молоко', 'məɫɐˈko', 'Sut', 'Я пью молоко утром.', 'ot', 'easy'),
                ('чай', 'tɕaj', 'Choy', 'Хочешь чашку чая?', 'ot', 'easy'),
                ('яблоко', 'ˈjabɫəkə', 'Olma', 'Это яблоко очень вкусное.', 'ot', 'easy'),
                ('мясо', 'ˈmʲasə', "Go'sht", 'Она готовит мясо.', 'ot', 'medium'),
                ('суп', 'sup', 'Sho\'rva', 'Суп очень горячий.', 'ot', 'easy'),
                ('сахар', 'ˈsaxər', 'Shakar', 'Не добавляй много сахара.', 'ot', 'medium'),
                ('завтрак', 'ˈzaftrək', 'Nonushta', 'Завтрак готов.', 'ot', 'medium'),
                ('вкусный', 'ˈfkusnɨj', 'Mazali', 'Этот торт очень вкусный.', 'sifat', 'easy'),
            ],
            'hayvonlar': [
                ('кошка', 'ˈkoʂkə', 'Mushuk', 'У меня есть кошка.', 'ot', 'easy'),
                ('собака', 'sɐˈbakə', 'It', 'Собака бежит по улице.', 'ot', 'easy'),
                ('лошадь', 'ˈɫoʂətʲ', 'Ot', 'Лошадь бежит быстро.', 'ot', 'medium'),
                ('птица', 'ˈptʲitsə', 'Qush', 'Птица поёт красиво.', 'ot', 'easy'),
                ('рыба', 'ˈrɨbə', 'Baliq', 'Рыба плавает в реке.', 'ot', 'easy'),
                ('корова', 'kɐˈrovə', 'Sigir', 'Корова даёт молоко.', 'ot', 'easy'),
                ('медведь', 'mʲɪdˈvʲetʲ', 'Ayiq', 'Медведь живёт в лесу.', 'ot', 'medium'),
                ('волк', 'voɫk', "Bo'ri", 'Волк воет ночью.', 'ot', 'medium'),
                ('заяц', 'ˈzajəts', 'Quyon', 'Заяц быстро бегает.', 'ot', 'medium'),
                ('лев', 'lʲef', 'Sher', 'Лев — царь зверей.', 'ot', 'easy'),
            ],
            'ranglar-shakllar': [
                ('красный', 'ˈkrasnɨj', 'Qizil', 'У неё красное платье.', 'sifat', 'easy'),
                ('синий', 'ˈsʲinʲɪj', "Ko'k", 'Небо синее.', 'sifat', 'easy'),
                ('жёлтый', 'ˈʐoɫtɨj', 'Sariq', 'Жёлтый цветок красивый.', 'sifat', 'easy'),
                ('зелёный', 'zʲɪˈlʲonɨj', 'Yashil', 'Трава зелёная.', 'sifat', 'easy'),
                ('чёрный', 'ˈtɕornɨj', 'Qora', 'Чёрный кот сидит на крыше.', 'sifat', 'easy'),
                ('белый', 'ˈbʲeɫɨj', 'Oq', 'Снег белый.', 'sifat', 'easy'),
                ('круг', 'kruk', 'Doira', 'Нарисуй круг.', 'ot', 'medium'),
                ('квадрат', 'kvɐˈdrat', 'Kvadrat', 'Это квадрат, а не круг.', 'ot', 'medium'),
                ('треугольник', 'trʲɪʊˈɡolʲnʲɪk', 'Uchburchak', 'Треугольник имеет три угла.', 'ot', 'hard'),
                ('цвет', 'tsvʲet', 'Rang', 'Какой твой любимый цвет?', 'ot', 'easy'),
            ],
        }

        total_created = 0
        for slug, words in words_by_category.items():
            try:
                category = WordCategory.objects.get(slug=slug)
            except WordCategory.DoesNotExist:
                continue

            for i, (word, pron, trans, example, pos, difficulty) in enumerate(words):
                _, created = Word.objects.get_or_create(
                    word=word,
                    defaults={
                        'pronunciation': pron,
                        'translation_uz': trans,
                        'example_sentence': example,
                        'part_of_speech': pos,
                        'category': category,
                        'difficulty': difficulty,
                        'order': i,
                    }
                )
                if created:
                    total_created += 1

        self.stdout.write(f'  Created {total_created} vocabulary words')

    def _create_grammar(self):
        from apps.grammar.models import GrammarTopic, GrammarExample, GrammarExercise

        topics = [
            {
                'title': 'Rus alifbosi (Алфавит)',
                'slug': 'rus-alifbosi',
                'level': 'A1',
                'icon': '🔤',
                'explanation': (
                    'Rus alifbosi 33 ta harfdan iborat (кириллица — kirill yozuvi).\n\n'
                    'Unlilar: А, Е, Ё, И, О, У, Ы, Э, Ю, Я\n'
                    'Undoshlar: Б, В, Г, Д, Ж, З, К, Л, М, Н, П, Р, С, Т, Ф, Х, Ц, Ч, Ш, Щ\n'
                    'Belgilar: Ъ (qattiq belgi), Ь (yumshoq belgi)\n\n'
                    'Misollar:\n'
                    '- А — арбуз (arbuz — tarvuz)\n'
                    '- Б — банан (banan — banan)\n'
                    '- В — вода (voda — suv)\n'
                    '- Г — город (gorod — shahar)\n'
                    '- Д — дом (dom — uy)'
                ),
                'examples': [
                    ('Москва', 'Moskva — Rossiyaning poytaxti', True),
                    ('Привет', 'Privet — Salom', True),
                    ('Россия', 'Rossiya — Rossiya davlati', True),
                ],
                'exercises': [
                    ('Qaysi harf "V" tovushini beradi?', 'В', 'multiple_choice', 'В harfi "v" tovushini bildiradi'),
                    ('Rus alifbosida nechta harf bor?', '33', 'fill_blank', 'Rus alifbosi 33 harfdan iborat'),
                ]
            },
            {
                'title': 'Rod (Род) — Ot jinsi',
                'slug': 'rod-ot-jinsi',
                'level': 'A1',
                'icon': '⚥',
                'explanation': (
                    'Rus tilida otlar uch jinsga bo\'linadi:\n\n'
                    '🔵 Erkak jins (мужской род) — -й, -ь, undosh bilan tugaydi:\n'
                    '   стол (stol — stol), брат (brat — aka), день (den\' — kun)\n\n'
                    '🔴 Urg\'u jins (женский род) — -а, -я, -ь bilan tugaydi:\n'
                    '   книга (kniga — kitob), земля (zemlya — yer), ночь (noch\' — tun)\n\n'
                    '🟢 O\'rta jins (средний род) — -о, -е, -ие bilan tugaydi:\n'
                    '   окно (okno — deraza), море (more — dengiz), здание (zdanie — bino)'
                ),
                'examples': [
                    ('стол — мужской род', 'Stol — erkak jinsiga kiradi (undosh bilan tugaydi)', True),
                    ('книга — женский род', 'Kitob — urg\'u jinsiga kiradi (-а bilan tugaydi)', True),
                    ('окно — средний род', 'Deraza — o\'rta jinsiga kiradi (-о bilan tugaydi)', True),
                    ('книга — мужской род', 'Bu noto\'g\'ri: книга urg\'u jinsiga kiradi', False),
                ],
                'exercises': [
                    ('«Письмо» (xat) qaysi jinsga kiradi?', 'средний род', 'multiple_choice',
                     'Письмо -о bilan tugaydi → o\'rta jins'),
                    ('«Мама» qaysi jinsga kiradi?', 'женский род', 'fill_blank',
                     'Мама -а bilan tugaydi → urg\'u jins'),
                ]
            },
            {
                'title': 'Настоящее время (Hozirgi zamon)',
                'slug': 'nastoyashchee-vremya',
                'level': 'A2',
                'icon': '⏰',
                'explanation': (
                    'Rus tilida hozirgi zamon fe\'llari shaxs va songa qarab o\'zgaradi.\n\n'
                    'I-tur (I спряжение): читать (o\'qimoq)\n'
                    '   я читаю   — men o\'qiyman\n'
                    '   ты читаешь — sen o\'qiysan\n'
                    '   он/она читает — u o\'qiydi\n'
                    '   мы читаем  — biz o\'qiymiz\n'
                    '   вы читаете — siz/sizlar o\'qiysiz\n'
                    '   они читают — ular o\'qiydi\n\n'
                    'II-tur (II спряжение): говорить (gapirmoq)\n'
                    '   я говорю   — men gapiraman\n'
                    '   ты говоришь — sen gapirassan\n'
                    '   он/она говорит — u gapiradi\n'
                    '   мы говорим  — biz gapiramiz\n'
                    '   вы говорите — siz/sizlar gapirasiz\n'
                    '   они говорят — ular gapiradi'
                ),
                'examples': [
                    ('Я читаю книгу.', 'Men kitob o\'qiyapman.', True),
                    ('Она говорит по-русски.', 'U rus tilida gapiradi.', True),
                    ('Мы учим русский язык.', 'Biz rus tilini o\'rganamiz.', True),
                    ('Он говорю хорошо.', 'Bu noto\'g\'ri: «он» bilan «говорю» ishlatilmaydi.', False),
                ],
                'exercises': [
                    ('To\'ldiring: Я ___ (читать) книгу.', 'читаю', 'fill_blank',
                     'Men uchun I-tur fe\'li: читаю'),
                    ('To\'ldiring: Они ___ (говорить) по-русски.', 'говорят', 'fill_blank',
                     'Ular uchun II-tur fe\'li: говорят'),
                    ('Tanlang: Ты ___ (учить) русский?', 'учишь', 'multiple_choice',
                     '"Ты" bilan II-tur: учишь'),
                ]
            },
            {
                'title': 'Отрицание (Inkor)',
                'slug': 'otricanie-inkor',
                'level': 'A1',
                'icon': '🚫',
                'explanation': (
                    'Rus tilida inkorni ifodalash uchun «не» yuklamasi ishlatiladi.\n\n'
                    'Qoida: не + fe\'l yoki sifat\n\n'
                    'Misollar:\n'
                    '   Я знаю. → Я не знаю.  (Men bilaman → Men bilmayman)\n'
                    '   Он дома. → Он не дома. (U uyda → U uyda emas)\n'
                    '   Это хорошо. → Это не хорошо. (Bu yaxshi → Bu yaxshi emas)\n\n'
                    'Muhim: «нет» — yo\'q (mavjud emaslik)\n'
                    '   Есть чай? — Нет, нет чая. (Choy bormi? — Yo\'q, choy yo\'q.)'
                ),
                'examples': [
                    ('Я не понимаю.', 'Men tushunmayman.', True),
                    ('Она не говорит по-русски.', 'U rus tilida gapirmaydi.', True),
                    ('Это не правда.', 'Bu to\'g\'ri emas.', True),
                    ('Я не знаете.', 'Bu noto\'g\'ri: «я» bilan «знаете» ishlatilmaydi.', False),
                ],
                'exercises': [
                    ('Inkorda yozing: Я знаю. → Я ___ знаю.', 'не', 'fill_blank',
                     'Inkor uchun «не» ishlatiladi'),
                    ('Tanlang: Он ___ дома. (u uyda emas)', 'не', 'multiple_choice',
                     '«не» — inkor yuklamasi'),
                ]
            },
            {
                'title': 'Притяжательные местоимения (Egalik olmoshlari)',
                'slug': 'egalik-olmoshlari',
                'level': 'A2',
                'icon': '👤',
                'explanation': (
                    'Egalik olmoshlari otning jinsi va soniga qarab o\'zgaradi.\n\n'
                    'мой/моя/моё/мои — mening\n'
                    '   мой брат (mening akam) — erkak jins\n'
                    '   моя сестра (mening opam) — urg\'u jins\n'
                    '   моё окно (mening derazam) — o\'rta jins\n'
                    '   мои книги (mening kitoblarim) — ko\'plik\n\n'
                    'твой/твоя/твоё/твои — sening\n'
                    'его — uning (erkak)\n'
                    'её — uning (ayol)\n'
                    'наш/наша/наше/наши — bizning\n'
                    'ваш/ваша/ваше/ваши — sizning\n'
                    'их — ularning'
                ),
                'examples': [
                    ('Это мой дом.', 'Bu mening uyim.', True),
                    ('Где твоя книга?', 'Sening kitobing qayerda?', True),
                    ('Это наш класс.', 'Bu bizning sinfimiz.', True),
                    ('Это моя брат.', 'Bu noto\'g\'ri: «брат» erkak jinsida → «мой брат»', False),
                ],
                'exercises': [
                    ('To\'ldiring: Это ___ (mening) книга.', 'моя', 'fill_blank',
                     '«книга» urg\'u jinsida → «моя»'),
                    ('To\'ldiring: Где ___ (sening) паспорт?', 'твой', 'fill_blank',
                     '«паспорт» erkak jinsida → «твой»'),
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
            ('Birinchi dars!', 'Birinchi darsingizni tugatdingiz.', '🎯', 'learning', 50, 10, 'lessons_completed', 1),
            ('So\'z ustasi', '50 ta so\'z o\'rganing.', '🧙', 'learning', 100, 20, 'words_learned', 50),
            ('Test ustasi', '10 ta test bajaring.', '❓', 'learning', 150, 30, 'quizzes_completed', 10),
            ('Izchil o\'quvchi', '3 kunlik seriya saqlang.', '🔥', 'streak', 75, 15, 'streak_days', 3),
            ('Bag\'ishlangan o\'quvchi', '7 kunlik seriya saqlang.', '💪', 'streak', 200, 40, 'streak_days', 7),
            ('Grammatika ustasi', '5 ta grammatika mavzusini tugating.', '📝', 'learning', 100, 20, 'grammar_topics', 5),
            ('5-daraja yutuvchi', '5-darajaga yeting.', '⭐', 'milestone', 300, 50, 'level', 5),
            ('XP ovchisi', 'Jami 1000 XP yig\'ing.', '⚡', 'milestone', 200, 40, 'total_xp', 1000),
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
            title='Rus tili: Umumiy test',
            defaults={
                'description': 'Rus tili bo\'yicha umumiy bilimlaringizni sinab ko\'ring.',
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
                    'text': '«Привет» so\'zi o\'zbekcha nima degan ma\'noni anglatadi?',
                    'type': 'mcq',
                    'choices': [
                        ('Rahmat', False),
                        ('Salom', True),
                        ('Xayr', False),
                        ('Kechirasiz', False),
                    ],
                    'explanation': '«Привет» — norasmiy salomlashish so\'zi (salom).'
                },
                {
                    'text': '«Книга» so\'zi qaysi jinsga kiradi?',
                    'type': 'mcq',
                    'choices': [
                        ('Мужской род (erkak jins)', False),
                        ('Женский род (urg\'u jins)', True),
                        ('Средний род (o\'rta jins)', False),
                        ('Hech qanday jins yo\'q', False),
                    ],
                    'explanation': '«Книга» -а bilan tugaydi → urg\'u jins (женский род).'
                },
                {
                    'text': 'To\'ldiring: Я ___ (читать) книгу.',
                    'type': 'mcq',
                    'choices': [
                        ('читает', False),
                        ('читаю', True),
                        ('читаешь', False),
                        ('читают', False),
                    ],
                    'explanation': '«Я» (men) bilan I-tur fe\'li «читаю» ishlatiladi.'
                },
                {
                    'text': '«Спасибо» so\'zi o\'zbekcha nima degan ma\'noni anglatadi?',
                    'type': 'mcq',
                    'choices': [
                        ('Salom', False),
                        ('Iltimos', False),
                        ('Rahmat', True),
                        ('Xayr', False),
                    ],
                    'explanation': '«Спасибо» — minnatdorlik bildiruvchi so\'z (rahmat).'
                },
                {
                    'text': 'Rus tilida inkorni ifodalash uchun qaysi yuklamadan foydalaniladi?',
                    'type': 'mcq',
                    'choices': [
                        ('да', False),
                        ('не', True),
                        ('и', False),
                        ('но', False),
                    ],
                    'explanation': '«не» yuklamasi fe\'l va sifatlar oldiga qo\'yiladi.'
                },
                {
                    'text': '«Мой» olmoshi «Моя» ga qachon o\'zgaradi?',
                    'type': 'mcq',
                    'choices': [
                        ('Erkak jinsidagi otlar oldida', False),
                        ('Urg\'u jinsidagi otlar oldida', True),
                        ('O\'rta jinsidagi otlar oldida', False),
                        ('Ko\'plikdagi otlar oldida', False),
                    ],
                    'explanation': 'Моя — urg\'u jins (женский род) uchun ishlatiladi: моя книга, моя мама.'
                },
                {
                    'text': 'To\'g\'ri yoki noto\'g\'ri: Rus alifbosi 33 ta harfdan iborat.',
                    'type': 'true_false',
                    'choices': [
                        ('To\'g\'ri', True),
                        ('Noto\'g\'ri', False),
                    ],
                    'explanation': 'Rus (kirill) alifbosi 33 ta harfdan iborat.'
                },
                {
                    'text': '«Окно» so\'zi qaysi jinsga kiradi?',
                    'type': 'mcq',
                    'choices': [
                        ('Мужской род', False),
                        ('Женский род', False),
                        ('Средний род', True),
                        ('Aniqlab bo\'lmaydi', False),
                    ],
                    'explanation': '«Окно» -о bilan tugaydi → o\'rta jins (средний род).'
                },
                {
                    'text': 'Qaysi jumlada hozirgi zamon to\'g\'ri ishlatilgan?',
                    'type': 'mcq',
                    'choices': [
                        ('Она говорю по-русски.', False),
                        ('Она говорит по-русски.', True),
                        ('Она говоришь по-русски.', False),
                        ('Она говорим по-русски.', False),
                    ],
                    'explanation': '«Она» (u — ayol) bilan II-tur fe\'li «говорит» ishlatiladi.'
                },
                {
                    'text': '«Нет» va «не» orasidagi farq nima?',
                    'type': 'mcq',
                    'choices': [
                        ('Ikkalasi ham bir xil ma\'noda', False),
                        ('«Нет» — yo\'q (mavjud emaslik), «не» — inkor yuklamasi', True),
                        ('«Не» — yo\'q, «нет» — inkor yuklamasi', False),
                        ('Faqat «нет» ishlatiladi', False),
                    ],
                    'explanation': (
                        '«Нет» mustaqil so\'z (yo\'q), «не» esa fe\'l va sifatlar '
                        'oldiga qo\'yiladigan yuklamаdir.'
                    )
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
        self.stdout.write('  Created leaderboard entries')
