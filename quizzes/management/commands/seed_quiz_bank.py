import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from quizzes.models import Category, Choice, Question, Quiz

from . import quiz_bank_data as bank


def build_choices(rng, question):
    choices = [(question['correct'], True)]
    for w in question['wrongs']:
        choices.append((w, False))
    rng.shuffle(choices)
    return choices


def unique_slug(title, used):
    base = slugify(title)[:200]
    slug = base
    i = 1
    while slug in used:
        slug = '{}-{}'.format(base, i)
        i += 1
    used.add(slug)
    return slug


class Command(BaseCommand):
    help = 'Seed the full quiz bank: 570 quizzes across 22 categories.'

    def add_arguments(self, parser):
        parser.add_argument('--seed', type=int, default=42,
                            help='Random seed for reproducibility (default 42).')
        parser.add_argument('--reset', action='store_true',
                            help='Delete quizzes created by this command first (idempotent re-run).')

    @transaction.atomic
    def handle(self, *args, **options):
        seed = options['seed']
        rng = random.Random(seed)
        used_slugs = set(Quiz.objects.values_list('slug', flat=True))

        if options['reset']:
            bank_slugs = {cat['slug'] for cat in bank.CATEGORIES}
            Quiz.objects.filter(category__slug__in=bank_slugs).delete()
            Category.objects.filter(slug__in=bank_slugs).delete()
            used_slugs = set(Quiz.objects.values_list('slug', flat=True))
            existing_titles = set(Quiz.objects.values_list('title', flat=True))
            self.stdout.write(self.style.WARNING('Cleared previous bank data.'))

        created = 0
        total_questions = 0

        for cat in bank.CATEGORIES:
            category, _ = Category.objects.get_or_create(
                slug=cat['slug'],
                defaults={
                    'name': cat['name'],
                    'emoji': cat['emoji'],
                    'gradient_from': cat['gradient_from'],
                    'gradient_to': cat['gradient_to'],
                    'description': cat['description'],
                },
            )
            pool = cat['build'](rng)
            rng.shuffle(pool)
            titles = bank.build_titles(rng, cat['title_fragments'], cat['count'],
                                       exclude=existing_titles)

            for title in titles:
                num_questions = rng.randint(10, 40)
                difficulty = rng.choices(
                    ['easy', 'medium', 'hard'],
                    weights=[30, 45, 25],
                    k=1,
                )[0]
                duration = min(20, max(3, num_questions // 2 + rng.randint(1, 3)))
                pass_percent = rng.randint(50, 70)

                quiz, was_created = Quiz.objects.get_or_create(
                    title=title,
                    defaults={
                        'slug': unique_slug(title, used_slugs),
                        'description': cat['description'],
                        'category': category,
                        'difficulty': difficulty,
                        'duration_minutes': duration,
                        'pass_percent': pass_percent,
                    },
                )
                if not was_created:
                    continue
                existing_titles.add(title)

                sample = rng.sample(pool, min(num_questions, len(pool)))
                for i, qd in enumerate(sample):
                    qobj = Question.objects.create(quiz=quiz, text=qd['text'], order=i)
                    for j, (text, is_correct) in enumerate(build_choices(rng, qd)):
                        Choice.objects.create(
                            question=qobj, text=text, is_correct=is_correct, order=j
                        )
                created += 1
                total_questions += len(sample)

        self.stdout.write(self.style.SUCCESS(
            'Seeded {} quizzes with {} questions across {} categories.'.format(
                created, total_questions, Category.objects.filter(
                    slug__in={c['slug'] for c in bank.CATEGORIES}).count()
            )
        ))
