from django import forms
from django.forms import modelformset_factory

from app_news import models
from project_modules.forms import ChangeIsValidFormMixin


class NewsForm(forms.ModelForm, ChangeIsValidFormMixin):
    """
    Форма для создания новостной сводки.
    """
    class Meta:
        model = models.News
        exclude = ['author', 'is_published', 'slug', 'published_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-field',
                'aria-label': 'Введите название новости',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-field form-field_content',
                'aria-label': 'Введите комментарий',
            }),
        }


class NewsModerateForm(forms.ModelForm, ChangeIsValidFormMixin):
    """
    Форма для модерации новостной сводки, управление статусом is_published модели News.
    """

    class Meta:
        model = models.News
        fields = ['is_published']
        widgets = {
            'is_published': forms.CheckboxInput(attrs={
                'class': 'news-verified-status',
                'aria-label': 'Поменять статус публикации',
                'title': 'Поменять статус публикации',
            }),
        }


class CommentForm(forms.ModelForm, ChangeIsValidFormMixin):
    """
    Форма для создания комментария к новостной сводке.
    """

    def __init__(self, user, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = models.Comment
        exclude = ['user', 'news']
        widgets = {
            'user_name': forms.TextInput(attrs={
                'required': '',
                'class': 'form-field',
                'placeholder': 'Введите свое имя',
                'aria-label': 'Введите свое имя',
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-field form-field_content',
                'placeholder': 'Введите комментарий',
                'aria-label': 'Введите комментарий',
            }),
        }

    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        user_name = cleaned_data['user_name']

        if not self.user.is_authenticated and not user_name:
            self.add_error('user_name', 'Необходимо ввести имя пользователя')

        return cleaned_data


NewsModerateFormSet = modelformset_factory(models.News, form=NewsModerateForm)
