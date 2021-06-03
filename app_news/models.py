from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

from app_news.permissions import PUBLISH_NEWS_PERM_CODE_NAME


class News(models.Model):
    """
    Модель Новостных сводок.
    """
    author = models.ForeignKey(User,
                               on_delete=models.SET_NULL,
                               verbose_name='Пользователь',
                               related_name='news',
                               null=True, )
    title = models.CharField('Название', max_length=100, db_index=True)
    content = models.TextField('Содержание')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    published_at = models.DateTimeField('Дата публикации', null=True, blank=True)
    edited_at = models.DateTimeField('Дата редактирования', auto_now=True)
    is_published = models.BooleanField('Статус публикации', db_index=True, default=False)
    slug = models.SlugField('slug-url')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']
        permissions = (
            (PUBLISH_NEWS_PERM_CODE_NAME, "Может публиковать новости"),
        )

    def get_absolute_url(self):
        return reverse('app_news:news_detail', kwargs={'pk': str(self.id), 'slug': self.slug})

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Модель комментариев к новостным сводкам
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='comments',
                             blank=True,
                             null=True, )

    user_name = models.CharField('Имя пользователя',
                                 max_length=100,
                                 db_index=True,
                                 blank=True,
                                 null=True, )
    text = models.TextField('Комментарий')
    news = models.ForeignKey('News',
                             on_delete=models.CASCADE,
                             verbose_name='Новость',
                             related_name='comments', )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    @property
    def get_related_username(self):
        """
        Получение имени пользователя из таблицы User, если такой существует.
        """
        try:
            username = User.objects.get(id=self.user_id).username
        except ObjectDoesNotExist:
            username = None

        return username

    def __str__(self):
        return self.get_related_username or f'{self.user_name} (аноним)'
