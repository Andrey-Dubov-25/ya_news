import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Фикстура неавторизированного автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура неавторизированного не автора."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура авторизированного автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура авторизированного не автора."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура одной новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def news_with_ten_comment(author):
    """Фикстура одной новости с наличием 10 комментариев к ней."""
    now = timezone.now()
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return news


@pytest.fixture
def comment(author, news):
    """Фикстура одного комментария."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def id_for_comment(comment):
    """Фикстура получения id для комментария."""
    return (comment.id,)


@pytest.fixture
def eleven_news():
    """Фикстура с наличием 11 новостей."""
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Заголовок {index}',
            text='Просто текст',
            date=today - timedelta(days=index))
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def news_url(news):
    """Фикстура получения URL страницы отдельной новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def home_url():
    """Фикстура получения URL страницы главной странице сайта."""
    return reverse('news:home')


@pytest.fixture
def login_url():
    """Фикстура получения URL страницы входа."""
    return reverse('users:login')
