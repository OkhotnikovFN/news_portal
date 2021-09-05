from django.contrib.auth.models import User
from django.db import models

from app_users.permissions import VERIFY_USER_PERM_CODE_NAME


class UserProfile(models.Model):
    """
    Профиль пользователя, дополняет модель User.
    """
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile',
                                verbose_name='Пользователь',)
    telephone = models.CharField('Телефонный номер',
                                 max_length=20,
                                 unique=True,)
    city = models.CharField('Город проживания',
                            max_length=40,
                            null=True,
                            blank=True,)
    is_verified = models.BooleanField('Флаг верификации', default=False)
    number_of_published_news = models.PositiveIntegerField('Количество опубликованных новостей',
                                                           default=0,)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        permissions = (
            (VERIFY_USER_PERM_CODE_NAME, "Может верифицировать пользователя"),
        )

    @property
    def get_related_username(self):
        """
        Получение имени пользователя связной модели User.
        """
        return User.objects.get(id=self.user_id).username

    def __str__(self):
        return self.get_related_username
