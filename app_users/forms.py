import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import password_validators_help_texts
from django.forms import modelformset_factory

from project_modules.forms import ChangeIsValidFormMixin
from app_users import models


LOGIN_REGISTER_UPDATE_FIELD_CLASS = 'login-register-update-field'


class CleanedUserProfileTelephoneMixin:
    """
    Миксин для проверки поля telephone модели UserProfile.
    """

    def clean_telephone(self):
        telephone = self.cleaned_data['telephone']
        telephone_digits = re.sub(r'\D', '', telephone)

        if telephone.startswith('8'):
            telephone = f'+7{telephone_digits[1:]}'
        else:
            telephone = f'+{telephone_digits}'

        user_with_telephone = models.UserProfile.objects.filter(telephone=telephone)

        if user_with_telephone.exists():
            if user_with_telephone.filter(pk=self.instance.id).exists():
                error_message = 'Это ваш номер телефона, пожалуйста введите другой'
            else:
                error_message = 'Пользователь с таким номером уже существует'
            self.add_error('telephone', error_message)

        return telephone


class CleanedUserEmailMixin:
    """
    Миксин для проверки поля email модели User.
    """

    def clean_email(self):
        email = self.cleaned_data['email']
        users_with_email = User.objects.filter(email=email)

        if not email:
            self.add_error('email', 'Необходимо ввести адрес электронной почты')
        elif users_with_email.exists():
            if users_with_email.filter(pk=self.instance.id).exists():
                error_message = 'Это ваш Email, пожалуйста введите другой'
            else:
                error_message = 'Пользователь с таким E-mail уже существует'
            self.add_error('email', error_message)

        return email


class AuthForm(AuthenticationForm, ChangeIsValidFormMixin):
    """
    Форма аутентификации пользователя.
    """
    username = UsernameField(
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'placeholder': 'Введите логин',
            'class': LOGIN_REGISTER_UPDATE_FIELD_CLASS,
        }),
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'placeholder': 'Введите пароль',
            'class': LOGIN_REGISTER_UPDATE_FIELD_CLASS,
        }),
    )


class UserChangePasswordForm(PasswordChangeForm, ChangeIsValidFormMixin):
    """
    Форма смены пароля пользователя.
    """
    prefix = 'change_password_form'

    def __init__(self, *args, **kwargs):
        super(UserChangePasswordForm, self).__init__(*args, **kwargs)

        self.fields['old_password'].help_text = 'Введите ваш старый пароль'
        self.fields['new_password1'].help_text = ''.join(password_validators_help_texts())
        self.fields['new_password2'].help_text = 'Повторите пароль'

        for field in self.fields.values():
            field.widget.attrs.update({'class': LOGIN_REGISTER_UPDATE_FIELD_CLASS,
                                       'title': field.help_text, })

        self.fields['old_password'].widget.attrs.update({'placeholder': 'Введите старый пароль',
                                                         'aria-label': 'Введите старый пароль', })
        self.fields['new_password1'].widget.attrs.update({'placeholder': 'Введите новый пароль',
                                                          'aria-label': 'Введите новый пароль', })
        self.fields['new_password2'].widget.attrs.update({'placeholder': 'Повторите пароль',
                                                          'aria-label': 'Повторите пароль', })


class RegisterForm(UserCreationForm, ChangeIsValidFormMixin, CleanedUserProfileTelephoneMixin, CleanedUserEmailMixin):
    """
    Форма регистрации пользователя.
    """
    telephone = forms.CharField(max_length=20,
                                required=True,
                                help_text='Введите ваш номер телефона', )

    telephone.widget.attrs.update({'placeholder': 'Номер телефона',
                                   'type': 'tel',
                                   'aria-label': 'Введите ваш номер телефона',
                                   'data-tel-input': '', })

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['email'].help_text = 'Адрес электронной почты должен содержать "@"'
        self.fields['password1'].help_text = ''.join(password_validators_help_texts())

        for field in self.fields.values():
            field.widget.attrs.update({'class': LOGIN_REGISTER_UPDATE_FIELD_CLASS,
                                       'title': f'{field.help_text}', })

        self.fields['username'].widget.attrs.update({'placeholder': 'Логин',
                                                     'aria-label': 'Введите ваш логин', })
        self.fields['email'].widget.attrs.update({'placeholder': 'E-mail',
                                                  'aria-label': 'Введите ваш e-mail', })
        self.fields['password1'].widget.attrs.update({'placeholder': 'Введите пароль',
                                                      'aria-label': 'Введите пароль', })
        self.fields['password2'].widget.attrs.update({'placeholder': 'Повторите пароль',
                                                      'aria-label': 'Повторите пароль', })

    class Meta:
        model = User
        fields = ('username', 'email', 'telephone', 'password1', 'password2',)


class UserProfileTelephoneForm(forms.ModelForm, ChangeIsValidFormMixin, CleanedUserProfileTelephoneMixin):
    """
    Форма смены телефона пользователя
    """
    prefix = 'telephone_form'

    def __init__(self, *args, **kwargs):
        super(UserProfileTelephoneForm, self).__init__(*args, **kwargs)

        self.fields['telephone'].widget.attrs.update({'placeholder': 'Введите новый номер телефона',
                                                      'type': 'tel',
                                                      'aria-label': 'Введите ваш номер телефона',
                                                      'title': 'Введите ваш номер телефона',
                                                      'data-tel-input': '',
                                                      'class': LOGIN_REGISTER_UPDATE_FIELD_CLASS, })

    class Meta:
        model = models.UserProfile
        fields = ('telephone',)


class UserProfileCityForm(forms.ModelForm, ChangeIsValidFormMixin):
    """
    Форма смены города пользователя
    """
    prefix = 'city_form'

    def __init__(self, *args, **kwargs):
        super(UserProfileCityForm, self).__init__(*args, **kwargs)

        self.fields['city'].widget.attrs.update({'placeholder': 'Введите новый город',
                                                 'aria-label': 'Введите новый город',
                                                 'title': 'Введите новый город',
                                                 'required': True,
                                                 'class': LOGIN_REGISTER_UPDATE_FIELD_CLASS, })

    def clean_city(self):
        city = self.cleaned_data['city']

        if not city:
            self.add_error('city', 'Введите пожалуйста название города')

        return city

    class Meta:
        model = models.UserProfile
        fields = ('city',)


class UserUsernameForm(forms.ModelForm, ChangeIsValidFormMixin):
    """
    Форма смены имени пользователя
    """
    prefix = 'username_form'

    def __init__(self, *args, **kwargs):
        super(UserUsernameForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({'placeholder': 'Введите новый логин',
                                                     'aria-label': 'Введите новый логин',
                                                     'title': 'Введите новый логин',
                                                     'required': True,
                                                     'class': LOGIN_REGISTER_UPDATE_FIELD_CLASS, })

    class Meta:
        model = User
        fields = ('username',)


class UserEmailForm(forms.ModelForm, ChangeIsValidFormMixin, CleanedUserEmailMixin):
    """
    Форма смены e-mail пользователя
    """
    prefix = 'email_form'

    def __init__(self, *args, **kwargs):
        super(UserEmailForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({'placeholder': 'Введите новый email',
                                                  'aria-label': 'Введите новый email',
                                                  'title': 'Введите новый email',
                                                  'required': True,
                                                  'class': LOGIN_REGISTER_UPDATE_FIELD_CLASS, })

    class Meta:
        model = User
        fields = ('email',)


class UserProfileVerificationForm(forms.ModelForm, ChangeIsValidFormMixin):
    """
    Форма верификации пользователя
    """

    class Meta:
        model = models.UserProfile
        fields = ('is_verified',)
        widgets = {
            'is_verified': forms.CheckboxInput(attrs={
                'class': 'user-verified-status',
                'aria-label': 'Поменять статус верификации',
                'title': 'Поменять статус верификации',
            }),
        }


UserProfileModerateFormSet = modelformset_factory(models.UserProfile, form=UserProfileVerificationForm)
