from django import forms
from django.contrib.auth.models import User
from .models import Profile, Tournament, PlayerTeam, Match


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

    author = forms.CharField(widget=forms.HiddenInput(), initial=1)

    class Meta:
        model = Tournament
        fields = ('author', 'name', 'tournament_type','num_of_players', 'description', 'slug', 'logo')
        exclude = ['author','slug']

        labels = { 'name':'Nazwa turnieju',
                    'description': 'Opis turnieju',
                   'logo': 'Logo turnieju',
                   'tournament_type': 'Typ turnieju',
                   'num_of_players': 'Liczba graczy'}

class AddPlayerTeamForm(forms.ModelForm):

    tournament = forms.CharField(widget=forms.HiddenInput(), initial=1)
    class Meta:
        model = PlayerTeam
        fields = ('tournament', 'name', 'photo')
        exclude = ['tournament', 'photo']

        labels = { 'name':'Nick gracza / Nazwa drużyny',
                   'photo': 'Zdjęcie'}


class MatchForm(forms.ModelForm):

    class Meta:
        model = Match
        fields = ('player_team_1', 'player_team_2')

        labels = { 'player_team_1':'Gracz/Drużyna 1',
                   'player_team_2': 'Gracz/Drużyna 2'}


class ScoreForm(forms.ModelForm):

    class Meta:
        model = Match
        fields = ('score_1', 'score_2')

        labels = {'score_1': 'Punkty Gracza/Drużyny nr 1',
                  'score_2': 'Punkty Gracza/Drużyny nr 2'
                  }


class YTForm(forms.ModelForm):

    class Meta:
        model = Match
        fields = ('youtube',)

        labels = {'youtube': 'Link do rozgrywki z YouTube',
                  }

class DescriptionForm(forms.ModelForm):

    class Meta:
        model = Match
        fields = ('description',)

        labels = {'description': 'Opis meczu',
                  }
