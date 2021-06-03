import datetime

from django.db.models import QuerySet
from django.http import HttpRequest

from app_news.forms import CommentForm, NewsForm
from app_news.models import News


def filter_news_queryset_by_title(queryset: QuerySet, request: HttpRequest) -> QuerySet:
    """
    Регистронезависимя фильтрация запорса новостей по полю title.
    """
    news_title = request.GET.get('news_title')

    if news_title:
        queryset = queryset.filter(title__icontains=news_title)

    return queryset


def filter_news_queryset_by_author(queryset: QuerySet, request: HttpRequest) -> QuerySet:
    """
    Регистронезависимя фильтрация запорса новостей по полю author.
    """
    news_author = request.GET.get('news_author')

    if news_author:
        queryset = queryset.filter(author__username__icontains=news_author)

    return queryset


def filter_news_queryset_by_date(queryset: QuerySet, request: HttpRequest) -> QuerySet:
    """
    Фильтрация запорса новостей по дате создания.
    """
    news_date_begin = request.GET.get('news_date_begin')
    news_date_end = request.GET.get('news_date_end')

    if news_date_begin:
        news_date_begin = datetime.datetime.strptime(news_date_begin, '%Y-%m-%d')
        queryset = queryset.filter(created_at__gte=news_date_begin)
    if news_date_end:
        news_date_end = datetime.datetime.strptime(news_date_end, '%Y-%m-%d')
        news_date_end += datetime.timedelta(hours=23, minutes=59, seconds=59)
        queryset = queryset.filter(created_at__lte=news_date_end)

    return queryset


def filter_news_queryset_by_activity(queryset: QuerySet, request: HttpRequest) -> QuerySet:
    """
    Фильтрация запорса новостей по статусу активности новости.
    """
    displayed_news = request.GET.get('displayed_news')

    if displayed_news == 'active':
        queryset = queryset.filter(is_published=True)
    elif displayed_news == 'not_active':
        queryset = queryset.filter(is_published=False)

    return queryset


def create_comment(form: CommentForm, request: HttpRequest, news: News, ):
    """
    Создание нового комметария к новости.
    """
    new_comment = form.save(commit=False)
    new_comment.news = news
    active_user = request.user

    if active_user.is_authenticated:
        new_comment.user = active_user
        new_comment.user_name = active_user.username

    new_comment.save()


def create_news(form: NewsForm, request: HttpRequest) -> News:
    """
    Создание новостной сводки.
    """
    news = form.save(commit=False)
    news.author = request.user
    news.save()

    return news


def update_news(form: NewsForm) -> News:
    """
    Редактирование новостной сводки. Если данные меняются, новость становится неактивной.
    """
    news = form.save(commit=False)
    if form.has_changed():
        news.is_published = False
    news.save()

    return news
