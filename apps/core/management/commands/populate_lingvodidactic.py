# -*- coding: utf-8 -*-
"""
Management command: python manage.py populate_lingvodidactic

Seeds the authoring course "LingvoDidactic PBL 1.0" — a digital educational
system for developing linguodidactic competencies of future Russian language
teachers based on problem-based learning technologies.

Creates:
  * category "LingvoDidactic PBL";
  * 10 course-modules with lessons (module passport, lectures, problem
    situations, cases, practical works, glossaries, self-study/reflection);
  * a 10-question quiz for every module (linked to its quiz lesson);
  * the entrance diagnostic test.

The command is idempotent: existing objects (matched by slug/title) are kept.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Populate the LingvoDidactic PBL 1.0 course (10 modules, quizzes, diagnostics)'

    def handle(self, *args, **options):
        from apps.core.lingvo_data import MODULES, DIAGNOSTIC_TESTS

        self.stdout.write('Populating LingvoDidactic PBL 1.0 ...')

        category = self._get_category()
        teacher = self._get_teacher()

        total_lessons = 0
        total_questions = 0
        for module in MODULES:
            lessons, questions = self._create_module(module, category, teacher)
            total_lessons += lessons
            total_questions += questions

        diag_tests, diag_questions = self._create_diagnostics(DIAGNOSTIC_TESTS)

        self.stdout.write(self.style.SUCCESS(
            'Done: %d modules, %d lessons, %d quiz questions, '
            '%d diagnostic tests (%d questions).' % (
                len(MODULES), total_lessons, total_questions,
                diag_tests, diag_questions,
            )
        ))

    def _get_category(self):
        from apps.courses.models import Category

        category, _ = Category.objects.get_or_create(
            slug='lingvodidactic-pbl',
            defaults={
                'name': 'LingvoDidactic PBL',
                'icon': '🎓',
                'color': '#8b5cf6',
                'order': 0,
            }
        )
        return category

    def _get_teacher(self):
        from apps.accounts.models import User

        teacher = User.objects.filter(email='teacher@lingvocompetence.uz').first()
        if teacher is None:
            teacher = User.objects.filter(role='teacher').first()
        return teacher

    def _create_module(self, module, category, teacher):
        from apps.courses.models import Course, Lesson
        from apps.quiz.models import Quiz, Question, Choice

        course, created = Course.objects.get_or_create(
            slug=module['slug'],
            defaults={
                'title': module['title'],
                'description': module['description'],
                'short_description': module['short_description'],
                'category': category,
                'teacher': teacher,
                'level': module['level'],
                'duration_hours': module['duration_hours'],
                'xp_reward': module['xp_reward'],
                'coin_reward': module['xp_reward'] // 5,
                'has_certificate': True,
                'is_published': True,
                'is_featured': module['order'] == 1,
                'is_free': True,
                'order': module['order'],
            }
        )
        self.stdout.write('  [%s] module %02d: %s' % (
            'new' if created else 'ok ', module['order'], module['slug']))

        lesson_count = 0
        for i, lesson_data in enumerate(module['lessons']):
            _, lesson_created = Lesson.objects.get_or_create(
                course=course,
                slug=lesson_data['slug'],
                defaults={
                    'title': lesson_data['title'],
                    'lesson_type': lesson_data['type'],
                    'content': lesson_data['content'],
                    'duration_minutes': lesson_data['duration'],
                    'xp_reward': lesson_data['xp'],
                    'order': i,
                    'is_published': True,
                    'is_free_preview': i == 0,
                }
            )
            if lesson_created:
                lesson_count += 1

        quiz_data = module['quiz']
        quiz_lesson, _ = Lesson.objects.get_or_create(
            course=course,
            slug='%s-test' % module['slug'].replace('ld-modul', 'ld-m'),
            defaults={
                'title': quiz_data['title'],
                'lesson_type': 'quiz',
                'description': quiz_data['description'],
                'content': (
                    '%s\n\nТест доступен в разделе «Тесты» платформы. '
                    'Лимит времени: %d минут. Проходной балл: %d %%.' % (
                        quiz_data['description'],
                        quiz_data['time_limit'],
                        quiz_data['pass_score'],
                    )
                ),
                'duration_minutes': quiz_data['time_limit'],
                'xp_reward': 60,
                'order': len(module['lessons']),
                'is_published': True,
            }
        )

        question_count = 0
        quiz, quiz_created = Quiz.objects.get_or_create(
            title=quiz_data['title'],
            defaults={
                'description': quiz_data['description'],
                'quiz_type': 'course',
                'course': course,
                'lesson': quiz_lesson,
                'time_limit_minutes': quiz_data['time_limit'],
                'pass_score': quiz_data['pass_score'],
                'xp_reward': 120,
                'coin_reward': 25,
                'is_published': True,
                'shuffle_questions': True,
            }
        )
        if quiz_created:
            for qi, qdata in enumerate(quiz_data['questions']):
                question = Question.objects.create(
                    quiz=quiz,
                    text=qdata['text'],
                    question_type=qdata['type'],
                    explanation=qdata.get('explanation', ''),
                    points=10,
                    order=qi,
                )
                for ci, (choice_text, is_correct) in enumerate(qdata['choices']):
                    Choice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=is_correct,
                        order=ci,
                    )
                question_count += 1

        return lesson_count, question_count

    def _create_diagnostics(self, tests_data):
        from apps.diagnostic.models import DiagnosticTest, DiagnosticQuestion

        created_tests = 0
        created_questions = 0
        option_letters = ['A', 'B', 'C', 'D']

        for order, test_data in enumerate(tests_data):
            test, created = DiagnosticTest.objects.get_or_create(
                title=test_data['title'],
                defaults={
                    'test_type': test_data['test_type'],
                    'description': test_data['description'],
                    'time_limit_minutes': test_data['time_limit'],
                    'is_active': True,
                    'order': order,
                }
            )
            if not created:
                continue

            created_tests += 1
            for qi, qdata in enumerate(test_data['questions']):
                options = qdata.get('options', [])
                fields = {
                    'test': test,
                    'text': qdata['text'],
                    'question_type': qdata['type'],
                    'correct_answer': qdata['correct'],
                    'explanation': qdata.get('explanation', ''),
                    'cefr_level': qdata.get('cefr', 'B1'),
                    'points': qdata.get('points', 1),
                    'order': qi,
                }
                for letter, option in zip(option_letters, options):
                    fields['option_%s' % letter.lower()] = option
                DiagnosticQuestion.objects.create(**fields)
                created_questions += 1

        return created_tests, created_questions
