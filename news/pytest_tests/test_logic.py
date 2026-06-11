import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


pytestmark = pytest.mark.django_db


TEXT_COMMENT = {'text': 'Текст комментария'}
NEW_TEXT_COMMENT = {'text': 'Новый текст комментария'}


def test_anonymous_user_cant_create_comment(client, news_url):
    """
    Тестирование возможности отправить комментарий анонимным
    пользователем.
    """
    client.post(news_url, data=TEXT_COMMENT)
    comments_count = Comment.objects.count()
    assert comments_count == 0, (
        f'Вернулось некорректное количество комментариев: {comments_count}, '
        'а ожидалось 0'
    )


def test_user_can_create_comment(client, not_author, news_url):
    """
    Тестирование возможности отправить комментарий авторизированным
    пользователем.
    """
    client.force_login(not_author)
    response = client.post(news_url, data=TEXT_COMMENT)
    assertRedirects(
        response,
        f'{news_url}#comments',
        msg_prefix=(
            f'Вернулся некорректный статус кода: {response.status_code}, '
            f'а ожидалось {HTTPStatus.FOUND}'
        )
    )
    comments_count = Comment.objects.count()
    assert comments_count == 1, (
        f'Вернулось некорректное количество комментариев: {comments_count}, '
        'а ожидалось 1'
    )
    comment = Comment.objects.get()
    news = News.objects.get()
    assert comment.text == TEXT_COMMENT['text'], (
        f'Вернулся некорректный текст комментария: {comment.text}, '
        f'а ожидался {TEXT_COMMENT['text']}'
    )
    assert comment.author == not_author, (
        f'Вернулся некорректный автор комментария: {comment.author}, '
        f'а ожидался {not_author}'
    )
    assert comment.news == news, (
        f'Вернулась некорректная новость для комментария: {comment.news}, '
        f'а ожидалась {news}'
    )


@pytest.mark.parametrize('bad_words', BAD_WORDS)
def test_user_cant_use_bad_words(not_author_client, news_url, bad_words):
    """
    Тестирование возможности отправить комментарий с использованием
    запрещенного слова.
    """
    bad_words_data = {'text': f'Какой-то текст {bad_words}, еще текст'}
    response = not_author_client.post(news_url, data=bad_words_data)
    form = response.context['form']
    assertFormError(form=form, field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0, (
        f'Вернулось некорректное количество комментариев: {comments_count}, '
        'а ожидалось 0'
    )


def test_author_can_delete_comment(author_client, id_for_comment):
    """Тестирование возможности удаления комментария автором комментария."""
    url = reverse('news:delete', args=id_for_comment)
    response = author_client.delete(url)
    assert response.status_code == HTTPStatus.FOUND, (
        f'Вернулся некорректный статус кода: {response.status_code}, '
        f'а ожидалось {HTTPStatus.FOUND}'
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0, (
        f'Вернулось некорректное количество комментариев: {comments_count}, '
        'а ожидалось 0'
    )


def test_user_cant_delete_comment_of_another_user(
    not_author_client, id_for_comment
):
    """Тестирование возможности удаления комментария не автором комментария."""
    url = reverse('news:delete', args=id_for_comment)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'Вернулся некорректный статус кода: {response.status_code}, '
        f'а ожидалось {HTTPStatus.NOT_FOUND}'
    )
    comments_count = Comment.objects.count()
    assert comments_count == 1, (
        f'Вернулось некорректное количество комментариев: {comments_count}, '
        'а ожидалось 1'
    )


def test_author_can_edit_comment(author_client, comment, news_url):
    """Тестирование возможности удаления комментария автором комментария."""
    edit_url = reverse('news:edit', args=(comment.id,))
    url_to_comments = news_url + '#comments'
    response = author_client.post(edit_url, data=NEW_TEXT_COMMENT)
    assertRedirects(
        response,
        url_to_comments,
        msg_prefix=(
            f'Вернулся некорректный статус кода: {response.status_code}, '
            f'а ожидалось {HTTPStatus.FOUND}'
        )
    )
    comment.refresh_from_db()
    assert comment.text == NEW_TEXT_COMMENT['text'], (
        f'Вернулся некорректный текст комментария: {comment.text}, '
        f'а ожидался {TEXT_COMMENT['text']}'
    )


def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    """
    Тестирование возможности редактирования комментария не автором
    комментария.
    """
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, data=NEW_TEXT_COMMENT)
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        f'Вернулся некорректный статус кода: {response.status_code}, '
        f'а ожидалось {HTTPStatus.NOT_FOUND}'
    )
    comment.refresh_from_db()
    assert comment.text == TEXT_COMMENT['text'], (
        f'Вернулся некорректный текст комментария: {comment.text}, '
        f'а ожидался {TEXT_COMMENT['text']}'
    )
