import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:signup')
)
def test_home_availability_for_anonymous_user(client, name):
    """
    Проверка доступнисти главной страницы, страниц регистрации, входа и
    отдельной новости для анонимного пользователя.
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, (
        f'Вернулся некорректный статус кода: {response.status_code}, '
        f'а ожидалось {HTTPStatus.OK}'
    )


def test_home_availability_for_anonymous_user(client, news_url):
    """
    Проверка доступнисти главной страницы, страниц регистрации, входа и
    отдельной новости для анонимного пользователя.
    """
    response = client.get(news_url)
    assert response.status_code == HTTPStatus.OK, (
        f'Вернулся некорректный статус кода: {response.status_code}, '
        f'а ожидалось {HTTPStatus.OK}'
    )


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_aviability_for_comment_edit_and_delete(
    comment, name, author_client, not_author_client
):
    """
    Тестирование доступности редактирования и удаления комментария
    авторизированным автором комментария и обычным пользователем.
    """
    url = reverse(name, args=(comment.id,))
    for user in (author_client, not_author_client):
        if user == author_client:
            response = author_client.get(url)
            assert response.status_code == HTTPStatus.OK, (
                f'Вернулся некорректный статус кода: {response.status_code}, '
                f'а ожидалось {HTTPStatus.OK}'
            )
        else:
            response = not_author_client.get(url)
            assert response.status_code == HTTPStatus.NOT_FOUND, (
                f'Вернулся некорректный статус кода: {response.status_code}, '
                f'а ожидалось {HTTPStatus.NOT_FOUND}'
            )


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete')
)
def test_redirect_for_anonymous_client(comment, client, name, login_url):
    """
    Тестирование редиректа для неавторизированного пользователя при попытке
    удаления или рекдактирования комментария.
    """
    url = reverse(name, args=(comment.id,))
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
    assert response.status_code == HTTPStatus.FOUND, (
        f'Вернулся некорректный статус кода: {response.status_code}, '
        f'а ожидалось {HTTPStatus.FOUND}'
    )
