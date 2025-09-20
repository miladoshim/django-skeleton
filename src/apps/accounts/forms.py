# from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from typing import Any
from django import forms
from django.forms import Form, ModelForm
from django.forms.widgets import PasswordInput
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget

# class CustomUserCreationForm(UserCreationForm):
#     class Meta: 
#         model = User
#         fields = UserCreationForm.Meta.fields + ('mobile',)
        

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder' : 'نام کاربری'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder' : 'ایمیل'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' : 'رمز عبور'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']


class UserLoginForm(Form):
    username = forms.TextInput()
    password = forms.TextInput()


class ChangePasswordForm(Form):
    old_password = forms.PasswordInput()
    password = forms.PasswordInput()
    password_confirmation = forms.PasswordInput()

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 8:
            raise forms.ValidationError(
                'رمز عبور باید بیشتر از 8 کاراکتر باشد')
        else:
            return password

    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data['password_confirmation']

        if password != password_confirmation:
            raise forms.ValidationError('رمز عبور ها یکی نیستند')
        return password_confirmation


class AccountSettingForm(ModelForm):
    class Meta:
        model = User
        fields = []

    def __init__(self, *args, **kwargs):
        super(AccountSettingForm, self).__init__(*args, **kwargs)
        self.fields['birthday'] = JalaliDateField(
            label=_('تاریخ تولد'), widget=AdminJalaliDateWidget)

    def save(self, commit):
        account = super(AccountSettingForm, self).save(commit=False)
