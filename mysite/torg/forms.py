from django import forms
from django.contrib.auth.models import User
from .models import Profile, Tournament


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

        def clean_password2(self):
            cd = self.cleaned_data
            if cd['password'] != cd['password2']:
                raise forms.ValidationError('Hasła nie są identyczne')
            return cd['password2']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'email')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('description','photo')


        labels = {'description': 'Opis',
                  'photo': 'Zdjęcie'}

class TournamentRegistrationForm(forms.ModelForm):
    author = forms.CharField(widget=forms.HiddenInput(), initial=123)
    class Meta:
        model = Tournament
        fields = ('author', 'name', 'description', 'slug', 'logo')
        exclude = ['author','slug']

        labels = { 'name':'Nazwa turnieju',
                    'description': 'Opis turnieju',
                   'logo': 'Logo turnieju'}


