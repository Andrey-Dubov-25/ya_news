import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('eleven_news')
def test_news_count(client, home_url):
    """Тестирование вывода количества новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE, (
        f'Вернулось некорректное количество новостей: {news_count}, '
        f'а ожидалось {settings.NEWS_COUNT_ON_HOME_PAGE}'
    )


@pytest.mark.usefixtures('eleven_news')
def test_news_order(client, home_url):
    """
    Тестирование сортировки новостей от самой свежей к самой старой. Свежие
    новости в начале списка.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates, (
        f'Вернулся некорректный список дат новостей: {all_dates}, '
        f'а ожидался {sorted_dates}'
    )


def test_comments_order(client, news_with_ten_comment):
    """
    Тестирование сортировки комментариев на странице отдельной новости от
    старых к новым: старые в начале списка, новые — в конце.
    """
    url = reverse('news:detail', args=(news_with_ten_comment.id,))
    response = client.get(url)
    assert 'news' in response.context, (
        f'news отсутствует в {response.context}'
    )
    all_comments = news_with_ten_comment.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps, (
        f'Вернулся некорректный список дат комментариев: {all_timestamps}, '
        f'а ожидался {sorted_timestamps}'
    )


def test_anonymous_client_has_no_form(client, news_url):
    """
    Тестирование отображения формы для отправки комментария на странице
    отдельной новости для анонимного пользователя.
    """
    response = client.get(news_url)
    assert 'form' not in response.context, (
        f'form не должна быть в {response.context}'
    )


def test_authorized_client_has_form(not_author_client, news_url):
    """
    Тестирование отображения формы для отправки комментария на странице
    отдельной новости для авторизированного пользователя.
    """
    response = not_author_client.get(news_url)
    assert 'form' in response.context, (
        f'form отсутствует в {response.context}'
    )
    assert isinstance(response.context['form'], CommentForm), (
        f'form не соответствует {CommentForm}'
    )
