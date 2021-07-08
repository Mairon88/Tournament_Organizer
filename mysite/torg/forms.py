from django import forms
from django.contrib.auth.models import User
from .models import Profile, Tournament, PlayerTeam, Match




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
        fields = ('description',)

        labels = {'description': 'Opis',}


class TournamentRegistrationForm(forms.ModelForm):
    NUMBER_CHOICES = ((2, 2), (4, 4), (8, 8), (16, 16), (32, 32))
    author = forms.CharField(widget=forms.HiddenInput(), initial=1)

    # widgets = {
    #     'name': forms.CharField(attrs={'class': 'input'}),
    #     'num_of_players': forms.IntegerField(attrs={'class': 'input'}),
    #     'description': forms.TextField(attrs={'class': 'input'}),
    #     'logo': forms.ImageField(attrs={'class': 'input'})
    #
    # }

    class Meta:
        model = Tournament
        fields = ('author', 'name','num_of_players', 'description', 'slug')
        exclude = ['author','slug']

        labels = {
                    'description': 'Opis turnieju',
                   'num_of_players': 'Liczba graczy'}

    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input'}),label='Nazwa turnieju')
    num_of_players = forms.ChoiceField(choices=Tournament.NUMBER_CHOICES, widget=forms.RadioSelect(attrs={'class': 'radio'}), label='Liczba graczy')
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'input'}), label='Opis turnieju')



class AddPlayerTeamForm(forms.ModelForm):

    tournament = forms.CharField(widget=forms.HiddenInput(), initial=1)
    class Meta:
        model = PlayerTeam
        fields = ('tournament', 'name')
        exclude = ['tournament',]

        labels = { 'name':'Nick gracza / Nazwa drużyny',}



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

        labels = {'description': 'Relacja z meczu',
                  }
