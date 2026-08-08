import json

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Case, F, IntegerField, Value, When
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Category, Choice, Question, Quiz

DIFFICULTY_ORDER = Case(
    When(difficulty='easy', then=Value(0)),
    When(difficulty='medium', then=Value(1)),
    When(difficulty='hard', then=Value(2)),
    default=Value(3),
    output_field=IntegerField(),
)

FEATURED_SLUGS = ['programming', 'computer-science', 'general-knowledge', 'mathematics', 'ai']
PER_PAGE = 12


def _category_dict(category):
    return {
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'emoji': category.emoji,
        'description': category.description,
        'gradient_from': category.gradient_from,
        'gradient_to': category.gradient_to,
        'quiz_count': category.quizzes.filter(is_published=True).count(),
    }


def _quiz_dict(quiz):
    return {
        'id': quiz.id,
        'title': quiz.title,
        'slug': quiz.slug,
        'description': quiz.description,
        'difficulty': quiz.difficulty,
        'duration_minutes': quiz.duration_minutes,
        'pass_percent': quiz.pass_percent,
        'attempts': quiz.attempts,
        'questions_count': quiz.questions_count,
        'category': {
            'name': quiz.category.name,
            'emoji': quiz.category.emoji,
            'gradient_from': quiz.category.gradient_from,
            'gradient_to': quiz.category.gradient_to,
        },
        'created_at': quiz.created_at.isoformat(),
    }


@require_GET
def categories(request):
    data = [_category_dict(c) for c in Category.objects.all()]
    return JsonResponse({'categories': data})


@require_GET
def quizzes(request):
    qs = (Quiz.objects.filter(is_published=True)
          .select_related('category')
          .annotate(diff_order=DIFFICULTY_ORDER)
          .order_by('category__name', 'diff_order', 'title'))
    slug = request.GET.get('category')
    if slug and slug != 'all':
        qs = qs.filter(category__slug=slug)
    q = request.GET.get('q')
    if q:
        qs = qs.filter(title__icontains=q)
    data = [_quiz_dict(qz) for qz in qs]
    return JsonResponse({'quizzes': data})


@require_GET
def home(request):
    trending = (Quiz.objects.filter(is_published=True)
                .select_related('category')
                .order_by('-attempts', '-created_at')[:5])
    featured = []
    for slug in FEATURED_SLUGS:
        category = Category.objects.filter(slug=slug).first()
        if not category:
            continue
        quizzes = (category.quizzes.filter(is_published=True)
                   .select_related('category')
                   .annotate(diff_order=DIFFICULTY_ORDER)
                   .order_by('diff_order', 'title')[:4])
        featured.append({
            'name': category.name,
            'slug': category.slug,
            'emoji': category.emoji,
            'gradient_from': category.gradient_from,
            'gradient_to': category.gradient_to,
            'description': category.description,
            'quizzes': [_quiz_dict(q) for q in quizzes],
        })
    return JsonResponse({
        'trending': [_quiz_dict(q) for q in trending],
        'featured_categories': featured,
    })


@require_GET
def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    quizzes = (category.quizzes.filter(is_published=True)
               .select_related('category')
               .annotate(diff_order=DIFFICULTY_ORDER)
               .order_by('diff_order', 'title'))
    paginator = Paginator(quizzes, PER_PAGE)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    all_categories = [
        (c, c.quizzes.filter(is_published=True).count())
        for c in Category.objects.all()
    ]
    total_quizzes = sum(count for _, count in all_categories)
    return render(request, 'category.html', {
        'category': category,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'all_categories': all_categories,
        'total_quizzes': total_quizzes,
    })


@require_GET
def quiz_detail(request, quiz_id):
    try:
        quiz = Quiz.objects.select_related('category').prefetch_related(
            'questions__choices'
        ).get(pk=quiz_id, is_published=True)
    except Quiz.DoesNotExist:
        return JsonResponse({'error': 'Quiz not found'}, status=404)

    data = _quiz_dict(quiz)
    data['questions'] = [
        {
            'id': q.id,
            'text': q.text,
            'order': q.order,
            'choices': [
                {'id': c.id, 'text': c.text, 'order': c.order}
                for c in q.choices.all()
            ],
        }
        for q in quiz.questions.all()
    ]
    return JsonResponse(data)


@require_POST
@csrf_exempt
def submit_quiz(request, quiz_id):
    try:
        quiz = Quiz.objects.get(pk=quiz_id, is_published=True)
    except Quiz.DoesNotExist:
        return JsonResponse({'error': 'Quiz not found'}, status=404)

    try:
        payload = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    answers = payload.get('answers', [])
    if not isinstance(answers, list):
        return JsonResponse({'error': 'answers must be a list'}, status=400)

    answer_map = {a.get('question_id'): a.get('choice_id') for a in answers}

    questions = list(quiz.questions.prefetch_related('choices').all())
    correct_count = 0
    results = []

    for q in questions:
        choices = list(q.choices.all())
        chosen_id = answer_map.get(q.id)
        correct_choice = next((c for c in choices if c.is_correct), None)
        is_correct = bool(correct_choice and chosen_id == correct_choice.id)
        if is_correct:
            correct_count += 1
        results.append({
            'question_id': q.id,
            'question_text': q.text,
            'chosen_id': chosen_id,
            'correct_id': correct_choice.id if correct_choice else None,
            'is_correct': is_correct,
            'choices': [
                {'id': c.id, 'text': c.text, 'is_correct': c.is_correct}
                for c in choices
            ],
        })

    total = len(questions)
    score = round((correct_count / total) * 100) if total else 0

    Quiz.objects.filter(pk=quiz.pk).update(attempts=F('attempts') + 1)

    return JsonResponse({
        'quiz_id': quiz.id,
        'quiz_title': quiz.title,
        'score': score,
        'correct_count': correct_count,
        'total': total,
        'answered': len(answers),
        'results': results,
    })
