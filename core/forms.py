from django.forms import ModelForm
from .models import Room
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ["host", "participants"]


class UserForm(ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'image']

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user